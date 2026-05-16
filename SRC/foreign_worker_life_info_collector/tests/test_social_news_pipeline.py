from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from foreign_worker_life_info_collector.social.news.models import NewsItem
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
            self.assertEqual(result["saved"][0]["status"], "CANDIDATE")
            self.assertEqual(result["saved"][1]["status"], "DUPLICATE")
            self.assertEqual(len(result["ready_to_publish"]), 1)
            self.assertEqual(result["publish_results"][0]["status"], "DRY_RUN")

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

            self.assertEqual(statuses, ["PUBLISHED", "DUPLICATE"])
            self.assertEqual(facebook_log_count, 1)
            self.assertEqual(telegram_log_count, 1)


if __name__ == "__main__":
    unittest.main()
