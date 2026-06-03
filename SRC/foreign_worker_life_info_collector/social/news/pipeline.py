"""Automated social news collection, scoring, publishing, and notification pipeline."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ...utils.date_utils import utc_now_iso
from .collector.google_news_collector import GoogleNewsCollector
from .collector.naver_news_collector import NaverNewsCollector
from .duplicate_guard.duplicate_detector import check_duplicate
from .duplicate_guard.llama_duplicate_checker import LlamaDuplicateChecker
from .evaluator.candidate_evaluator import CandidateEvaluator
from .models import DuplicateCheckResult, NewsCandidate, NewsItem
from .normalizer.news_normalizer import normalize_news_item
from .notifier.telegram_notifier import NewsTelegramNotifier
from .publisher.facebook_publisher import FacebookPublisher
from .repository.news_repository import NewsRepository
from .summarizer.news_summarizer import NewsSummarizer

KST = ZoneInfo("Asia/Seoul")
STOP_WORDS = {
    "about",
    "after",
    "from",
    "have",
    "into",
    "korea",
    "korean",
    "more",
    "news",
    "that",
    "their",
    "this",
    "with",
    "worker",
    "workers",
}


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

    def run(self, keyword: str = "foreign worker visa Korea", dry_run: bool = False, limit: int = 5) -> dict:
        cycle_id = today_cycle_id()
        self.ensure_publish_cycle_metadata()
        self.expire_old_unposted_candidates(cycle_id=cycle_id)

        self.repository.insert_pipeline_log("collect", "STARTED", "뉴스 수집 시작")
        collected_items = self.collect(keyword, allow_seed=dry_run)
        self.repository.insert_pipeline_log("collect", "COMPLETED", f"뉴스 수집 완료: {len(collected_items)}건")

        saved_candidates = [self.save_normalized(item, keyword) for item in collected_items]
        minimum_safe_score = self.minimum_publish_score()
        self.restore_today_safe_skipped_candidates(minimum_safe_score=minimum_safe_score)
        self.repository.insert_pipeline_log("score", "STARTED", f"신규 후보 {len(saved_candidates)}건 기준 최소 안전 점수 {minimum_safe_score:.0f}점")
        processed_candidates = [self.process_candidate(candidate, dry_run=dry_run, threshold=minimum_safe_score) for candidate in saved_candidates]

        cooldown = self.publish_cooldown_info()
        if not dry_run and cooldown["active"]:
            selection = self.cooldown_selection(cycle_id, cooldown)
        else:
            selection = self.evaluate_publish_candidates_v2(cycle_id=cycle_id, dry_run=dry_run)

        selected_candidates = [selection["selected_candidate"]] if selection.get("selected_candidate") else []
        ready_snapshot = [candidate.to_dict() for candidate in selected_candidates]
        publish_results: list[dict] = []
        publish_attempted = False
        publish_result_label = "SKIPPED"
        no_publish_reason = selection.get("no_publish_reason") or ""
        no_publish_code = selection.get("no_publish_code") or ""

        if no_publish_code == "WAITING_COOLDOWN":
            publish_result_label = "WAITING_COOLDOWN"
            self.repository.insert_pipeline_log(
                "facebook_publish",
                "WAITING",
                no_publish_reason,
                payload_json=json.dumps(self.selection_log_payload(selection), ensure_ascii=False),
            )
            notification = self.telegram_notifier.notify_cooldown(cooldown, dry_run=dry_run)
            self.repository.insert_telegram_log(
                message=notification.get("message", ""),
                status=notification.get("status", "FAILED"),
                sent_at=utc_now_iso(),
                error_message=notification.get("error_message", ""),
            )
            publish_results.append({"status": "WAITING_COOLDOWN", "facebook_status": "WAITING_COOLDOWN", "telegram_status": notification.get("status", "SKIPPED"), "error_message": no_publish_reason})
        elif not selected_candidates:
            skip_message = no_publish_reason or "게시 가능한 후보가 없습니다."
            self.repository.insert_pipeline_log(
                "facebook_publish",
                "SKIPPED",
                skip_message,
                payload_json=json.dumps(self.selection_log_payload(selection), ensure_ascii=False),
            )
            if os.getenv("NEWS_NOTIFY_NO_PUBLISH", "true").lower() in {"1", "true", "yes", "on"}:
                if no_publish_code == "NO_SAFE_CANDIDATE":
                    notification = self.telegram_notifier.notify_no_safe_candidate(selection, dry_run=dry_run)
                else:
                    notification = self.telegram_notifier.notify_no_candidate(selection, dry_run=dry_run)
                self.repository.insert_telegram_log(
                    message=notification.get("message", ""),
                    status=notification.get("status", "FAILED"),
                    sent_at=utc_now_iso(),
                    error_message=notification.get("error_message", ""),
                )
                self.repository.insert_pipeline_log(
                    "telegram_notify",
                    "COMPLETED" if notification.get("status") in {"NOTIFIED", "DRY_RUN"} else "FAILED",
                    f"게시 상태 운영 알림: {notification.get('status')}",
                )
            publish_results.append({"status": no_publish_code or "SKIPPED", "facebook_status": "SKIPPED", "telegram_status": "SKIPPED", "error_message": skip_message})
        elif dry_run:
            publish_result_label = "DRY_RUN_EVALUATED"
            publish_results.append({
                "status": "DRY_RUN_EVALUATED",
                "facebook_status": "DRY_RUN",
                "telegram_status": "DRY_RUN",
                "error_message": "",
                "message": "dry-run 평가만 수행했습니다. 실제 Facebook 게시와 DB 게시 상태 변경은 하지 않습니다.",
            })
        else:
            publish_attempted = True
            publish_results = [self.auto_publish(candidate, dry_run=dry_run) for candidate in selected_candidates[:1]]
            publish_result_label = publish_results[0].get("facebook_status") or publish_results[0].get("status", "UNKNOWN")

        selection["publish_attempted"] = publish_attempted
        selection["publish_result"] = publish_result_label
        selection["no_publish_reason"] = no_publish_reason
        if isinstance(selection.get("dry_run_evaluation"), dict):
            selection["dry_run_evaluation"]["publish_attempted"] = publish_attempted
            selection["dry_run_evaluation"]["no_publish_reason"] = no_publish_reason
        self.log_selection_result(selection)

        final_candidates = self.repository.list_candidates()
        return {
            "cycle_id": cycle_id,
            "dry_run": dry_run,
            "collected_count": len(collected_items),
            "saved_count": len(saved_candidates),
            "processed_count": len(processed_candidates),
            "duplicate_count": sum(1 for candidate in final_candidates if candidate.status == "DUPLICATE"),
            "skipped_count": sum(1 for candidate in final_candidates if candidate.status.startswith("SKIPPED") or candidate.status == "EXPIRED"),
            "selected_count": len(selected_candidates),
            "threshold": selection.get("threshold_used", selection.get("today_avg_score", 0)),
            "minimum_safe_score": selection.get("minimum_safe_score", minimum_safe_score),
            "saved": [candidate.to_dict() for candidate in final_candidates],
            "ready_to_publish": ready_snapshot,
            "publish_results": publish_results,
            "dry_run_evaluation": selection.get("dry_run_evaluation", {}),
            "selection_log": self.selection_log_payload(selection),
            "report": self.build_report(dry_run, len(collected_items), len(saved_candidates), final_candidates, selected_candidates, publish_results, selection.get("threshold_used", 0)),
        }

    def collect(self, keyword: str, allow_seed: bool = False) -> list[NewsItem]:
        items: list[NewsItem] = []
        for collector in self.collectors:
            try:
                self.repository.insert_pipeline_log("collect", "STARTED", f"{collector.__class__.__name__} 진입: 뉴스 수집 시작")
                collected = collector.collect(keyword)
                english_items = []
                for index, item in enumerate(collected, start=1):
                    if is_english_article(item):
                        item.language = "en"
                        english_items.append(item)
                        self.repository.insert_pipeline_log("collect", "COMPLETED", f"{collector.__class__.__name__} {index}번 영문 기사 확인: {item.title[:120]}")
                    else:
                        self.repository.insert_pipeline_log("collect", "SKIPPED", f"{collector.__class__.__name__} {index}번 기사 제외: 영문 기사 아님 - {item.title[:120]}")
                items.extend(english_items)
                self.repository.insert_pipeline_log("collect", "COMPLETED", f"{collector.__class__.__name__} 수집 완료: 전체 {len(collected)}건, 영문 {len(english_items)}건")
            except Exception as exc:
                self.repository.insert_pipeline_log("collect", "FAILED", f"{collector.__class__.__name__} 수집 실패: {str(exc)[:180]}")
        if items:
            return items
        self.repository.insert_pipeline_log("collect", "SKIPPED", "영문 기사 수집 결과가 없어 이번 사이클은 게시 없이 종료합니다.")
        return self._dry_run_seed_items(keyword) if allow_seed and os.getenv("NEWS_DRY_RUN_USE_SEED", "").lower() in {"1", "true", "yes"} else []

    def save_normalized(self, item: NewsItem, keyword: str) -> NewsCandidate:
        candidate = normalize_news_item(NewsCandidate.from_item(item))
        candidate.keyword = keyword
        candidate.cycle_id = today_cycle_id(parse_iso(candidate.collected_at))
        candidate.status = "NORMALIZED"
        candidate.publish_status = "NORMALIZED"
        candidate.post_expired = False
        saved = self.repository.save(candidate)
        self.repository.insert_pipeline_log("save", "COMPLETED", f"전체 결과 DB 저장: {saved.title}", saved.id)
        return saved

    def process_candidate(self, candidate: NewsCandidate, dry_run: bool = False, threshold: float = 75.0) -> NewsCandidate:
        if getattr(candidate, "existing_representative", False):
            self.repository.insert_pipeline_log(
                "candidate_group",
                "COMPLETED",
                f"기존 대표 후보 갱신: {candidate.title} / 중복 {candidate.duplicate_count}건 / 관련 출처 {candidate.related_source_count}개",
                candidate.id,
            )
            return candidate
        self.repository.insert_pipeline_log("article", "STARTED", f"기사 처리 시작: {candidate.title}", candidate.id)
        validation_error = self.validate_text(candidate)
        if validation_error:
            candidate.status = "TEXT_INVALID"
            candidate.publish_status = "TEXT_INVALID"
            candidate.fail_reason = validation_error
            candidate.skip_reason = validation_error
            self.repository.insert_pipeline_log("text_validation", "FAILED", f"텍스트 검증 실패: {validation_error} / {candidate.title}", candidate.id)
            return self.repository.update_candidate(candidate)

        summary = self.summarizer.summarize(candidate)
        if not dry_run and (not summary.short_summary or summary.risk_notes.startswith("Rule-based summary")):
            candidate.status = "FAILED"
            candidate.publish_status = "FAILED"
            candidate.fail_reason = "Local LLaMA 요약 응답 실패 또는 시간 초과로 게시 중단"
            self.repository.insert_pipeline_log("llama_summary", "FAILED", candidate.fail_reason, candidate.id)
            self.telegram_notifier.notify_failure(candidate, candidate.fail_reason, dry_run=False)
            return self.repository.update_candidate(candidate)

        candidate.short_summary = summary.short_summary
        candidate.key_points = "\n".join(summary.key_points[:3])
        candidate.relevance_reason = summary.relevance_reason
        candidate.risk_notes = summary.risk_notes
        candidate.generated_title = summary.generated_title or candidate.title
        candidate.generated_summary_en = summary.generated_summary_en
        candidate.generated_why_it_matters_en = summary.generated_why_it_matters_en
        candidate.status = "SUMMARIZED"
        candidate.publish_status = "SUMMARIZED"
        candidate = self.repository.update_candidate(candidate)
        self.repository.insert_pipeline_log("llama_summary", "COMPLETED", f"LLaMA 요약 완료: {candidate.title}", candidate.id)

        duplicate_result = self.check_duplicate(candidate)
        if duplicate_result.is_duplicate:
            candidate.status = "DUPLICATE"
            candidate.publish_status = "DUPLICATE"
            candidate.duplicate_group_id = duplicate_result.duplicate_group_id
            candidate.duplicate_risk_score = duplicate_result.duplicate_risk_score
            candidate.skip_reason = f"중복 기사 제외: {duplicate_result.reason}"
            candidate.risk_notes = _append_note(candidate.risk_notes, candidate.skip_reason)
            self.repository.insert_pipeline_log("duplicate_check", "SKIPPED", f"중복 기사 제외: {candidate.title}", candidate.id)
            return self.repository.update_candidate(candidate)
        self.repository.insert_pipeline_log("duplicate_check", "COMPLETED", f"중복 확인 완료: {candidate.title}", candidate.id)

        evaluation = self.evaluator.evaluate(candidate, threshold=threshold)
        candidate.evaluation_score = evaluation.total_score
        candidate.duplicate_risk_score = evaluation.duplicate_risk_score
        candidate.foreign_worker_relevance_score = evaluation.foreign_worker_relevance_score
        candidate.korea_relevance_score = evaluation.korea_relevance_score
        candidate.visa_or_labor_policy_score = evaluation.visa_or_labor_policy_score
        candidate.freshness_score = evaluation.freshness_score
        candidate.source_reliability_score = evaluation.source_reliability_score
        candidate.facebook_post_suitability_score = evaluation.facebook_post_suitability_score
        candidate.score_threshold = evaluation.threshold
        candidate.score_breakdown_json = evaluation.score_breakdown_json
        candidate.risk_level = "HIGH" if evaluation.duplicate_risk_score >= 0.85 else "LOW"
        candidate.status = evaluation.decision
        candidate.publish_status = evaluation.decision
        if evaluation.decision == "READY_TO_PUBLISH":
            candidate.selection_reason = evaluation.reason
            self.repository.insert_pipeline_log("queue", "COMPLETED", f"Facebook 등록 대상 확정: {candidate.title} ({candidate.evaluation_score:.0f}/{threshold:.0f})", candidate.id)
        else:
            candidate.skip_reason = evaluation.reason
            self.repository.insert_pipeline_log("queue", "SKIPPED", f"게시 기준 미달로 제외: {candidate.title} ({candidate.evaluation_score:.0f}/{threshold:.0f})", candidate.id)
        candidate.risk_notes = _append_note(candidate.risk_notes, evaluation.reason)
        self.repository.insert_pipeline_log("score", "COMPLETED", f"점수 평가 완료: {candidate.title} ({candidate.evaluation_score:.0f}/{threshold:.0f})", candidate.id)
        return self.repository.update_candidate(candidate)

    def validate_text(self, candidate: NewsCandidate) -> str:
        text = " ".join(part for part in (candidate.title, candidate.summary, candidate.content) if part).strip()
        if not candidate.title.strip():
            return "제목이 없습니다."
        if not candidate.source_url.strip():
            return "원문 URL이 없습니다."
        if len(text) < 30:
            return "요약 가능한 텍스트가 너무 짧습니다."
        lowered = text.lower()
        if any(term in lowered for term in ("casino", "coupon", "lottery", "click here", "advertorial")):
            return "광고성 또는 스팸성 기사입니다."
        relevance_terms = ("foreign worker", "migrant", "visa", "korea", "e-9", "e-7", "employment", "labor", "immigration")
        if not any(term in lowered for term in relevance_terms):
            return "한국 외국인 취업/비자/생활/노동 정보 관련성이 부족합니다."
        self.repository.insert_pipeline_log("text_validation", "COMPLETED", f"텍스트 검증 완료: {candidate.title}", candidate.id)
        return ""

    def check_duplicate(self, candidate: NewsCandidate) -> DuplicateCheckResult:
        existing = self.repository.list_candidates()
        deterministic = check_duplicate(candidate, existing)
        if deterministic.is_duplicate:
            return deterministic
        published = self.repository.list_recent_published(limit=20)
        llama_duplicate, confidence, reason = self.llama_duplicate_checker.check(candidate, published)
        if llama_duplicate and confidence >= 0.75:
            return DuplicateCheckResult(True, published[0].duplicate_group_id if published else candidate.duplicate_group_id, confidence, reason, "local_llama")
        return deterministic

    def evaluate_publish_candidates(self, cycle_id: str) -> dict:
        now = datetime.now(timezone.utc)
        cycle_id = today_cycle_id(now)
        recent_cutoff = now - timedelta(hours=1)
        minimum_safe_score = self.minimum_publish_score()
        today_ready = self.repository.list_ready_for_cycle(cycle_id, limit=500)
        today_scores = [candidate.evaluation_score for candidate in today_ready if candidate.evaluation_score > 0]
        today_avg_score = round(sum(today_scores) / len(today_scores), 2) if today_scores else 0.0

        recent_pool = [candidate for candidate in today_ready if parse_iso(candidate.collected_at) >= recent_cutoff]
        recent_ids = {candidate.id for candidate in recent_pool}
        backlog_all = [candidate for candidate in today_ready if candidate.id not in recent_ids]
        backlog_pool = [candidate for candidate in backlog_all if candidate.evaluation_score >= today_avg_score]

        candidate_map: dict[int, NewsCandidate] = {}
        for candidate in recent_pool + backlog_pool:
            if candidate.id is not None:
                candidate_map[candidate.id] = candidate
        fallback_used = False
        fallback_candidates = [
            candidate
            for candidate in sorted(today_ready, key=lambda item: (item.evaluation_score, parse_iso(item.collected_at)), reverse=True)
            if candidate.evaluation_score >= minimum_safe_score and candidate.id is not None and candidate.id not in candidate_map
        ]
        current_best_score = max((candidate.evaluation_score for candidate in candidate_map.values()), default=0.0)
        if fallback_candidates and (not candidate_map or fallback_candidates[0].evaluation_score > current_best_score):
            fallback_used = True
            candidate_map[fallback_candidates[0].id] = fallback_candidates[0]

        facebook_posts = self.fetch_facebook_engagement_samples()
        scored = [
            self.score_publish_candidate(
                candidate,
                now=now,
                today_avg_score=today_avg_score,
                recent_ids=recent_ids,
                facebook_posts=facebook_posts,
            )
            for candidate in candidate_map.values()
        ]
        publishable = [item for item in scored if item["base_score"] >= minimum_safe_score and not item["blocked"]]
        publishable.sort(
            key=lambda item: (
                item["final_score"],
                1 if item["is_recent"] else 0,
                item["base_score"],
                parse_iso(item["collected_at"]),
            ),
            reverse=True,
        )
        selected_score = publishable[0] if publishable else None
        selected = selected_score["candidate"] if selected_score else None
        no_publish_reason = ""
        if not today_ready:
            no_publish_reason = "오늘 READY_TO_PUBLISH 후보가 없습니다."
        elif not publishable:
            best = max(scored, key=lambda item: item["base_score"], default=None)
            no_publish_reason = f"최소 안전 점수 {minimum_safe_score:.0f}점 이상 후보가 없습니다."
            if best:
                no_publish_reason = f"{no_publish_reason} 최고 후보 점수: {best['base_score']:.0f}점"

        if selected:
            self.repository.insert_pipeline_log(
                "queue",
                "COMPLETED",
                f"게시 후보 선택: {selected.title} (base {selected_score['base_score']:.0f}, final {selected_score['final_score']:.0f}, 후보 {len(publishable)}건)",
                selected.id,
            )

        return {
            "cycle_id": cycle_id,
            "recent_pool_count": len(recent_pool),
            "backlog_pool_count": len(backlog_pool),
            "candidate_pool_count": len(scored),
            "today_avg_score": today_avg_score,
            "minimum_safe_score": minimum_safe_score,
            "selected_candidate": selected,
            "selected_score": selected_score,
            "publish_attempted": False,
            "publish_result": "SKIPPED",
            "no_publish_reason": no_publish_reason,
            "remaining_ready_count": len(today_ready) - (1 if selected else 0),
            "fallback_used": fallback_used,
            "dry_run_evaluation": {
                "recent_pool_top_5": [self.score_summary(item) for item in sorted([self.score_publish_candidate(candidate, now, today_avg_score, recent_ids, facebook_posts) for candidate in recent_pool], key=lambda row: row["final_score"], reverse=True)[:5]],
                "backlog_pool_top_5": [self.score_summary(item) for item in sorted([self.score_publish_candidate(candidate, now, today_avg_score, recent_ids, facebook_posts) for candidate in backlog_pool], key=lambda row: row["final_score"], reverse=True)[:5]],
                "final_candidate_top_10": [self.score_summary(item) for item in publishable[:10]],
                "selected_candidate": self.score_summary(selected_score) if selected_score else None,
                "score_breakdown": selected_score["breakdown"] if selected_score else {},
                "will_publish": bool(selected_score),
                "no_publish_reason": no_publish_reason,
            },
        }

    def evaluate_publish_candidates_v2(self, cycle_id: str, dry_run: bool = False) -> dict:
        now = datetime.now(timezone.utc)
        cycle_id = today_cycle_id(now)
        recent_cutoff = now - timedelta(hours=1)
        all_candidates = self.repository.list_publish_candidates_for_cycle(cycle_id, limit=1000)
        today_all_candidates = [candidate for candidate in self.repository.list_candidates() if candidate.cycle_id == cycle_id]
        today_unposted_candidates = [
            candidate
            for candidate in today_all_candidates
            if not candidate.published_at
            and not candidate.facebook_post_url
            and not candidate.post_expired
            and candidate.publish_status not in {"POSTED", "PUBLISHED", "NOTIFIED", "POST_EXPIRED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}
            and candidate.status not in {"POSTED", "PUBLISHED", "NOTIFIED", "POST_EXPIRED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}
        ]
        ready_candidates = [candidate for candidate in all_candidates if candidate.publish_status == "READY_TO_PUBLISH" or candidate.status == "READY_TO_PUBLISH"]
        retryable_candidates = [candidate for candidate in all_candidates if candidate.publish_status == "FAILED_RETRYABLE" or candidate.status == "FAILED_RETRYABLE"]
        expanded_candidates = [candidate for candidate in all_candidates if candidate.id not in {item.id for item in ready_candidates + retryable_candidates}]

        prepared_candidates = self.prepare_publish_candidates(all_candidates, dry_run=dry_run)
        today_article_count = len(today_all_candidates)
        today_unposted_count = len(today_unposted_candidates)
        all_scores = [float(candidate.evaluation_score or 0.0) for candidate in today_all_candidates if float(candidate.evaluation_score or 0.0) > 0]
        publishable_scores = [float(candidate.evaluation_score or 0.0) for candidate in prepared_candidates if float(candidate.evaluation_score or 0.0) > 0]
        today_avg_score = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0
        thresholds = self.publish_threshold_sequence(today_avg_score)
        threshold_used = thresholds[-1][1] if thresholds else self.minimum_publish_score()
        no_publish_code = ""
        no_publish_reason = ""
        promoted_to_ready = False

        recent_pool = [candidate for candidate in prepared_candidates if parse_iso(candidate.collected_at) >= recent_cutoff]
        recent_ids = {candidate.id for candidate in recent_pool}
        facebook_posts = self.fetch_facebook_engagement_samples()
        selected_score = None
        selected = None
        selected_from_status = ""
        publishable: list[dict] = []

        for label, threshold in thresholds:
            scored = [
                self.score_publish_candidate(candidate, now=now, today_avg_score=today_avg_score, recent_ids=recent_ids, facebook_posts=facebook_posts)
                for candidate in prepared_candidates
            ]
            publishable = [item for item in scored if item["base_score"] >= threshold and not item["blocked"]]
            publishable.sort(
                key=lambda item: (
                    item["final_score"],
                    1 if item["is_recent"] else 0,
                    item["base_score"],
                    parse_iso(item["collected_at"]),
                ),
                reverse=True,
            )
            if publishable:
                selected_score = publishable[0]
                selected = selected_score["candidate"]
                threshold_used = threshold
                break

        if selected:
            selected_from_status = selected.publish_status or selected.status
            if selected.publish_status != "READY_TO_PUBLISH" or selected.status != "READY_TO_PUBLISH":
                promoted_to_ready = True
                selected.status = "READY_TO_PUBLISH"
                selected.publish_status = "READY_TO_PUBLISH"
                selected.score_threshold = threshold_used
                selected.selection_reason = selected.selection_reason or f"게시 후보 재평가에서 threshold {threshold_used:.0f}점 기준을 통과했습니다."
                selected.skip_reason = ""
                if not dry_run:
                    self.repository.update_candidate(selected)
            self.repository.insert_pipeline_log(
                "queue",
                "COMPLETED",
                f"게시 후보 선택: {selected.title} (base {selected_score['base_score']:.0f}, final {selected_score['final_score']:.0f}, threshold {threshold_used:.0f})",
                selected.id,
            )
        else:
            if today_article_count == 0:
                no_publish_code = "NO_CANDIDATE"
                no_publish_reason = "오늘 수집된 미게시 기사가 없어 게시 후보를 만들 수 없습니다."
            else:
                no_publish_code = "NO_SAFE_CANDIDATE"
                best = max(publishable_scores, default=0.0)
                no_publish_reason = f"오늘 기사 {today_article_count}건을 재평가했지만 최소 안전 점수 40점 이상 후보가 없습니다. 최고 점수: {best:.0f}점"

        remaining_ready_count = max(0, len([candidate for candidate in prepared_candidates if candidate.publish_status == "READY_TO_PUBLISH"]) - (1 if selected else 0))
        final_top = publishable[:10] if publishable else []
        return {
            "cycle_id": cycle_id,
            "ready_count": len(ready_candidates),
            "retryable_count": len(retryable_candidates),
            "recent_pool_count": len(recent_pool),
            "backlog_pool_count": max(0, len(prepared_candidates) - len(recent_pool)),
            "candidate_pool_count": len(prepared_candidates),
            "expanded_candidate_count": len(expanded_candidates),
            "today_article_count": today_article_count,
            "today_unposted_count": today_unposted_count,
            "today_avg_score": today_avg_score,
            "minimum_safe_score": self.minimum_publish_score(),
            "threshold_used": threshold_used,
            "threshold_sequence": [{"label": label, "threshold": threshold} for label, threshold in thresholds],
            "selected_candidate": selected,
            "selected_score": selected_score,
            "selected_from_status": selected_from_status,
            "publish_attempted": False,
            "publish_result": "SKIPPED",
            "no_publish_code": no_publish_code,
            "no_publish_reason": no_publish_reason,
            "remaining_ready_count": remaining_ready_count,
            "fallback_used": bool(expanded_candidates),
            "promoted_to_ready": promoted_to_ready,
            "cooldown_remaining": 0,
            "dry_run_evaluation": {
                "ready_count": len(ready_candidates),
                "retryable_count": len(retryable_candidates),
                "expanded_candidate_count": len(expanded_candidates),
                "today_article_count": today_article_count,
                "today_unposted_count": today_unposted_count,
                "minimum_safe_score": self.minimum_publish_score(),
                "threshold_used": threshold_used,
                "selected_candidate": self.score_summary(selected_score) if selected_score else None,
                "promoted_to_ready": promoted_to_ready,
                "publish_attempted": False,
                "no_publish_reason": no_publish_reason,
                "final_candidate_top_10": [self.score_summary(item) for item in final_top],
                "score_breakdown": selected_score["breakdown"] if selected_score else {},
                "will_publish": bool(selected_score),
            },
        }

    def prepare_publish_candidates(self, candidates: list[NewsCandidate], dry_run: bool = False) -> list[NewsCandidate]:
        prepared: list[NewsCandidate] = []
        for candidate in candidates:
            if int(candidate.publish_attempt_count or 0) >= 3:
                candidate.status = "AUTO_RETRY_BLOCKED"
                candidate.publish_status = "AUTO_RETRY_BLOCKED"
                candidate.skip_reason = "Facebook 자동 재시도 3회 초과로 수동 재게시 대기 상태입니다."
                if not dry_run:
                    self.repository.update_candidate(candidate)
                continue
            if self.required_publish_safety_error(candidate):
                continue
            if candidate.evaluation_score <= 0 or candidate.status in {"COLLECTED", "NORMALIZED", "SUMMARIZED", "SCORED", "SKIPPED_LOW_SCORE"}:
                evaluation = self.evaluator.evaluate(candidate, threshold=40.0)
                candidate.evaluation_score = evaluation.total_score
                candidate.duplicate_risk_score = evaluation.duplicate_risk_score
                candidate.foreign_worker_relevance_score = evaluation.foreign_worker_relevance_score
                candidate.korea_relevance_score = evaluation.korea_relevance_score
                candidate.visa_or_labor_policy_score = evaluation.visa_or_labor_policy_score
                candidate.freshness_score = evaluation.freshness_score
                candidate.source_reliability_score = evaluation.source_reliability_score
                candidate.facebook_post_suitability_score = evaluation.facebook_post_suitability_score
                candidate.score_threshold = 40.0
                candidate.score_breakdown_json = evaluation.score_breakdown_json
                candidate.risk_level = "HIGH" if evaluation.duplicate_risk_score >= 0.85 else candidate.risk_level or "LOW"
                candidate.selection_reason = evaluation.reason if evaluation.total_score >= 40.0 else ""
                candidate.skip_reason = "" if evaluation.total_score >= 40.0 else evaluation.reason
                if not dry_run:
                    self.repository.update_candidate(candidate)
            if not self.required_publish_safety_error(candidate):
                prepared.append(candidate)
        return prepared

    def publish_threshold_sequence(self, today_avg_score: float) -> list[tuple[str, float]]:
        minimum = self.minimum_publish_score()
        raw_thresholds: list[tuple[str, float]] = []
        if today_avg_score >= 40.0:
            raw_thresholds.extend(
                [
                    ("AVG_SCORE", today_avg_score),
                    ("AVG_MINUS_5", today_avg_score - 5.0),
                    ("AVG_MINUS_10", today_avg_score - 10.0),
                ]
            )
        raw_thresholds.extend([("SAFE_50", minimum), ("SAFE_45", 45.0), ("SAFE_40", 40.0)])
        result: list[tuple[str, float]] = []
        seen: set[float] = set()
        for label, threshold in sorted(raw_thresholds, key=lambda item: item[1], reverse=True):
            normalized = round(max(40.0, threshold), 2)
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append((label, normalized))
        return result or [("SAFE_40", 40.0)]

    def cooldown_selection(self, cycle_id: str, cooldown: dict) -> dict:
        ready_candidates = self.repository.list_ready_for_cycle(cycle_id, limit=500)
        candidate_pool = self.repository.list_publish_candidates_for_cycle(cycle_id, limit=1000)
        remaining = int(cooldown.get("remaining_seconds", 0) or 0)
        return {
            "cycle_id": cycle_id,
            "ready_count": len(ready_candidates),
            "retryable_count": len([candidate for candidate in candidate_pool if candidate.publish_status == "FAILED_RETRYABLE" or candidate.status == "FAILED_RETRYABLE"]),
            "recent_pool_count": 0,
            "backlog_pool_count": len(candidate_pool),
            "candidate_pool_count": len(candidate_pool),
            "expanded_candidate_count": 0,
            "today_article_count": 0,
            "today_unposted_count": 0,
            "today_avg_score": 0,
            "minimum_safe_score": self.minimum_publish_score(),
            "threshold_used": 0,
            "selected_candidate": None,
            "selected_score": None,
            "selected_from_status": "",
            "cooldown_remaining": remaining,
            "publish_attempted": False,
            "publish_result": "WAITING_COOLDOWN",
            "no_publish_code": "WAITING_COOLDOWN",
            "no_publish_reason": (
                f"Facebook 게시 대기: 마지막 게시 후 60분 쿨다운 적용 중입니다. "
                f"READY 후보 {len(ready_candidates)}건, 게시 가능 시간 {cooldown.get('next_publish_at', '-')}, "
                f"남은 시간 {int((remaining + 59) // 60)}분"
            ),
            "remaining_ready_count": len(ready_candidates),
            "promoted_to_ready": False,
        }

    def prepare_expanded_candidates(self, cycle_id: str) -> list[NewsCandidate]:
        candidates = self.repository.list_expandable_for_cycle(cycle_id, limit=500)
        prepared: list[NewsCandidate] = []
        for candidate in candidates:
            if self.required_publish_safety_error(candidate):
                continue
            if candidate.evaluation_score <= 0 or candidate.status in {"COLLECTED", "NORMALIZED", "SUMMARIZED", "SCORED"}:
                evaluation = self.evaluator.evaluate(candidate, threshold=40.0)
                candidate.evaluation_score = evaluation.total_score
                candidate.duplicate_risk_score = evaluation.duplicate_risk_score
                candidate.foreign_worker_relevance_score = evaluation.foreign_worker_relevance_score
                candidate.korea_relevance_score = evaluation.korea_relevance_score
                candidate.visa_or_labor_policy_score = evaluation.visa_or_labor_policy_score
                candidate.freshness_score = evaluation.freshness_score
                candidate.source_reliability_score = evaluation.source_reliability_score
                candidate.facebook_post_suitability_score = evaluation.facebook_post_suitability_score
                candidate.score_threshold = 40.0
                candidate.score_breakdown_json = evaluation.score_breakdown_json
                candidate.risk_level = "HIGH" if evaluation.duplicate_risk_score >= 0.85 else candidate.risk_level or "LOW"
                candidate.selection_reason = evaluation.reason if evaluation.total_score >= 40.0 else ""
                candidate.skip_reason = "" if evaluation.total_score >= 40.0 else evaluation.reason
                self.repository.update_candidate(candidate)
            if not self.required_publish_safety_error(candidate):
                prepared.append(candidate)
        return prepared

    def select_and_promote_fallback_candidate(self, candidates: list[NewsCandidate], dry_run: bool = False) -> tuple[NewsCandidate | None, float]:
        for threshold in (45.0, 40.0):
            pool = [
                candidate
                for candidate in candidates
                if candidate.evaluation_score >= threshold
                and candidate.duplicate_risk_score < 0.85
                and candidate.risk_level != "HIGH"
                and not self.required_publish_safety_error(candidate)
            ]
            pool.sort(key=lambda item: (item.evaluation_score, parse_iso(item.collected_at)), reverse=True)
            if not pool:
                continue
            selected = pool[0]
            selected.status = "READY_TO_PUBLISH"
            selected.publish_status = "READY_TO_PUBLISH"
            selected.score_threshold = threshold
            selected.selection_reason = selected.selection_reason or f"확장 후보 평가에서 동적 기준 {threshold:.0f}점을 통과했습니다."
            selected.skip_reason = ""
            if not dry_run:
                self.repository.update_candidate(selected)
            return selected, threshold
        return None, 40.0

    def required_publish_safety_error(self, candidate: NewsCandidate) -> str:
        if not candidate.title.strip():
            return "제목 없음"
        if not candidate.source_url.strip():
            return "원문 URL 없음"
        if candidate.status in {"DUPLICATE", "TEXT_INVALID", "POSTED", "PUBLISHED", "NOTIFIED", "POST_EXPIRED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}:
            return f"게시 제외 상태: {candidate.status}"
        if candidate.publish_status in {"DUPLICATE", "TEXT_INVALID", "POSTED", "PUBLISHED", "NOTIFIED", "POST_EXPIRED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}:
            return f"게시 제외 상태: {candidate.publish_status}"
        if candidate.risk_level == "HIGH":
            return "고위험 후보"
        text = f"{candidate.title} {candidate.summary} {candidate.content} {candidate.short_summary} {candidate.relevance_reason}".lower()
        if not any(term in text for term in ("foreign worker", "migrant", "visa", "korea", "employment", "labor", "immigration", "e-9", "e-7")):
            return "외국인 근로자/비자/고용 관련성 부족"
        if any(term in text for term in ("casino", "coupon", "lottery", "click here", "advertorial")):
            return "광고성 또는 스팸성 표현"
        return ""

    def score_publish_candidate(
        self,
        candidate: NewsCandidate,
        now: datetime,
        today_avg_score: float,
        recent_ids: set[int | None],
        facebook_posts: list[dict],
    ) -> dict:
        base_score = float(candidate.evaluation_score or 0.0)
        is_recent = candidate.id in recent_ids or now - parse_iso(candidate.collected_at) <= timedelta(hours=1)
        freshness_score = 10.0 if is_recent else 0.0
        backlog_bonus = 0.0 if is_recent else 5.0 if base_score >= today_avg_score else 0.0
        engagement_score = self.engagement_prediction_score(candidate, facebook_posts)
        group_signal_score = min(
            8.0,
            max(0, int(candidate.related_source_count or 0) - 1) * 1.5
            + max(0, int(candidate.duplicate_count or 0)) * 0.08,
        )
        duplication_penalty = 30.0 if float(candidate.duplicate_risk_score or 0.0) >= 0.6 else 0.0
        risk_penalty = self.risk_penalty(candidate)
        final_score = base_score + freshness_score + backlog_bonus + engagement_score + group_signal_score - duplication_penalty - risk_penalty
        blocked = candidate.risk_level == "HIGH" or not candidate.source_url or duplication_penalty >= 30.0
        return {
            "candidate": candidate,
            "id": candidate.id,
            "title": candidate.title,
            "collected_at": candidate.collected_at,
            "base_score": round(base_score, 2),
            "freshness_score": round(freshness_score, 2),
            "backlog_above_average_bonus": round(backlog_bonus, 2),
            "engagement_prediction_score": round(engagement_score, 2),
            "group_signal_score": round(group_signal_score, 2),
            "duplication_penalty": round(duplication_penalty, 2),
            "risk_penalty": round(risk_penalty, 2),
            "final_score": round(final_score, 2),
            "is_recent": is_recent,
            "blocked": blocked,
            "breakdown": {
                "base_score": round(base_score, 2),
                "freshness_score": round(freshness_score, 2),
                "backlog_above_average_bonus": round(backlog_bonus, 2),
                "engagement_prediction_score": round(engagement_score, 2),
                "group_signal_score": round(group_signal_score, 2),
                "duplication_penalty": round(duplication_penalty, 2),
                "risk_penalty": round(risk_penalty, 2),
                "final_score": round(final_score, 2),
                "today_avg_score": today_avg_score,
            },
        }

    def score_summary(self, score: dict | None) -> dict | None:
        if not score:
            return None
        return {
            "id": score["id"],
            "title": score["title"],
            "base_score": score["base_score"],
            "freshness_score": score["freshness_score"],
            "engagement_prediction_score": score["engagement_prediction_score"],
            "group_signal_score": score.get("group_signal_score", 0),
            "final_score": score["final_score"],
            "collected_at": score["collected_at"],
        }

    def fetch_facebook_engagement_samples(self) -> list[dict]:
        page_id = os.getenv("FACEBOOK_PAGE_ID", "").strip()
        access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "").strip()
        client = getattr(self.facebook_publisher, "client", None)
        if not page_id or not access_token or not client or not hasattr(client, "recent_feed"):
            return []
        posts = client.recent_feed(page_id=page_id, access_token=access_token, limit=25)
        for post in posts[:5]:
            post_id = str(post.get("id") or "")
            if post_id and hasattr(client, "comments"):
                post["comment_items"] = client.comments(post_id=post_id, access_token=access_token, limit=10)
        return posts

    def engagement_prediction_score(self, candidate: NewsCandidate, facebook_posts: list[dict]) -> float:
        if not facebook_posts:
            return 0.0
        candidate_terms = keywords_for_similarity(f"{candidate.title} {candidate.summary} {candidate.short_summary} {candidate.key_points}")
        if not candidate_terms:
            return 0.0
        best_score = 0.0
        for post in facebook_posts:
            message = str(post.get("message") or "")
            post_terms = keywords_for_similarity(message)
            similarity = keyword_similarity(candidate_terms, post_terms)
            if similarity < 0.12:
                continue
            reactions = int(((post.get("reactions") or {}).get("summary") or {}).get("total_count") or 0)
            comments = int(((post.get("comments") or {}).get("summary") or {}).get("total_count") or 0)
            shares = int((post.get("shares") or {}).get("count") or 0)
            engagement = reactions + comments * 2 + shares * 3
            negative_penalty = self.negative_comment_penalty(post.get("comment_items") or [])
            best_score = max(best_score, min(18.0, similarity * min(60.0, engagement) / 4.0) - negative_penalty)
        return max(-10.0, min(18.0, best_score))

    def negative_comment_penalty(self, comments: list[dict]) -> float:
        negative_terms = ("spam", "fake", "scam", "wrong", "hate", "angry", "bad", "false")
        penalty = 0.0
        for comment in comments:
            message = str(comment.get("message") or "").lower()
            if any(term in message for term in negative_terms):
                penalty += 2.0
        return min(10.0, penalty)

    def risk_penalty(self, candidate: NewsCandidate) -> float:
        if candidate.risk_level == "HIGH":
            return 100.0
        notes = f"{candidate.risk_notes} {candidate.fail_reason} {candidate.skip_reason}".lower()
        penalty = 0.0
        if "spam" in notes or "광고" in notes:
            penalty += 20.0
        if "위험" in notes or "high" in notes:
            penalty += 15.0
        return penalty

    def selection_log_payload(self, selection: dict) -> dict:
        selected_score = selection.get("selected_score") or {}
        selected = selection.get("selected_candidate")
        return {
            "cycle_id": selection.get("cycle_id"),
            "recent_pool_count": selection.get("recent_pool_count", 0),
            "backlog_pool_count": selection.get("backlog_pool_count", 0),
            "candidate_pool_count": selection.get("candidate_pool_count", 0),
            "ready_count": selection.get("ready_count", 0),
            "retryable_count": selection.get("retryable_count", 0),
            "expanded_candidate_count": selection.get("expanded_candidate_count", 0),
            "today_article_count": selection.get("today_article_count", 0),
            "today_unposted_count": selection.get("today_unposted_count", 0),
            "today_avg_score": selection.get("today_avg_score", 0),
            "minimum_safe_score": selection.get("minimum_safe_score", 0),
            "threshold_used": selection.get("threshold_used", 0),
            "selected_news_id": selected.id if selected else None,
            "selected_title": selected.title if selected else "",
            "selected_from_status": selection.get("selected_from_status", ""),
            "base_score": selected_score.get("base_score", 0),
            "freshness_score": selected_score.get("freshness_score", 0),
            "engagement_prediction_score": selected_score.get("engagement_prediction_score", 0),
            "final_score": selected_score.get("final_score", 0),
            "publish_attempted": selection.get("publish_attempted", False),
            "publish_result": selection.get("publish_result", "SKIPPED"),
            "cooldown_remaining": selection.get("cooldown_remaining", 0),
            "no_publish_code": selection.get("no_publish_code", ""),
            "no_publish_reason": selection.get("no_publish_reason", ""),
            "remaining_ready_count": selection.get("remaining_ready_count", 0),
            "promoted_to_ready": selection.get("promoted_to_ready", False),
        }

    def log_selection_result(self, selection: dict) -> None:
        payload = self.selection_log_payload(selection)
        if payload["no_publish_code"] == "WAITING_COOLDOWN":
            message = (
                f"게시 대기: 쿨다운 적용 중, READY {payload['ready_count']}건, "
                f"후보풀 {payload['candidate_pool_count']}건, 남은 {int((payload['cooldown_remaining'] + 59) // 60)}분"
            )
            status = "WAITING"
        else:
            message = (
                f"게시 후보 평가: 후보 {payload['candidate_pool_count']}건, 선택 "
                f"{payload['selected_news_id'] or '-'}, final {payload['final_score']:.0f}, 결과 {payload['publish_result']}"
            )
            status = "COMPLETED" if payload["selected_news_id"] else "SKIPPED"
        self.repository.insert_pipeline_log("publish_selection", status, message, payload_json=json.dumps(payload, ensure_ascii=False))

    def auto_publish(self, candidate: NewsCandidate, dry_run: bool = False) -> dict:
        timestamp = utc_now_iso()
        candidate.last_publish_attempt_at = timestamp
        candidate.publish_attempt_count = int(candidate.publish_attempt_count or 0) + 1
        self.repository.update_candidate(candidate)
        self.repository.insert_pipeline_log("facebook_publish", "STARTED", f"Facebook 게시 시작: {candidate.title}", candidate.id)
        publish_result = self.facebook_publisher.publish(candidate, dry_run=dry_run)
        status = publish_result.get("status", "FAILED")
        facebook_post_id = publish_result.get("facebook_post_id", "")
        facebook_post_url = publish_result.get("facebook_post_url", "")
        error_code = publish_result.get("error_code", "")
        error_message = publish_result.get("error_message", "")
        message_preview = publish_result.get("message", "")[:1000]
        token_debug = publish_result.get("token_debug") or {}
        if token_debug:
            self.repository.insert_pipeline_log(
                "facebook_token_debug",
                "COMPLETED" if token_debug.get("is_valid") else "FAILED",
                (
                    f"Facebook token debug: type={token_debug.get('token_type') or '-'}, "
                    f"is_valid={token_debug.get('is_valid')}, "
                    f"profile_id={token_debug.get('profile_id') or '-'}, "
                    f"expires_at={token_debug.get('expires_at') or '-'}"
                ),
                candidate.id,
                payload_json=json.dumps(token_debug, ensure_ascii=False),
            )
        self.repository.insert_facebook_log(
            news_candidate_id=candidate.id,
            page_id=publish_result.get("page_id", ""),
            facebook_post_id=facebook_post_id,
            facebook_permalink=facebook_post_url,
            status=status,
            score=candidate.evaluation_score,
            threshold=candidate.score_threshold,
            message_preview=message_preview,
            response_code=publish_result.get("response_code", ""),
            response_body=json.dumps({"facebook_response": publish_result.get("response_body", ""), "token_debug": token_debug}, ensure_ascii=False),
            error_code=error_code,
            error_message=error_message,
            published_at=timestamp,
        )

        if status in ("DRY_RUN", "PUBLISHED"):
            published_status = "DRY_RUN_PUBLISHED" if dry_run else "POSTED"
            self.repository.mark_status(
                candidate.id,
                published_status,
                published_at=timestamp,
                facebook_post_url=facebook_post_url,
                facebook_post_id=facebook_post_id,
                last_publish_attempt_at=timestamp,
                publish_attempt_count=candidate.publish_attempt_count,
                publish_status=published_status,
            )
            candidate.status = published_status
            candidate.publish_status = published_status
            candidate.published_at = timestamp
            candidate.facebook_post_url = facebook_post_url
            candidate.facebook_post_id = facebook_post_id
            self.repository.insert_pipeline_log("facebook_publish", "COMPLETED", f"Facebook 게시 완료: {candidate.title}", candidate.id)
        else:
            manual_repost_issue = error_code in {
                "FACEBOOK_TOKEN_EXPIRED",
                "FACEBOOK_TOKEN_INVALID",
                "FACEBOOK_PAGE_TOKEN_MISMATCH",
                "FACEBOOK_PERMISSION_ERROR",
                "FACEBOOK_PERMISSION_MISSING",
                "FACEBOOK_TOKEN_OR_PERMISSION_ERROR",
                "MISSING_FACEBOOK_ENV",
                "MISSING_FACEBOOK_APP_TOKEN",
            }
            next_status = "AUTO_RETRY_BLOCKED" if candidate.publish_attempt_count >= 3 else "FAILED_RETRYABLE"
            self.repository.mark_status(
                candidate.id,
                next_status,
                fail_reason=error_message,
                last_publish_attempt_at=timestamp,
                publish_attempt_count=candidate.publish_attempt_count,
                publish_status=next_status,
            )
            candidate.status = next_status
            candidate.publish_status = next_status
            candidate.fail_reason = error_message
            if manual_repost_issue:
                token_alert = self.telegram_notifier.notify_facebook_error(candidate, error_message, next_status, dry_run=dry_run)
                self.repository.insert_telegram_log(
                    news_candidate_id=candidate.id,
                    message=token_alert.get("message", ""),
                    status=token_alert.get("status", "FAILED"),
                    error_message=token_alert.get("error_message", ""),
                    sent_at=utc_now_iso(),
                )
            self.repository.insert_pipeline_log("facebook_publish", "FAILED", f"Facebook 게시 실패: {candidate.title} / {error_code} {error_message[:180]}", candidate.id)

        notify_result = self.telegram_notifier.notify_publish_result(
            candidate,
            status=candidate.status,
            facebook_post_id=facebook_post_id,
            facebook_post_url=facebook_post_url,
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
            notified_status = candidate.status
            self.repository.mark_status(candidate.id, notified_status, telegram_notified=True, publish_status=notified_status)
            candidate.status = notified_status
            candidate.publish_status = notified_status
            candidate.telegram_notified = True
            self.repository.insert_pipeline_log("telegram_notify", "COMPLETED", f"Telegram 알림 완료: {candidate.title}", candidate.id)
        elif notify_result["status"] == "FAILED":
            self.repository.insert_pipeline_log("telegram_notify", "FAILED", f"Telegram 알림 실패: {candidate.title}", candidate.id)

        return {
            "news_candidate_id": candidate.id,
            "status": candidate.status,
            "facebook_status": status,
            "facebook_post_id": facebook_post_id,
            "facebook_post_url": facebook_post_url,
            "telegram_status": notify_result["status"],
            "message": publish_result.get("message", ""),
            "error_message": error_message or notify_result.get("error_message", ""),
            "token_debug": token_debug,
        }

    def expire_old_unposted_candidates(self, cycle_id: str = "") -> None:
        expired_at = utc_now_iso()
        expired, target_cycle_id = self.repository.expire_ready_before_cycle(cycle_id, expired_at, reason="DAILY_CYCLE_EXPIRED")
        if expired:
            self.repository.insert_pipeline_log(
                "daily_reset",
                "COMPLETED",
                f"이전 일일 사이클 READY 후보 {expired}건 게시 만료 처리",
                payload_json=json.dumps(
                    {
                        "expired_count": expired,
                        "target_cycle_id": target_cycle_id,
                        "new_cycle_id": cycle_id,
                        "expired_at": expired_at,
                        "reason": "DAILY_CYCLE_EXPIRED",
                    },
                    ensure_ascii=False,
                ),
            )

    def ensure_publish_cycle_metadata(self) -> None:
        updated = 0
        for candidate in self.repository.list_candidates():
            changed = False
            if not candidate.cycle_id:
                candidate.cycle_id = today_cycle_id(parse_iso(candidate.collected_at))
                changed = True
            if not candidate.publish_status:
                candidate.publish_status = candidate.status
                changed = True
            if candidate.publish_status == "POST_EXPIRED" and not candidate.post_expired:
                candidate.post_expired = True
                changed = True
            if changed:
                self.repository.update_candidate(candidate)
                updated += 1
        if updated:
            self.repository.insert_pipeline_log("daily_queue", "COMPLETED", f"게시 사이클 메타데이터 {updated}건 보정")

    def restore_today_safe_skipped_candidates(self, minimum_safe_score: float) -> None:
        current_cycle_id = today_cycle_id()
        restored = 0
        for candidate in self.repository.list_candidates():
            if candidate.status != "SKIPPED":
                continue
            if not candidate.skip_reason.startswith("게시 기준"):
                continue
            if candidate.evaluation_score < minimum_safe_score:
                continue
            if candidate.cycle_id != current_cycle_id:
                continue
            candidate.status = "READY_TO_PUBLISH"
            candidate.publish_status = "READY_TO_PUBLISH"
            candidate.post_expired = False
            candidate.selection_reason = f"새 게시 알고리즘 적용: 최소 안전 점수 {minimum_safe_score:.0f}점 이상 후보를 오늘 대기열로 복구"
            self.repository.update_candidate(candidate)
            restored += 1
        if restored:
            self.repository.insert_pipeline_log("daily_queue", "COMPLETED", f"오늘 SKIPPED 후보 {restored}건을 READY_TO_PUBLISH 대기열로 복구")

    def is_publishable_candidate(self, candidate: NewsCandidate) -> bool:
        if candidate.status in {"READY_TO_PUBLISH", "FAILED_RETRYABLE"}:
            return True
        return candidate.status == "SKIPPED" and candidate.skip_reason.startswith("게시 기준")

    def dynamic_threshold(self, queue_count: int = 0, new_candidate_count: int = 0) -> float:
        pressure = max(queue_count, new_candidate_count)
        if pressure >= 100:
            return 90.0
        if pressure >= 50:
            return 85.0
        if pressure >= 20:
            return 80.0
        if pressure >= 8:
            return 75.0
        if pressure >= 3:
            return 70.0
        if pressure >= 1:
            return 65.0
        return self.minimum_publish_score()

    def minimum_publish_score(self) -> float:
        return env_float("NEWS_PUBLISH_MIN_SCORE", 50.0, 40.0, 75.0)

    def unposted_expire_hours(self) -> int:
        return int(env_float("NEWS_UNPOSTED_EXPIRE_HOURS", 24.0, 6.0, 168.0))

    def is_publish_cooldown_active(self) -> bool:
        return self.publish_cooldown_info()["active"]

    def publish_cooldown_info(self) -> dict:
        last = self.repository.last_successful_facebook_publish_at()
        if not last:
            return {"active": False, "last_post_at": "", "next_publish_at": "", "remaining_seconds": 0, "remaining_minutes": 0}
        last_at = parse_iso(last)
        next_at = last_at + timedelta(hours=1)
        remaining = max(0, int((next_at - datetime.now(timezone.utc)).total_seconds()))
        return {
            "active": remaining > 0,
            "last_post_at": last_at.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S"),
            "next_publish_at": next_at.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S"),
            "remaining_seconds": remaining,
            "remaining_minutes": int((remaining + 59) // 60),
        }

    def build_report(
        self,
        dry_run: bool,
        collected_count: int,
        saved_count: int,
        final_candidates: list[NewsCandidate],
        selected_candidates: list[NewsCandidate],
        publish_results: list[dict],
        threshold: float,
    ) -> str:
        selected = selected_candidates[0] if selected_candidates else None
        publish = publish_results[0] if publish_results else {}
        lines = [
            f"[WorkConnect 뉴스 자동화 - {'테스트 실행' if dry_run else '실행'}]",
            f"수집: {collected_count}",
            f"저장: {saved_count}",
            f"오늘 READY 평균 점수: {threshold:.0f}",
            f"중복 제외: {sum(1 for item in final_candidates if item.status == 'DUPLICATE')}",
            f"게시 후보: {len(selected_candidates)}",
            "",
            "선택 기사:",
        ]
        if selected:
            lines.extend([f"- 제목: {selected.title}", f"- 출처: {selected.source_name or selected.source_type}", f"- 점수: {selected.evaluation_score:.0f}", f"- 원문: {selected.source_url}"])
        else:
            lines.append("- 없음")
        lines.extend(["", "게시:", f"- Facebook: {publish.get('facebook_status', 'N/A')}", f"- Telegram: {publish.get('telegram_status', 'N/A')}"])
        return "\n".join(lines)

    def _dry_run_seed_items(self, keyword: str) -> list[NewsItem]:
        return [
            NewsItem(
                title="Korea expands support policy for foreign worker visa holders",
                url="https://example.com/workconnect/news/support-policy",
                source="dry_run",
                summary="Korea is expanding employment visa and stay support for foreign workers seeking stable jobs.",
                language="en",
                category="foreign_worker_policy",
            )
        ]


def _append_note(existing: str, note: str) -> str:
    return "\n".join(part for part in (existing, note) if part)


def today_utc_start() -> datetime:
    return today_window_utc()[0]


def today_window_utc(now: datetime | None = None) -> tuple[datetime, datetime]:
    current = now or datetime.now(timezone.utc)
    local_now = current.astimezone(KST)
    local_start = datetime(local_now.year, local_now.month, local_now.day, tzinfo=KST)
    local_end = local_start + timedelta(days=1)
    return local_start.astimezone(timezone.utc), local_end.astimezone(timezone.utc)


def today_cycle_id(now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    return current.astimezone(KST).strftime("%Y-%m-%d")


def parse_iso(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def is_english_article(item: NewsItem) -> bool:
    text = f"{item.title} {item.summary} {item.content}"
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return False
    ascii_letters = sum(1 for char in letters if "a" <= char.lower() <= "z")
    hangul = sum(1 for char in text if "\uac00" <= char <= "\ud7a3")
    return ascii_letters / max(len(letters), 1) >= 0.65 and hangul <= 3


def env_float(name: str, default: float, minimum: float, maximum: float) -> float:
    try:
        value = float(os.getenv(name, default))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(maximum, value))


def keywords_for_similarity(text: str) -> set[str]:
    normalized = "".join(char.lower() if char.isalnum() else " " for char in text)
    return {word for word in normalized.split() if len(word) >= 4 and word not in STOP_WORDS}


def keyword_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / max(min(len(left), len(right)), 1)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the automated social news publishing pipeline.")
    parser.add_argument("--keyword", default="foreign worker visa Korea", help="News search keyword.")
    parser.add_argument("--limit", type=int, default=1, help="Maximum candidates to publish in one cycle.")
    parser.add_argument("--dry-run", action="store_true", help="Run without external Facebook/Telegram calls.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")
    parser.add_argument("--verbose", action="store_true", help="Print full JSON output.")
    args = parser.parse_args(argv)

    pipeline = NewsPipeline(repository=NewsRepository())
    result = pipeline.run(keyword=args.keyword, dry_run=args.dry_run, limit=args.limit)
    if args.json or args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
