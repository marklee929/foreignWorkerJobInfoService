from __future__ import annotations

import os
import unittest

from foreign_worker_life_info_collector.social.news.evaluator.candidate_evaluator import CandidateEvaluator
from foreign_worker_life_info_collector.social.news.models import NewsCandidate, NewsItem
from foreign_worker_life_info_collector.social.news.normalizer.news_normalizer import normalize_news_item
from foreign_worker_life_info_collector.social.news.pipeline import NewsPipeline, today_cycle_id


class StaticNewsCollector:
    def collect(self, keyword: str) -> list[NewsItem]:
        return [
            NewsItem(
                title="Korea expands foreign worker visa support program",
                url="https://example.com/news/visa-support",
                source="test",
                category="immigration",
                summary="Korea announced visa support for foreign workers seeking stable employment.",
            ),
            NewsItem(
                title="Korea expands foreign worker visa support program",
                url="https://example.com/news/visa-support",
                source="test",
                category="immigration",
                summary="Korea announced visa support for foreign workers seeking stable employment.",
            ),
        ]


class InMemoryNewsRepository:
    def __init__(self) -> None:
        self.candidates: list[NewsCandidate] = []
        self.facebook_logs: list[dict] = []
        self.telegram_logs: list[dict] = []
        self.pipeline_logs: list[dict] = []

    def insert_pipeline_log(self, step: str, status: str, message: str, news_candidate_id: int | None = None, payload_json: str = "", created_at: str = "") -> int:
        row = {
            "id": len(self.pipeline_logs) + 1,
            "news_candidate_id": news_candidate_id,
            "step": step,
            "status": status,
            "message": message,
            "payload_json": payload_json,
            "created_at": created_at,
        }
        self.pipeline_logs.append(row)
        return row["id"]

    def save(self, item: NewsItem) -> NewsCandidate:
        candidate = normalize_news_item(item)
        candidate.id = len(self.candidates) + 1
        candidate.duplicate_group_id = candidate.id
        self.candidates.append(candidate)
        return candidate

    def list_candidates(self) -> list[NewsCandidate]:
        return list(self.candidates)

    def list_recent_published(self, limit: int = 20) -> list[NewsCandidate]:
        return [
            candidate
            for candidate in self.candidates
            if candidate.status in {"POSTED", "PUBLISHED", "NOTIFIED", "DRY_RUN_PUBLISHED", "DRY_RUN_NOTIFIED"}
        ][:limit]

    def list_ready_for_cycle(self, cycle_id: str, limit: int = 500) -> list[NewsCandidate]:
        return [
            candidate
            for candidate in self.candidates
            if candidate.cycle_id == cycle_id
            and candidate.publish_status == "READY_TO_PUBLISH"
            and not candidate.post_expired
            and not candidate.published_at
        ][:limit]

    def list_expandable_for_cycle(self, cycle_id: str, limit: int = 500) -> list[NewsCandidate]:
        allowed = {"COLLECTED", "NORMALIZED", "SUMMARIZED", "SCORED", "SKIPPED", "SKIPPED_LOW_SCORE", "FAILED_RETRYABLE"}
        return [
            candidate
            for candidate in self.candidates
            if candidate.cycle_id == cycle_id
            and (candidate.status in allowed or candidate.publish_status in allowed)
            and not candidate.post_expired
            and not candidate.published_at
        ][:limit]

    def update_candidate(self, candidate: NewsCandidate) -> NewsCandidate:
        for index, item in enumerate(self.candidates):
            if item.id == candidate.id:
                self.candidates[index] = candidate
                return candidate
        self.candidates.append(candidate)
        return candidate

    def mark_status(self, candidate_id: int, status: str, **kwargs) -> None:
        for candidate in self.candidates:
            if candidate.id == candidate_id:
                candidate.status = status
                for key, value in kwargs.items():
                    if value is not None:
                        setattr(candidate, key, value)
                return

    def insert_facebook_log(self, **kwargs) -> int:
        self.facebook_logs.append(kwargs)
        return len(self.facebook_logs)

    def insert_telegram_log(self, **kwargs) -> int:
        self.telegram_logs.append(kwargs)
        return len(self.telegram_logs)

    def last_successful_facebook_publish_at(self) -> str:
        return ""

    def expire_ready_before_cycle(self, new_cycle_id: str, expired_at: str, reason: str = "DAILY_CYCLE_EXPIRED") -> tuple[int, str]:
        return 0, ""


class SocialNewsPipelineTest(unittest.TestCase):
    def test_dry_run_saves_candidates_deduplicates_and_logs_publish(self) -> None:
        repository = InMemoryNewsRepository()
        pipeline = NewsPipeline(repository=repository, collectors=[StaticNewsCollector()])
        result = pipeline.run(keyword="foreign worker visa Korea", dry_run=True)

        self.assertEqual(result["collected_count"], 2)
        self.assertEqual(result["saved"][0]["status"], "READY_TO_PUBLISH")
        self.assertEqual(result["saved"][1]["status"], "DUPLICATE")
        self.assertEqual(len(result["ready_to_publish"]), 1)
        self.assertEqual(result["ready_to_publish"][0]["status"], "READY_TO_PUBLISH")
        self.assertEqual(result["publish_results"][0]["status"], "DRY_RUN_EVALUATED")
        self.assertEqual(result["publish_results"][0]["facebook_status"], "DRY_RUN")
        self.assertEqual([item.status for item in repository.candidates], ["READY_TO_PUBLISH", "DUPLICATE"])
        self.assertEqual(len(repository.facebook_logs), 0)
        self.assertEqual(len(repository.telegram_logs), 0)

    def test_real_mode_without_env_fails_and_logs_result_without_approval(self) -> None:
        old_env = {
            "FACEBOOK_PAGE_ID": os.environ.pop("FACEBOOK_PAGE_ID", None),
            "FACEBOOK_PAGE_ACCESS_TOKEN": os.environ.pop("FACEBOOK_PAGE_ACCESS_TOKEN", None),
            "TELEGRAM_BOT_TOKEN": os.environ.pop("TELEGRAM_BOT_TOKEN", None),
            "TELEGRAM_CHAT_ID": os.environ.pop("TELEGRAM_CHAT_ID", None),
        }
        try:
            repository = InMemoryNewsRepository()
            pipeline = NewsPipeline(repository=repository, collectors=[StaticNewsCollector()])
            result = pipeline.run(keyword="foreign worker visa Korea", dry_run=False)

            self.assertEqual(result["publish_results"][0]["status"], "SKIPPED")
            self.assertEqual(result["publish_results"][0]["facebook_status"], "SKIPPED")
            self.assertEqual([item.status for item in repository.candidates], ["FAILED", "FAILED"])
            self.assertEqual(len(repository.facebook_logs), 0)
        finally:
            for key, value in old_env.items():
                if value is not None:
                    os.environ[key] = value

    def test_korea_specific_visa_news_scores_above_h1b_news(self) -> None:
        evaluator = CandidateEvaluator()
        korea_candidate = normalize_news_item(
            NewsItem(
                title="Korea expands E-9 employment visa support for foreign workers",
                url="https://news.kbs.co.kr/korea-visa",
                source="test",
                summary="The labor ministry announced a Korean employment visa policy for foreign workers.",
            )
        )
        h1b_candidate = normalize_news_item(
            NewsItem(
                title="US H-1B visa lottery changes affect foreign workers",
                url="https://example.com/h1b",
                source="test",
                summary="US immigration policy changes for H-1B applicants.",
            )
        )

        korea_score = evaluator.evaluate(korea_candidate).total_score
        h1b_score = evaluator.evaluate(h1b_candidate).total_score

        self.assertGreater(korea_score, h1b_score)
        self.assertGreater(korea_score, 0.7)

    def test_no_ready_candidate_promotes_safe_fallback_candidate(self) -> None:
        repository = InMemoryNewsRepository()
        candidate = normalize_news_item(
            NewsItem(
                title="Korea foreign worker visa policy update",
                url="https://example.com/news/korea-foreign-worker-visa",
                source="test",
                summary="Korea announced employment visa support for foreign workers and migrant workers.",
            )
        )
        candidate.id = 1
        candidate.cycle_id = today_cycle_id()
        candidate.status = "SKIPPED_LOW_SCORE"
        candidate.publish_status = "SKIPPED_LOW_SCORE"
        candidate.evaluation_score = 42.0
        candidate.risk_level = "LOW"
        repository.candidates.append(candidate)

        pipeline = NewsPipeline(repository=repository, collectors=[])
        pipeline.fetch_facebook_engagement_samples = lambda: []

        selection = pipeline.evaluate_publish_candidates_v2(candidate.cycle_id, dry_run=False)

        self.assertEqual(selection["ready_count"], 0)
        self.assertEqual(selection["expanded_candidate_count"], 1)
        self.assertEqual(selection["minimum_safe_score"], 40.0)
        self.assertTrue(selection["promoted_to_ready"])
        self.assertEqual(selection["selected_candidate"].id, candidate.id)
        self.assertEqual(repository.candidates[0].publish_status, "READY_TO_PUBLISH")


if __name__ == "__main__":
    unittest.main()
