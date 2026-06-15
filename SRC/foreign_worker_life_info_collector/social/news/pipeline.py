"""Automated social news collection, scoring, publishing, and notification pipeline."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from ...utils.date_utils import utc_now_iso
from .collector.article_text_extractor import fetch_article_metadata
from .collector.google_news_collector import GoogleNewsCollector
from .collector.google_news_url_resolver import is_acceptable_source_url, resolve_google_news_url
from .collector.naver_news_collector import NaverNewsCollector
from .duplicate_guard.duplicate_detector import check_duplicate
from .duplicate_guard.llama_duplicate_checker import LlamaDuplicateChecker
from .category_rotation import (
    GROUP_THRESHOLDS,
    SEARCH_KEYWORDS,
    category_group,
    group_threshold,
    recent_category_ratio,
    rotation_score,
    selection_payload_extra,
    target_group,
)
from .evaluator.candidate_evaluator import CandidateEvaluator, NEGATIVE_INCIDENT_TERMS, has_korean_text
from .models import DuplicateCheckResult, NewsCandidate, NewsItem
from .normalizer.news_normalizer import normalize_news_item
from .notifier.telegram_notifier import NewsTelegramNotifier
from .publisher.facebook_publisher import FacebookPublisher
from ..facebook.token_manager import get_facebook_page_token
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

    def apply_evaluation(self, candidate: NewsCandidate, evaluation) -> NewsCandidate:
        candidate.evaluation_score = evaluation.total_score
        candidate.duplicate_risk_score = evaluation.duplicate_risk_score
        candidate.foreign_worker_relevance_score = evaluation.foreign_worker_relevance_score
        candidate.korea_relevance_score = evaluation.korea_relevance_score
        candidate.visa_or_labor_policy_score = evaluation.visa_or_labor_policy_score
        candidate.freshness_score = evaluation.freshness_score
        candidate.source_reliability_score = evaluation.source_reliability_score
        candidate.facebook_post_suitability_score = evaluation.facebook_post_suitability_score
        candidate.settlement_relevance_score = evaluation.settlement_relevance_score
        candidate.practical_value_score = evaluation.practical_value_score
        candidate.content_potential_score = evaluation.content_potential_score
        candidate.is_sensitive = evaluation.is_sensitive
        candidate.review_required_reason = evaluation.review_required_reason
        candidate.score_threshold = evaluation.threshold
        candidate.score_breakdown_json = evaluation.score_breakdown_json
        candidate.risk_level = "HIGH" if evaluation.duplicate_risk_score >= 0.85 else candidate.risk_level or "LOW"
        return candidate

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
        self.repair_recent_missing_url_candidates(minimum_safe_score=minimum_safe_score, dry_run=dry_run)

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
            publish_results.append({"status": "WAITING_COOLDOWN", "facebook_status": "WAITING_COOLDOWN", "telegram_status": "SKIPPED", "error_message": no_publish_reason})
        elif not selected_candidates:
            skip_message = no_publish_reason or "게시 가능한 후보가 없습니다."
            self.repository.insert_pipeline_log(
                "facebook_publish",
                "SKIPPED",
                skip_message,
                payload_json=json.dumps(self.selection_log_payload(selection), ensure_ascii=False),
            )
            if os.getenv("NEWS_NOTIFY_NO_PUBLISH", "false").lower() in {"1", "true", "yes", "on"}:
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

    def collect_single_keyword_legacy(self, keyword: str, allow_seed: bool = False) -> list[NewsItem]:
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

    def collect(self, keyword: str, allow_seed: bool = False) -> list[NewsItem]:
        items: list[NewsItem] = []
        search_terms = collector_search_keywords(keyword) if uses_default_news_collectors(self.collectors) else [(keyword, keyword_category_hint(keyword))]
        per_query_limit = max(1, min(int(os.getenv("NEWS_COLLECTOR_LIMIT_PER_QUERY", "5") or "5"), 20))
        self.repository.insert_pipeline_log(
            "collect",
            "STARTED",
            f"category search keywords: {len(search_terms)} terms / {', '.join(term for term, _category in search_terms[:8])}",
        )
        for search_keyword, category_hint in search_terms:
            for collector in self.collectors:
                try:
                    self.repository.insert_pipeline_log(
                        "collect",
                        "STARTED",
                        f"{collector.__class__.__name__} collect start: {search_keyword} / {category_hint}",
                    )
                    collected = collect_with_optional_limit(collector, search_keyword, per_query_limit)
                    english_items = []
                    for index, item in enumerate(collected, start=1):
                        if is_english_article(item):
                            item.language = "en"
                            item.keyword = search_keyword
                            if not item.category or item.category == "foreign_jobs":
                                item.category = category_hint
                            english_items.append(item)
                            self.repository.insert_pipeline_log("collect", "COMPLETED", f"{collector.__class__.__name__} English article {index}: {item.title[:120]}")
                        else:
                            self.repository.insert_pipeline_log("collect", "SKIPPED", f"{collector.__class__.__name__} non-English article {index}: {item.title[:120]}")
                    items.extend(english_items)
                    self.repository.insert_pipeline_log(
                        "collect",
                        "COMPLETED",
                        f"{collector.__class__.__name__} completed: keyword '{search_keyword}', total {len(collected)}, English {len(english_items)}",
                    )
                except Exception as exc:
                    self.repository.insert_pipeline_log("collect", "FAILED", f"{collector.__class__.__name__} failed for '{search_keyword}': {str(exc)[:180]}")
        if items:
            return items
        self.repository.insert_pipeline_log("collect", "SKIPPED", "No English article collected for this cycle.")
        return self._dry_run_seed_items(keyword) if allow_seed and os.getenv("NEWS_DRY_RUN_USE_SEED", "").lower() in {"1", "true", "yes"} else []

    def save_normalized(self, item: NewsItem, keyword: str) -> NewsCandidate:
        candidate = normalize_news_item(NewsCandidate.from_item(item))
        candidate.keyword = item.keyword or keyword
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
        candidate = self.recover_article_source(candidate)
        validation_error = self.validate_text(candidate)
        if validation_error:
            candidate.status = "TEXT_INVALID"
            candidate.publish_status = "TEXT_INVALID"
            candidate.fail_reason = validation_error
            candidate.skip_reason = validation_error
            self.repository.insert_pipeline_log("text_validation", "FAILED", f"텍스트 검증 실패: {validation_error} / {candidate.title}", candidate.id)
            return self.repository.update_candidate(candidate)

        summary = self.summarizer.summarize(candidate)
        if not dry_run and not summary.short_summary:
            candidate.status = "FAILED_RETRYABLE"
            candidate.publish_status = "FAILED_RETRYABLE"
            candidate.fail_reason = "Local LLaMA 요약 응답 실패 또는 시간 초과로 게시 중단"
            self.repository.insert_pipeline_log("llama_summary", "FAILED_RETRYABLE", candidate.fail_reason, candidate.id)
            self.telegram_notifier.notify_failure(candidate, candidate.fail_reason, dry_run=False)
            return self.repository.update_candidate(candidate)
        if summary.risk_notes.startswith("Rule-based summary"):
            self.repository.insert_pipeline_log("llama_summary", "FALLBACK", f"Local LLaMA summary unavailable; rule-based fallback used: {candidate.title}", candidate.id)

        candidate.short_summary = summary.short_summary
        candidate.key_points = "\n".join(summary.key_points[:3])
        candidate.relevance_reason = summary.relevance_reason
        candidate.risk_notes = summary.risk_notes
        candidate.generated_title = summary.generated_title or candidate.title
        candidate.generated_summary_en = summary.generated_summary_en
        candidate.generated_why_it_matters_en = summary.generated_why_it_matters_en
        candidate.fail_reason = ""
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
            candidate.is_representative = False
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
        candidate.settlement_relevance_score = evaluation.settlement_relevance_score
        candidate.practical_value_score = evaluation.practical_value_score
        candidate.content_potential_score = evaluation.content_potential_score
        candidate.is_sensitive = evaluation.is_sensitive
        candidate.review_required_reason = evaluation.review_required_reason
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

    def recover_article_source(self, candidate: NewsCandidate) -> NewsCandidate:
        if candidate.source_url and candidate.content:
            return candidate

        source_url = candidate.source_url.strip()
        recovery_source = ""
        if not source_url:
            source_url = self.repository.find_existing_article_url(candidate)
            if source_url:
                recovery_source = "existing_article_url"

        if not source_url and candidate.google_news_url:
            resolved_url = resolve_google_news_url(candidate.google_news_url, timeout=10)
            if is_acceptable_source_url(resolved_url):
                source_url = resolved_url
                recovery_source = "google_news_resolver"

        if not source_url:
            guessed_url = guess_article_url_from_source(candidate)
            if guessed_url:
                source_url = guessed_url
                recovery_source = "source_title_guess"

        if source_url:
            candidate.source_url = source_url
            candidate.canonical_url = candidate.canonical_url or source_url
            if "URL" in (candidate.fail_reason or "") or "원문" in (candidate.fail_reason or ""):
                candidate.fail_reason = ""
            if "URL" in (candidate.skip_reason or "") or "원문" in (candidate.skip_reason or ""):
                candidate.skip_reason = ""

        content_status = "FETCHED" if candidate.content else "URL_MISSING"
        content_error = ""
        if candidate.source_url and (not candidate.content or len(candidate.content) < 200):
            try:
                metadata = fetch_article_metadata(candidate.source_url, timeout=12)
                if metadata.canonical_url and is_acceptable_source_url(metadata.canonical_url):
                    candidate.source_url = metadata.canonical_url
                    candidate.canonical_url = metadata.canonical_url
                if metadata.content:
                    candidate.content = metadata.content
                    content_status = "FETCHED" if len(metadata.content) >= 120 else "PARTIAL"
                else:
                    content_status = "FAILED"
                    content_error = "content empty"
                if metadata.image_url:
                    candidate.image_url = metadata.image_url
                if metadata.image_urls:
                    candidate.image_urls = metadata.image_urls
                if metadata.publisher_name:
                    candidate.publisher_name = metadata.publisher_name
            except Exception as exc:
                content_status = "FAILED"
                content_error = str(exc)[:300]

        if candidate.source_url or content_error or content_status != "URL_MISSING":
            if hasattr(self.repository, "update_article_recovery"):
                self.repository.update_article_recovery(candidate, content_status, content_error)
            else:
                self.repository.update_candidate(candidate)
            if recovery_source:
                self.repository.insert_pipeline_log(
                    "article_recovery",
                    "COMPLETED",
                    f"source recovered from {recovery_source}: {candidate.source_url}",
                    candidate.id,
                )
            elif content_status in {"FETCHED", "PARTIAL"}:
                self.repository.insert_pipeline_log("article_recovery", "COMPLETED", "article content refreshed", candidate.id)
            elif content_error:
                self.repository.insert_pipeline_log("article_recovery", "FAILED", content_error, candidate.id)
        return candidate

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
        relevance_terms = (
            "foreign worker", "migrant", "visa", "korea", "e-9", "e-7", "employment", "labor", "immigration",
            "foreigners in korea", "foreign residents", "living in korea", "housing", "bank", "health insurance",
            "transportation", "korean language", "cost of living", "support center", "settlement", "safety",
        )
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

        recent_pool = [candidate for candidate in today_ready if candidate_seen_at(candidate) >= recent_cutoff]
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
            for candidate in sorted(today_ready, key=lambda item: (item.evaluation_score, candidate_seen_at(item)), reverse=True)
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
                parse_iso(item["seen_at"]),
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
                payload_json=selection_payload_extra(
                    {
                        "target_category_group": target,
                        "selected_category": selected.content_category,
                        "primary_candidate_count": len(pools["PRIMARY"]),
                        "secondary_candidate_count": len(pools["SECONDARY"]),
                        "tertiary_candidate_count": len(pools["TERTIARY"]),
                        "recent_24h_category_ratio": recent_counts,
                        "category_selection_reason": selected.category_selection_reason,
                        "fallback_used": fallback_used,
                    }
                ),
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
        window_start = self.publish_window_start(now)
        window_start_iso = window_start.isoformat()
        recent_cutoff = now - timedelta(hours=1)
        window_candidates = (
            self.repository.list_publish_candidates_since(window_start_iso, limit=1000)
            if hasattr(self.repository, "list_publish_candidates_since")
            else self.repository.list_candidates()
        )
        queue_candidates = (
            self.repository.list_publish_queue(limit=1000)
            if hasattr(self.repository, "list_publish_queue")
            else self.repository.list_ready_for_cycle(cycle_id, limit=1000)
        )
        candidate_map = {candidate.id: candidate for candidate in queue_candidates if candidate.id is not None}
        candidate_map.update({candidate.id: candidate for candidate in window_candidates if candidate.id is not None})
        all_candidates = list(candidate_map.values())
        today_all_candidates = [
            candidate
            for candidate in self.repository.list_candidates()
            if candidate_seen_at(candidate) >= window_start or candidate.id in candidate_map
        ]
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

        recent_pool = [candidate for candidate in prepared_candidates if candidate_seen_at(candidate) >= recent_cutoff]
        recent_ids = {candidate.id for candidate in recent_pool}
        facebook_posts = self.fetch_facebook_engagement_samples()
        selected_score = None
        selected = None
        selected_from_status = ""
        publishable: list[dict] = []

        recent_published = self.repository.list_recent_published(limit=50)
        recent_24h_published = [candidate for candidate in recent_published if now - parse_iso(candidate.published_at or candidate.collected_at) <= timedelta(hours=24)]
        recent_counts = recent_category_ratio(recent_24h_published)
        last_group = ""
        if recent_published:
            last_group = recent_published[0].content_priority_group or category_group(recent_published[0].content_category or recent_published[0].category)

        scored = [
            self.score_publish_candidate(
                candidate,
                now=now,
                today_avg_score=today_avg_score,
                recent_ids=recent_ids,
                facebook_posts=facebook_posts,
                recent_category_counts=recent_counts,
                last_category_group=last_group,
            )
            for candidate in prepared_candidates
        ]
        safe_scored = [item for item in scored if not item["blocked"]]
        pools = {
            "PRIMARY": [item for item in safe_scored if item["priority_group"] == "PRIMARY"],
            "SECONDARY": [item for item in safe_scored if item["priority_group"] == "SECONDARY"],
            "TERTIARY": [item for item in safe_scored if item["priority_group"] == "TERTIARY"],
        }
        target, category_reason = target_group(len(pools["PRIMARY"]), len(pools["SECONDARY"]), recent_counts, last_group)
        fallback_used = False
        for group in [target] + [item for item in ("PRIMARY", "SECONDARY", "TERTIARY") if item != target]:
            for relaxed in (False, True):
                threshold = group_threshold(group, relaxed=relaxed)
                publishable = [
                    item
                    for item in pools[group]
                    if item["base_score"] >= self.minimum_publish_score() or item["final_score"] >= threshold
                ]
                publishable.sort(
                    key=lambda item: (
                        item["final_score"],
                        item["category_rotation_score"],
                        1 if item["is_recent"] else 0,
                        item["base_score"],
                        parse_iso(item["seen_at"]),
                    ),
                    reverse=True,
                )
                if publishable:
                    selected_score = publishable[0]
                    selected = selected_score["candidate"]
                    threshold_used = threshold
                    fallback_used = group != target or relaxed
                    break
            if selected:
                break

        if not selected:
            publishable = [
                item
                for item in safe_scored
                if item["base_score"] >= self.minimum_publish_score()
                or item["final_score"] >= GROUP_THRESHOLDS.get(item["priority_group"], GROUP_THRESHOLDS["PRIMARY"])["floor"]
            ]
            publishable.sort(key=lambda item: (item["final_score"], item["base_score"], parse_iso(item["seen_at"])), reverse=True)
            if publishable:
                selected_score = publishable[0]
                selected = selected_score["candidate"]
                threshold_used = GROUP_THRESHOLDS.get(selected_score["priority_group"], GROUP_THRESHOLDS["PRIMARY"])["floor"]
                fallback_used = True

        if selected:
            selected_from_status = selected.publish_status or selected.status
            if selected.publish_status != "READY_TO_PUBLISH" or selected.status != "READY_TO_PUBLISH":
                promoted_to_ready = True
                selected.status = "READY_TO_PUBLISH"
                selected.publish_status = "READY_TO_PUBLISH"
                selected.score_threshold = threshold_used
                selected.selection_reason = selected.selection_reason or f"게시 후보 재평가에서 threshold {threshold_used:.0f}점 기준을 통과했습니다."
                selected.category_rotation_score = selected_score.get("category_rotation_score", 0)
                selected.category_selection_reason = selected_score.get("category_selection_reason", category_reason)
                selected.selection_reason = (
                    f"{selected.category_selection_reason} "
                    f"{selected.content_priority_group}/{selected.content_category} 후보가 threshold {threshold_used:.0f}점을 통과했습니다."
                )
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
                best = max((item["final_score"] for item in safe_scored), default=max(publishable_scores, default=0.0))
                no_publish_reason = (
                    f"오늘 기사 {today_article_count}건을 재평가했지만 자동 게시 기준을 통과한 안전 후보가 없습니다. "
                    f"최고 최종 점수: {best:.0f}점"
                )

        remaining_ready_count = max(0, len([candidate for candidate in prepared_candidates if candidate.publish_status == "READY_TO_PUBLISH"]) - (1 if selected else 0))
        final_top = publishable[:10] if publishable else []
        effective_minimum_safe_score = min(self.minimum_publish_score(), threshold_used) if selected else self.minimum_publish_score()
        return {
            "cycle_id": cycle_id,
            "publish_window_start": window_start_iso,
            "ready_count": len(ready_candidates),
            "retryable_count": len(retryable_candidates),
            "recent_pool_count": len(recent_pool),
            "backlog_pool_count": max(0, len(prepared_candidates) - len(recent_pool)),
            "candidate_pool_count": len(prepared_candidates),
            "expanded_candidate_count": len(expanded_candidates),
            "today_article_count": today_article_count,
            "today_unposted_count": today_unposted_count,
            "today_avg_score": today_avg_score,
            "minimum_safe_score": effective_minimum_safe_score,
            "threshold_used": threshold_used,
            "threshold_sequence": [{"label": group, "threshold": group_threshold(group, relaxed=False), "relaxed_threshold": group_threshold(group, relaxed=True)} for group in ("PRIMARY", "SECONDARY", "TERTIARY")],
            "target_category_group": target,
            "selected_category": selected.content_category if selected else "",
            "primary_candidate_count": len(pools["PRIMARY"]),
            "secondary_candidate_count": len(pools["SECONDARY"]),
            "tertiary_candidate_count": len(pools["TERTIARY"]),
            "recent_24h_category_ratio": recent_counts,
            "category_selection_reason": selected.category_selection_reason if selected else category_reason,
            "selected_candidate": selected,
            "selected_score": selected_score,
            "selected_from_status": selected_from_status,
            "publish_attempted": False,
            "publish_result": "SKIPPED",
            "no_publish_code": no_publish_code,
            "no_publish_reason": no_publish_reason,
            "remaining_ready_count": remaining_ready_count,
            "fallback_used": fallback_used or bool(expanded_candidates),
            "promoted_to_ready": promoted_to_ready,
            "cooldown_remaining": 0,
            "dry_run_evaluation": {
                "ready_count": len(ready_candidates),
                "publish_window_start": window_start_iso,
                "retryable_count": len(retryable_candidates),
                "expanded_candidate_count": len(expanded_candidates),
                "today_article_count": today_article_count,
                "today_unposted_count": today_unposted_count,
                "minimum_safe_score": effective_minimum_safe_score,
                "threshold_used": threshold_used,
                "target_category_group": target,
                "primary_candidate_count": len(pools["PRIMARY"]),
                "secondary_candidate_count": len(pools["SECONDARY"]),
                "tertiary_candidate_count": len(pools["TERTIARY"]),
                "recent_24h_category_ratio": recent_counts,
                "category_selection_reason": selected.category_selection_reason if selected else category_reason,
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
            if not candidate.content_priority_group or not candidate.content_category:
                evaluation = self.evaluator.evaluate(candidate, threshold=max(40.0, float(candidate.score_threshold or 40.0)))
                self.apply_evaluation(candidate, evaluation)
                if not dry_run:
                    self.repository.update_candidate(candidate)
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
                candidate.settlement_relevance_score = evaluation.settlement_relevance_score
                candidate.practical_value_score = evaluation.practical_value_score
                candidate.content_potential_score = evaluation.content_potential_score
                candidate.is_sensitive = evaluation.is_sensitive
                candidate.review_required_reason = evaluation.review_required_reason
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
        window_start = self.publish_window_start()
        window_start_iso = window_start.isoformat()
        ready_candidates = self.repository.list_publish_queue(limit=500)
        window_candidates = self.repository.list_publish_candidates_since(window_start_iso, limit=1000)
        candidate_map = {candidate.id: candidate for candidate in ready_candidates if candidate.id is not None}
        candidate_map.update({candidate.id: candidate for candidate in window_candidates if candidate.id is not None})
        candidate_pool = list(candidate_map.values())
        remaining = int(cooldown.get("remaining_seconds", 0) or 0)
        cooldown_minutes = int(cooldown.get("cooldown_minutes") or self.publish_cooldown_minutes())
        return {
            "cycle_id": cycle_id,
            "publish_window_start": window_start_iso,
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
                f"Facebook 게시 대기: 마지막 게시 후 {cooldown_minutes}분 쿨다운 적용 중입니다. "
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
                candidate.settlement_relevance_score = evaluation.settlement_relevance_score
                candidate.practical_value_score = evaluation.practical_value_score
                candidate.content_potential_score = evaluation.content_potential_score
                candidate.is_sensitive = evaluation.is_sensitive
                candidate.review_required_reason = evaluation.review_required_reason
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

    def required_publish_safety_error(self, candidate: NewsCandidate, now: datetime | None = None) -> str:
        now = now or datetime.now(timezone.utc)
        if not candidate.title.strip():
            return "Title is missing."
        if not candidate.source_url.strip():
            return "Article URL is missing."
        if candidate.status in {"DUPLICATE", "TEXT_INVALID", "REVIEW_REQUIRED", "POSTED", "PUBLISHED", "NOTIFIED", "POST_EXPIRED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}:
            return f"Excluded status: {candidate.status}"
        if candidate.publish_status in {"DUPLICATE", "TEXT_INVALID", "REVIEW_REQUIRED", "POSTED", "PUBLISHED", "NOTIFIED", "POST_EXPIRED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}:
            return f"Excluded publish status: {candidate.publish_status}"
        if candidate.risk_level == "HIGH":
            return "High-risk candidate."
        if candidate.is_sensitive:
            return candidate.review_required_reason or "Sensitive article requires manual review."
        if candidate_seen_at(candidate) < self.publish_window_start(now):
            return "Candidate is outside the rolling 24-hour publishing window."
        text = f"{candidate.title} {candidate.summary} {candidate.content} {candidate.short_summary} {candidate.relevance_reason}".lower()
        generated_text = f"{candidate.generated_summary_en} {candidate.generated_why_it_matters_en}"
        if has_korean_text(generated_text, max_hangul_chars=6):
            return "Generated Facebook message contains Korean text."
        if any(term in text for term in NEGATIVE_INCIDENT_TERMS):
            return "Negative incident/crime article."
        practical_life_candidate = (
            candidate.content_priority_group in {"SECONDARY", "TERTIARY"}
            and candidate.settlement_relevance_score >= 0.25
            and candidate.practical_value_score >= 0.15
        )
        if not practical_life_candidate and not any(term in text for term in ("foreign worker", "migrant", "visa", "korea", "employment", "labor", "immigration", "e-9", "e-7")):
            return "Not directly related to foreign workers, visas, jobs, or labor in Korea."
        if any(term in text for term in ("casino", "coupon", "lottery", "click here", "advertorial")):
            return "Advertising or spam-like text."
        return ""

    def score_publish_candidate(
        self,
        candidate: NewsCandidate,
        now: datetime,
        today_avg_score: float,
        recent_ids: set[int | None],
        facebook_posts: list[dict],
        recent_category_counts: dict[str, int] | None = None,
        last_category_group: str = "",
    ) -> dict:
        base_score = float(candidate.evaluation_score or 0.0)
        is_recent = candidate.id in recent_ids or now - candidate_seen_at(candidate) <= timedelta(hours=1)
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
        safety_error = self.required_publish_safety_error(candidate, now)
        priority_group = candidate.content_priority_group or category_group(candidate.content_category or candidate.category)
        category_bonus = rotation_score(candidate, recent_category_counts or {}, last_category_group)
        candidate.category_rotation_score = category_bonus
        if not candidate.category_selection_reason:
            candidate.category_selection_reason = f"{priority_group} category rotation score {category_bonus:+.0f} applied."
        final_score = base_score + freshness_score + backlog_bonus + engagement_score + group_signal_score + category_bonus - duplication_penalty - risk_penalty
        blocked = bool(safety_error) or candidate.risk_level == "HIGH" or not candidate.source_url or duplication_penalty >= 30.0
        return {
            "candidate": candidate,
            "id": candidate.id,
            "title": candidate.title,
            "collected_at": candidate.collected_at,
            "seen_at": candidate_seen_at(candidate).isoformat(),
            "base_score": round(base_score, 2),
            "freshness_score": round(freshness_score, 2),
            "backlog_above_average_bonus": round(backlog_bonus, 2),
            "engagement_prediction_score": round(engagement_score, 2),
            "group_signal_score": round(group_signal_score, 2),
            "duplication_penalty": round(duplication_penalty, 2),
            "risk_penalty": round(risk_penalty, 2),
            "category_rotation_score": round(category_bonus, 2),
            "category_selection_reason": candidate.category_selection_reason,
            "content_category": candidate.content_category or candidate.category,
            "priority_group": priority_group,
            "final_score": round(final_score, 2),
            "is_recent": is_recent,
            "blocked": blocked,
            "blocked_reason": safety_error,
            "breakdown": {
                "base_score": round(base_score, 2),
                "freshness_score": round(freshness_score, 2),
                "backlog_above_average_bonus": round(backlog_bonus, 2),
                "engagement_prediction_score": round(engagement_score, 2),
                "group_signal_score": round(group_signal_score, 2),
                "duplication_penalty": round(duplication_penalty, 2),
                "risk_penalty": round(risk_penalty, 2),
                "category_rotation_score": round(category_bonus, 2),
                "content_category": candidate.content_category or candidate.category,
                "priority_group": priority_group,
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
            "category_rotation_score": score.get("category_rotation_score", 0),
            "content_category": score.get("content_category", ""),
            "priority_group": score.get("priority_group", ""),
            "final_score": score["final_score"],
            "collected_at": score["collected_at"],
        }

    def fetch_facebook_engagement_samples(self) -> list[dict]:
        token_selection = get_facebook_page_token(allow_refresh=True)
        page_id = token_selection.page_id or os.getenv("FACEBOOK_PAGE_ID", "").strip()
        access_token = token_selection.access_token
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
        error_category = publish_result.get("error_category", "")
        error_context = publish_result.get("error_context") or {}
        retryable_yn = bool(publish_result.get("retryable_yn", status == "FAILED_RETRYABLE"))
        message_preview = publish_result.get("message", "")[:1000]
        token_debug = publish_result.get("token_debug") or {}
        token_status = publish_result.get("token_status") or {}
        request_payload = publish_result.get("request_payload") or {}
        if token_debug:
            self.repository.insert_pipeline_log(
                "facebook_token_debug",
                "COMPLETED" if token_debug.get("is_valid") else "FAILED",
                (
                    f"Facebook token debug: type={token_debug.get('token_type') or '-'}, "
                    f"is_valid={token_debug.get('is_valid')}, "
                    f"profile_id={token_debug.get('profile_id') or '-'}, "
                    f"fingerprint={token_debug.get('token_fingerprint') or '-'}, "
                    f"token={token_debug.get('token_masked') or '-'}, "
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
            response_body=json.dumps(
                {
                    "facebook_response": publish_result.get("response_body", ""),
                    "error_category": error_category,
                    "error_context": error_context,
                    "meta_error": error_context.get("meta_error", {}),
                    "token_debug": token_debug,
                    "token_status": token_status,
                    "retryable_yn": retryable_yn,
                    "facebook_link_url": publish_result.get("facebook_link_url", ""),
                    "link_valid_yn": publish_result.get("link_valid_yn", False),
                    "link_reject_reason": publish_result.get("link_reject_reason", ""),
                    "facebook_debugger_url": request_payload.get("facebook_debugger_url", ""),
                },
                ensure_ascii=False,
            ),
            error_code=error_code,
            error_message=error_message,
            published_at=timestamp,
            request_payload=json.dumps(request_payload, ensure_ascii=False),
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
            manual_repost_issue = error_category in {
                "TOKEN_INVALID",
                "TOKEN_EXPIRED",
                "TOKEN_PERMISSION_MISSING",
                "TOKEN_WRONG_TYPE",
                "TOKEN_PAGE_MISMATCH",
                "INTERNAL_ENV_MISSING",
            } or error_code in {
                "FACEBOOK_TOKEN_EXPIRED",
                "FACEBOOK_TOKEN_INVALID",
                "FACEBOOK_PAGE_TOKEN_MISMATCH",
                "FACEBOOK_PERMISSION_ERROR",
                "FACEBOOK_PERMISSION_MISSING",
                "FACEBOOK_TOKEN_OR_PERMISSION_ERROR",
                "MISSING_FACEBOOK_ENV",
                "MISSING_FACEBOOK_APP_TOKEN",
            }
            next_status = "FAILED_RETRYABLE" if retryable_yn else "FAILED_PERMISSION" if manual_repost_issue else "AUTO_RETRY_BLOCKED" if candidate.publish_attempt_count >= 3 else "FAILED_RETRYABLE"
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
                token_alert = self.telegram_notifier.notify_facebook_error(candidate, error_message, next_status, dry_run=dry_run, publish_result=publish_result)
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
            publish_result=publish_result,
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
            "error_category": error_category,
            "error_context": error_context,
            "retryable_yn": retryable_yn,
        }

    def expire_old_unposted_candidates(self, cycle_id: str = "") -> None:
        if not hasattr(self.repository, "restore_auto_expired_unposted"):
            return
        restored = self.repository.restore_auto_expired_unposted()
        if restored:
            self.repository.insert_pipeline_log(
                "rolling_queue",
                "COMPLETED",
                f"자동 만료 처리된 미게시 후보 {restored}건을 READY_TO_PUBLISH로 복구",
                payload_json=json.dumps({"restored_count": restored, "cycle_id": cycle_id}, ensure_ascii=False),
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
        cutoff = self.publish_window_start()
        restored = 0
        for candidate in self.repository.list_candidates():
            if candidate.status != "SKIPPED":
                continue
            skip_reason = candidate.skip_reason or ""
            recoverable_reason = (
                skip_reason.startswith("게시 기준")
                or "rolling 24-hour publishing window" in skip_reason
                or "posting criteria" in skip_reason
                or "Below minimum safety score" in skip_reason
            )
            if not recoverable_reason:
                continue
            if candidate.evaluation_score < minimum_safe_score:
                continue
            if candidate_seen_at(candidate) < cutoff:
                continue
            candidate.status = "READY_TO_PUBLISH"
            candidate.publish_status = "READY_TO_PUBLISH"
            candidate.post_expired = False
            candidate.skip_reason = ""
            candidate.selection_reason = f"rolling 24시간 게시 기준 적용: 최소 안전 점수 {minimum_safe_score:.0f}점 이상 후보를 대기열로 복구"
            self.repository.update_candidate(candidate)
            restored += 1
        if restored:
            self.repository.insert_pipeline_log("rolling_queue", "COMPLETED", f"최근 24시간 SKIPPED 후보 {restored}건을 READY_TO_PUBLISH 대기열로 복구")

    def repair_recent_missing_url_candidates(self, minimum_safe_score: float, dry_run: bool = False) -> None:
        cutoff = self.publish_window_start()
        repaired = 0
        for candidate in self.repository.list_candidates():
            if candidate_seen_at(candidate) < cutoff:
                continue
            if candidate.published_at or candidate.facebook_post_url:
                continue
            if candidate.status in {"POSTED", "PUBLISHED", "NOTIFIED", "DRY_RUN_PUBLISHED", "DRY_RUN_NOTIFIED", "ARCHIVED", "AUTO_RETRY_BLOCKED"}:
                continue
            if candidate.source_url:
                continue
            reason_text = f"{candidate.skip_reason} {candidate.fail_reason}".lower()
            if "url" not in reason_text and "링크" not in reason_text and "원문" not in reason_text:
                continue
            candidate = self.recover_article_source(candidate)
            if self.validate_text(candidate):
                continue
            evaluation = self.evaluator.evaluate(candidate, threshold=minimum_safe_score)
            candidate.evaluation_score = evaluation.total_score
            candidate.duplicate_risk_score = evaluation.duplicate_risk_score
            candidate.foreign_worker_relevance_score = evaluation.foreign_worker_relevance_score
            candidate.korea_relevance_score = evaluation.korea_relevance_score
            candidate.visa_or_labor_policy_score = evaluation.visa_or_labor_policy_score
            candidate.freshness_score = evaluation.freshness_score
            candidate.source_reliability_score = evaluation.source_reliability_score
            candidate.facebook_post_suitability_score = evaluation.facebook_post_suitability_score
            candidate.settlement_relevance_score = evaluation.settlement_relevance_score
            candidate.practical_value_score = evaluation.practical_value_score
            candidate.content_potential_score = evaluation.content_potential_score
            candidate.is_sensitive = evaluation.is_sensitive
            candidate.review_required_reason = evaluation.review_required_reason
            candidate.score_threshold = evaluation.threshold
            candidate.score_breakdown_json = evaluation.score_breakdown_json
            candidate.risk_level = "HIGH" if evaluation.duplicate_risk_score >= 0.85 else "LOW"
            if evaluation.decision == "READY_TO_PUBLISH":
                candidate.status = "READY_TO_PUBLISH"
                candidate.publish_status = "READY_TO_PUBLISH"
                candidate.post_expired = False
                candidate.skip_reason = ""
                candidate.fail_reason = ""
                candidate.selection_reason = evaluation.reason
                repaired += 1
            else:
                candidate.status = "SKIPPED"
                candidate.publish_status = "SKIPPED"
                candidate.skip_reason = evaluation.reason
            if not dry_run:
                self.repository.update_candidate(candidate)
        if repaired:
            self.repository.insert_pipeline_log("article_recovery", "COMPLETED", f"최근 24시간 원문 URL 누락 후보 {repaired}건을 대기열로 복구")

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

    def publish_cooldown_minutes(self) -> int:
        return int(env_float("NEWS_PUBLISH_COOLDOWN_MINUTES", 30.0, 5.0, 180.0))

    def publish_window_start(self, now: datetime | None = None) -> datetime:
        current = now or datetime.now(timezone.utc)
        return current - timedelta(hours=self.unposted_expire_hours())

    def is_publish_cooldown_active(self) -> bool:
        return self.publish_cooldown_info()["active"]

    def publish_cooldown_info(self) -> dict:
        last = self.repository.last_successful_facebook_publish_at()
        cooldown_minutes = self.publish_cooldown_minutes()
        if not last:
            return {
                "active": False,
                "cooldown_minutes": cooldown_minutes,
                "last_post_at": "",
                "next_publish_at": "",
                "remaining_seconds": 0,
                "remaining_minutes": 0,
            }
        last_at = parse_iso(last)
        next_at = last_at + timedelta(minutes=cooldown_minutes)
        remaining = max(0, int((next_at - datetime.now(timezone.utc)).total_seconds()))
        return {
            "active": remaining > 0,
            "cooldown_minutes": cooldown_minutes,
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
            f"최근 게시 기준 24시간 평균 점수: {threshold:.0f}",
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


def candidate_seen_at(candidate: NewsCandidate) -> datetime:
    return parse_iso(candidate.last_seen_at or candidate.collected_at)


def collector_search_keywords(default_keyword: str) -> list[tuple[str, str]]:
    configured = [
        item.strip()
        for item in os.getenv("NEWS_COLLECTOR_SEARCH_KEYWORDS", "").split("|")
        if item.strip()
    ]
    if configured:
        terms = [(item, keyword_category_hint(item)) for item in configured]
    elif os.getenv("NEWS_COLLECTOR_MULTI_KEYWORD_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}:
        primary_limit = max(1, min(int(os.getenv("NEWS_COLLECTOR_PRIMARY_KEYWORDS", "3") or "3"), len(SEARCH_KEYWORDS["PRIMARY"])))
        secondary_limit = max(1, min(int(os.getenv("NEWS_COLLECTOR_SECONDARY_KEYWORDS", "3") or "3"), len(SEARCH_KEYWORDS["SECONDARY"])))
        tertiary_limit = max(0, min(int(os.getenv("NEWS_COLLECTOR_TERTIARY_KEYWORDS", "2") or "2"), len(SEARCH_KEYWORDS["TERTIARY"])))
        raw_terms: list[str] = [default_keyword]
        raw_terms.extend(SEARCH_KEYWORDS["PRIMARY"][:primary_limit])
        raw_terms.extend(SEARCH_KEYWORDS["SECONDARY"][:secondary_limit])
        raw_terms.extend(SEARCH_KEYWORDS["TERTIARY"][:tertiary_limit])
        terms = [(item, keyword_category_hint(item)) for item in raw_terms if item.strip()]
    else:
        terms = [(default_keyword, keyword_category_hint(default_keyword))]

    deduped: list[tuple[str, str]] = []
    seen: set[str] = set()
    max_terms = max(1, min(int(os.getenv("NEWS_COLLECTOR_MAX_SEARCH_TERMS", "9") or "9"), 30))
    for term, category in terms:
        key = term.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append((term.strip(), category))
        if len(deduped) >= max_terms:
            break
    return deduped


def collect_with_optional_limit(collector, keyword: str, limit: int) -> list[NewsItem]:
    try:
        return collector.collect(keyword, limit=limit)
    except TypeError as exc:
        if "limit" not in str(exc):
            raise
        return collector.collect(keyword)


def uses_default_news_collectors(collectors: list) -> bool:
    default_names = {"NaverNewsCollector", "GoogleNewsCollector", "RSSNewsCollector"}
    return all(collector.__class__.__name__ in default_names for collector in collectors)


def keyword_category_hint(keyword: str) -> str:
    text = (keyword or "").lower()
    if any(token in text for token in ("housing", "rent", "bank", "health", "transport", "cost of living", "language", "support center", "living guide")):
        if "housing" in text or "rent" in text:
            return "housing"
        if "bank" in text:
            return "banking"
        if "health" in text:
            return "healthcare"
        if "transport" in text:
            return "transportation"
        if "language" in text:
            return "korean_language"
        if "cost of living" in text:
            return "cost_of_living"
        return "settlement_life"
    if any(token in text for token in ("travel", "culture", "expat", "local life", "living in seoul", "living in busan")):
        if "travel" in text:
            return "travel"
        if "culture" in text:
            return "culture"
        return "lifestyle"
    if "visa" in text or "e-9" in text or "e-7" in text:
        return "work_visa"
    if "immigration" in text:
        return "immigration"
    if "labor rights" in text or "migrant workers" in text:
        return "labor_rights"
    if "employment" in text or "skilled worker" in text:
        return "employment_policy"
    return "foreign_jobs"


def is_english_article(item: NewsItem) -> bool:
    text = f"{item.title} {item.summary} {item.content}"
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return False
    ascii_letters = sum(1 for char in letters if "a" <= char.lower() <= "z")
    hangul = sum(1 for char in text if "\uac00" <= char <= "\ud7a3")
    return ascii_letters / max(len(letters), 1) >= 0.65 and hangul <= 3


def guess_article_url_from_source(candidate: NewsCandidate) -> str:
    source = f"{candidate.source_name} {candidate.publisher_name} {candidate.source_type}".lower()
    slug = article_slug(candidate.title)
    if not slug:
        return ""
    if "erickson immigration" in source or "eiglaw" in source:
        return f"https://eiglaw.com/{slug}/"
    return ""


def article_slug(title: str) -> str:
    text = normalize_ascii_slug(title)
    words = [word for word in text.split("-") if word]
    return "-".join(words[:18])


def normalize_ascii_slug(value: str) -> str:
    text = normalize_slug_apostrophe(value).lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-")


def normalize_slug_apostrophe(value: str) -> str:
    return (value or "").replace("’", "").replace("'", "")


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
