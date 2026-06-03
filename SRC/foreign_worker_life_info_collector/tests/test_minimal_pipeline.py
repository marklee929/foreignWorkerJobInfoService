from __future__ import annotations

import unittest

from foreign_worker_life_info_collector.crew_team.research_manager import ResearchManager
from foreign_worker_life_info_collector.models import RawSourceData
from foreign_worker_life_info_collector.research.crawler.local_site_collector import LocalSiteCollector


class MinimalPipelineTest(unittest.TestCase):
    def test_collect_normalize_score_without_file_storage(self) -> None:
        seed = RawSourceData(
            source_type="local_site",
            source_url="https://example.go.kr/foreigner-center",
            search_keyword="외국인 지원센터",
            raw_title="서울 외국인 지원센터",
            raw_content="서울 중구 외국인 상담, 영어 통역, E-9 고용 상담. 전화 02-1234-5678",
        )
        manager = ResearchManager(collector_agent=None)
        manager.collector_agent.collectors = [LocalSiteCollector([seed])]
        result = manager.run_keyword("외국인 지원센터", persist=False)

        self.assertEqual(len(result.raw_rows), 1)
        self.assertEqual(result.businesses[0].category, "foreigner_support_center")
        self.assertEqual(result.businesses[0].sido, "서울")
        self.assertTrue(result.businesses[0].languages)
        self.assertTrue(result.quality_scores[0].total_score > 0)


if __name__ == "__main__":
    unittest.main()

