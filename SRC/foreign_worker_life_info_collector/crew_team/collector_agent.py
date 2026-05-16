from __future__ import annotations

from typing import Iterable, List

from ..crawler.base import BaseCollector
from ..crawler.google_search_collector import GoogleSearchCollector
from ..crawler.naver_search_collector import NaverSearchCollector
from ..models import RawSourceData


class CollectorAgent:
    role = "외국인 생활정보 수집 담당"

    def __init__(self, collectors: Iterable[BaseCollector] | None = None):
        self.collectors = list(collectors or [GoogleSearchCollector(), NaverSearchCollector()])

    def collect(self, keyword: str, limit_per_source: int = 10) -> List[RawSourceData]:
        rows: List[RawSourceData] = []
        for collector in self.collectors:
            rows.extend(collector.collect(keyword, limit=limit_per_source))
        return rows
