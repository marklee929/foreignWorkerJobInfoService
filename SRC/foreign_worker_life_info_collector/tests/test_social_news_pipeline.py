from __future__ import annotations

import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from foreign_worker_life_info_collector.social.news.evaluator.candidate_evaluator import CandidateEvaluator
from foreign_worker_life_info_collector.social.news.models import NewsItem
from foreign_worker_life_info_collector.social.news.normalizer.news_normalizer import normalize_news_item
from foreign_worker_life_info_collector.social.news.pipeline import NewsPipeline
from foreign_worker_life_info_collector.social.news.repository.news_repository import NewsRepository


class StaticNewsCollector:
    def collect(self, keyword: str) -> list[NewsItem]:
        return [
            NewsItem(
                title="외국인 근로자 비자 지원 안내",
                url="https://example.com/news/visa-support",
                source="test",
                category="immigration",
            ),
            NewsItem(
                title="외국인 근로자 비자 지원 안내",
                url="https://example.com/news/visa-support",
                source="test",
                category="immigration",
            ),
        ]


class SocialNewsPipelineTest(unittest.TestCase):
    def test_dry_run_saves_candidates_deduplicates_and_logs_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "news.db"
            pipeline = NewsPipeline(
                repository=NewsRepository(db_path),
                collectors=[StaticNewsCollector()],
            )
            result = pipeline.run(keyword="외국인 비자", dry_run=True)

            self.assertEqual(result["collected_count"], 2)
            self.assertEqual(result["saved"][0]["status"], "DRY_RUN_NOTIFIED")
            self.assertEqual(result["saved"][1]["status"], "DUPLICATE")
            self.assertEqual(len(result["ready_to_publish"]), 1)
            self.assertEqual(result["ready_to_publish"][0]["status"], "READY_TO_PUBLISH")
            self.assertEqual(result["publish_results"][0]["status"], "DRY_RUN_NOTIFIED")
            self.assertEqual(result["publish_results"][0]["facebook_status"], "DRY_RUN")

            conn = sqlite3.connect(db_path)
            try:
                statuses = [
                    row[0]
                    for row in conn.execute("SELECT status FROM news_candidate ORDER BY id").fetchall()
                ]
                facebook_log_count = conn.execute("SELECT COUNT(*) FROM facebook_publish_log").fetchone()[0]
                telegram_log_count = conn.execute("SELECT COUNT(*) FROM telegram_notify_log").fetchone()[0]
            finally:
                conn.close()

            self.assertEqual(statuses, ["DRY_RUN_NOTIFIED", "DUPLICATE"])
            self.assertEqual(facebook_log_count, 1)
            self.assertEqual(telegram_log_count, 1)

    def test_real_mode_without_env_fails_and_logs_result_without_approval(self) -> None:
        old_env = {
            "FACEBOOK_PAGE_ID": os.environ.pop("FACEBOOK_PAGE_ID", None),
            "FACEBOOK_PAGE_ACCESS_TOKEN": os.environ.pop("FACEBOOK_PAGE_ACCESS_TOKEN", None),
            "TELEGRAM_BOT_TOKEN": os.environ.pop("TELEGRAM_BOT_TOKEN", None),
            "TELEGRAM_CHAT_ID": os.environ.pop("TELEGRAM_CHAT_ID", None),
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                db_path = Path(temp_dir) / "news.db"
                pipeline = NewsPipeline(
                    repository=NewsRepository(db_path),
                    collectors=[StaticNewsCollector()],
                )
                result = pipeline.run(keyword="외국인 비자", dry_run=False)

                self.assertEqual(result["publish_results"][0]["status"], "FAILED")
                self.assertEqual(result["publish_results"][0]["facebook_status"], "FAILED")
                self.assertIn("FACEBOOK_PAGE_ID", result["publish_results"][0]["error_message"])

                conn = sqlite3.connect(db_path)
                try:
                    statuses = [
                        row[0]
                        for row in conn.execute("SELECT status FROM news_candidate ORDER BY id").fetchall()
                    ]
                    facebook_status = conn.execute("SELECT status FROM facebook_publish_log").fetchone()[0]
                    telegram_status = conn.execute("SELECT status FROM telegram_notify_log").fetchone()[0]
                finally:
                    conn.close()

                self.assertEqual(statuses, ["FAILED", "DUPLICATE"])
                self.assertEqual(facebook_status, "FAILED")
                self.assertEqual(telegram_status, "FAILED")
            finally:
                for key, value in old_env.items():
                    if value is not None:
                        os.environ[key] = value

    def test_korea_specific_visa_news_scores_above_h1b_news(self) -> None:
        evaluator = CandidateEvaluator()
        korea_candidate = normalize_news_item(
            NewsItem(
                title="외국인 취업비자 개편으로 E-9 근로자 정주 지원 - KBS 뉴스",
                url="https://news.kbs.co.kr/korea-visa",
                source="test",
                summary="법무부와 고용노동부가 한국 산업현장 외국인 근로자 비자 제도를 개편한다.",
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


if __name__ == "__main__":
    unittest.main()
