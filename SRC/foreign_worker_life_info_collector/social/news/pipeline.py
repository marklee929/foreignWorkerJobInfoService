"""Automated social news publishing pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ...utils.date_utils import utc_now_iso
from .collector.google_news_collector import GoogleNewsCollector
from .collector.naver_news_collector import NaverNewsCollector
from .duplicate_guard.duplicate_detector import check_duplicate
from .duplicate_guard.llama_duplicate_checker import LlamaDuplicateChecker
from .evaluator.candidate_evaluator import CandidateEvaluator
from .models import CandidateEvaluation, DuplicateCheckResult, NewsCandidate, NewsItem
from .normalizer.news_normalizer import normalize_news_item
from .notifier.telegram_notifier import NewsTelegramNotifier
from .publisher.facebook_publisher import FacebookPublisher
from .repository.news_repository import NewsRepository
from .summarizer.news_summarizer import NewsSummarizer


class NewsPipeline:
    def __init__(
        self,
        repository: NewsRepository,
        collectors: list | None = None,
        summarizer: NewsSummarizer | None = None,
        evaluator: CandidateEvaluator | None = None,
        llama_duplicate_checker: LlamaDuplicateChecker | None = None,
        facebook_publisher: FacebookPublisher | None = None,
        telegram_notifier: NewsTelegramNotifier | None = None,
    ):
        self.repository = repository
        self.collectors = collectors or [NaverNewsCollector(), GoogleNewsCollector()]
        self.summarizer = summarizer or NewsSummarizer()
        self.evaluator = evaluator or CandidateEvaluator()
        self.llama_duplicate_checker = llama_duplicate_checker or LlamaDuplicateChecker()
        self.facebook_publisher = facebook_publisher or FacebookPublisher()
        self.telegram_notifier = telegram_notifier or NewsTelegramNotifier()

    def run(self, keyword: str = "외국인 취업 비자", dry_run: bool = True, limit: int = 5) -> dict:
        collected_items = self.collect(keyword)
        saved_candidates = [self.save_normalized(item, keyword) for item in collected_items]
        processed_candidates = [self.process_candidate(candidate) for candidate in saved_candidates]
        selected_candidates = self.auto_select(processed_candidates, limit=limit)
        ready_snapshot = [candidate.to_dict() for candidate in selected_candidates]
        publish_results = [self.auto_publish(candidate, dry_run=dry_run) for candidate in selected_candidates]
        final_candidates = self.repository.list_candidates()
        return {
            "dry_run": dry_run,
            "collected_count": len(collected_items),
            "saved_count": len(saved_candidates),
            "duplicate_count": sum(1 for candidate in final_candidates if candidate.status == "DUPLICATE"),
            "skipped_count": sum(1 for candidate in final_candidates if candidate.status == "SKIPPED"),
            "selected_count": len(selected_candidates),
            "saved": [candidate.to_dict() for candidate in final_candidates],
            "ready_to_publish": ready_snapshot,
            "publish_results": publish_results,
            "report": self.build_report(
                dry_run=dry_run,
                collected_count=len(collected_items),
                saved_count=len(saved_candidates),
                final_candidates=final_candidates,
                selected_candidates=selected_candidates,
                publish_results=publish_results,
            ),
        }

    def collect(self, keyword: str) -> list[NewsItem]:
        items: list[NewsItem] = []
        for collector in self.collectors:
            items.extend(collector.collect(keyword))
        return items or self._dry_run_seed_items(keyword)

    def save_normalized(self, item: NewsItem, keyword: str) -> NewsCandidate:
        candidate = normalize_news_item(NewsCandidate.from_item(item))
        candidate.keyword = keyword
        candidate.status = "NORMALIZED"
        return self.repository.save(candidate)

    def process_candidate(self, candidate: NewsCandidate) -> NewsCandidate:
        summary = self.summarizer.summarize(candidate)
        candidate.short_summary = summary.short_summary
        candidate.key_points = "\n".join(summary.key_points)
        candidate.relevance_reason = summary.relevance_reason
        candidate.risk_notes = summary.risk_notes
        candidate.status = "SUMMARIZED"
        candidate = self.repository.update_candidate(candidate)

        duplicate_result = self.check_duplicate(candidate)
        if duplicate_result.is_duplicate:
            candidate.status = "DUPLICATE"
            candidate.duplicate_group_id = duplicate_result.duplicate_group_id
            candidate.duplicate_risk_score = duplicate_result.duplicate_risk_score
            candidate.risk_notes = _append_note(candidate.risk_notes, f"Duplicate: {duplicate_result.reason}")
            return self.repository.update_candidate(candidate)

        evaluation = self.evaluator.evaluate(candidate)
        candidate.evaluation_score = evaluation.total_score
        candidate.duplicate_risk_score = evaluation.duplicate_risk_score
        candidate.foreign_worker_relevance_score = evaluation.foreign_worker_relevance_score
        candidate.korea_relevance_score = evaluation.korea_relevance_score
        candidate.visa_or_labor_policy_score = evaluation.visa_or_labor_policy_score
        candidate.freshness_score = evaluation.freshness_score
        candidate.source_reliability_score = evaluation.source_reliability_score
        candidate.facebook_post_suitability_score = evaluation.facebook_post_suitability_score
        candidate.status = evaluation.decision
        if evaluation.decision == "READY_TO_PUBLISH":
            candidate.selection_reason = evaluation.reason
        else:
            candidate.skip_reason = evaluation.reason
        candidate.risk_notes = _append_note(candidate.risk_notes, evaluation.reason)
        return self.repository.update_candidate(candidate)

    def check_duplicate(self, candidate: NewsCandidate) -> DuplicateCheckResult:
        existing = self.repository.list_candidates()
        deterministic = check_duplicate(candidate, existing)
        if deterministic.is_duplicate:
            return deterministic

        published = self.repository.list_recent_published(limit=20)
        llama_duplicate, confidence, reason = self.llama_duplicate_checker.check(candidate, published)
        if llama_duplicate and confidence >= 0.75:
            return DuplicateCheckResult(
                True,
                published[0].duplicate_group_id if published else candidate.duplicate_group_id,
                confidence,
                reason,
                "local_llama",
            )
        return deterministic

    def auto_select(self, candidates: list[NewsCandidate], limit: int = 5) -> list[NewsCandidate]:
        ready = [candidate for candidate in candidates if candidate.status == "READY_TO_PUBLISH"]
        ready.sort(key=lambda candidate: candidate.evaluation_score, reverse=True)
        selected = ready[:limit]
        selected_ids = {candidate.id for candidate in selected}
        for candidate in ready[limit:]:
            candidate.status = "SKIPPED"
            candidate.skip_reason = "Skipped because a higher-scoring Korea-specific candidate was selected."
            candidate.risk_notes = _append_note(candidate.risk_notes, candidate.skip_reason)
            self.repository.update_candidate(candidate)
        return [candidate for candidate in selected if candidate.id in selected_ids]

    def auto_publish(self, candidate: NewsCandidate, dry_run: bool = True) -> dict:
        timestamp = utc_now_iso()
        publish_result = self.facebook_publisher.publish(candidate, dry_run=dry_run)
        status = publish_result.get("status", "FAILED")
        facebook_post_id = publish_result.get("facebook_post_id", "")
        error_code = publish_result.get("error_code", "")
        error_message = publish_result.get("error_message", "")
        self.repository.insert_facebook_log(
            news_candidate_id=candidate.id,
            page_id=publish_result.get("page_id", ""),
            facebook_post_id=facebook_post_id,
            status=status,
            error_code=error_code,
            error_message=error_message,
            published_at=timestamp,
        )

        if status in ("DRY_RUN", "PUBLISHED"):
            published_status = "DRY_RUN_PUBLISHED" if dry_run else "PUBLISHED"
            self.repository.mark_status(candidate.id, published_status, published_at=timestamp)
            candidate.status = published_status
            candidate.published_at = timestamp
        else:
            self.repository.mark_status(candidate.id, "FAILED")
            candidate.status = "FAILED"

        notify_result = self.telegram_notifier.notify_publish_result(
            candidate,
            status=candidate.status,
            facebook_post_id=facebook_post_id,
            error_message=error_message,
            dry_run=dry_run,
        )
        self.repository.insert_telegram_log(
            news_candidate_id=candidate.id,
            message=notify_result["message"],
            status=notify_result["status"],
            error_message=notify_result.get("error_message", ""),
            sent_at=utc_now_iso(),
        )
        if notify_result["status"] in ("DRY_RUN", "NOTIFIED"):
            notified_status = "DRY_RUN_NOTIFIED" if dry_run else "NOTIFIED"
            self.repository.mark_status(candidate.id, notified_status)
            candidate.status = notified_status

        return {
            "news_candidate_id": candidate.id,
            "status": candidate.status,
            "facebook_status": status,
            "facebook_post_id": facebook_post_id,
            "telegram_status": notify_result["status"],
            "message": publish_result.get("message", ""),
            "error_message": error_message or notify_result.get("error_message", ""),
        }

    def build_report(
        self,
        dry_run: bool,
        collected_count: int,
        saved_count: int,
        final_candidates: list[NewsCandidate],
        selected_candidates: list[NewsCandidate],
        publish_results: list[dict],
    ) -> str:
        selected = selected_candidates[0] if selected_candidates else None
        publish = publish_results[0] if publish_results else {}
        lines = [
            f"[WorkConnect News Automation - {'DRY RUN' if dry_run else 'REAL RUN'}]",
            f"Collected: {collected_count}",
            f"Saved: {saved_count}",
            f"Duplicates: {sum(1 for item in final_candidates if item.status == 'DUPLICATE')}",
            f"Skipped: {sum(1 for item in final_candidates if item.status == 'SKIPPED')}",
            f"Selected: {len(selected_candidates)}",
            "",
            "Selected Candidate:",
        ]
        if selected:
            lines.extend(
                [
                    f"- Title: {selected.title}",
                    f"- Source: {selected.source_name or selected.source_type}",
                    f"- Keyword: {selected.keyword}",
                    f"- Score: {selected.evaluation_score:.2f}",
                    f"- Reason: {selected.selection_reason}",
                    f"- URL: {selected.source_url}",
                ]
            )
        else:
            lines.append("- None")
        lines.extend(
            [
                "",
                "Publish:",
                f"- Facebook: {publish.get('facebook_status', 'N/A')}",
                f"- Telegram: {publish.get('telegram_status', 'N/A')}",
                f"- DB status: {publish.get('status', 'N/A')}",
            ]
        )
        return "\n".join(lines)

    def _dry_run_seed_items(self, keyword: str) -> list[NewsItem]:
        return [
            NewsItem(
                title=f"{keyword} 지원 정책 안내",
                url="https://example.com/workconnect/news/support-policy",
                source="dry_run",
                summary="Dry-run sample news candidate for foreign workers in Korea.",
                category="foreign_worker_policy",
            ),
            NewsItem(
                title=f"{keyword} 지원 정책 안내",
                url="https://example.com/workconnect/news/support-policy",
                source="dry_run",
                summary="Duplicate dry-run sample news candidate.",
                category="foreign_worker_policy",
            ),
        ]


def _append_note(existing: str, note: str) -> str:
    return "\n".join(part for part in (existing, note) if part)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the automated social news publishing pipeline.")
    parser.add_argument("--db", required=True, help="SQLite database path.")
    parser.add_argument("--keyword", default="외국인 취업 비자", help="News search keyword.")
    parser.add_argument("--limit", type=int, default=1, help="Maximum candidates to publish in one cycle.")
    parser.add_argument("--dry-run", action="store_true", help="Run without external Facebook/Telegram calls.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")
    parser.add_argument("--verbose", action="store_true", help="Print full JSON output.")
    args = parser.parse_args(argv)

    pipeline = NewsPipeline(repository=NewsRepository(Path(args.db)))
    result = pipeline.run(keyword=args.keyword, dry_run=args.dry_run, limit=args.limit)
    if args.json or args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
