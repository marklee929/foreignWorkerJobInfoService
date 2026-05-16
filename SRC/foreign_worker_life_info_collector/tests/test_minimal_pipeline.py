from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from foreign_worker_life_info_collector.crew_team.research_manager import ResearchManager
from foreign_worker_life_info_collector.models import RawSourceData
from foreign_worker_life_info_collector.research.crawler.local_site_collector import LocalSiteCollector
from foreign_worker_life_info_collector.storage.db_writer import SQLiteDBWriter


class MinimalPipelineTest(unittest.TestCase):
    def test_collect_normalize_score_and_store(self) -> None:
        seed = RawSourceData(
            source_type="local_site",
            source_url="https://example.go.kr/foreigner-center",
            search_keyword="외국인 지원센터",
            raw_title="서울 외국인 지원센터",
            raw_content="서울특별시 중구 외국인 상담, 영어 통역, E-9 고용허가제 상담. 전화 02-1234-5678",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            writer = SQLiteDBWriter(Path(temp_dir) / "life_info.db")
            manager = ResearchManager(
                collector_agent=None,
                db_writer=writer,
            )
            manager.collector_agent.collectors = [LocalSiteCollector([seed])]
            result = manager.run_keyword("외국인 지원센터")

        self.assertEqual(len(result.raw_rows), 1)
        self.assertEqual(result.businesses[0].category, "foreigner_support_center")
        self.assertEqual(result.businesses[0].sido, "서울")
        self.assertTrue(result.businesses[0].languages)
        self.assertTrue(result.quality_scores[0].total_score > 0)


if __name__ == "__main__":
    unittest.main()
