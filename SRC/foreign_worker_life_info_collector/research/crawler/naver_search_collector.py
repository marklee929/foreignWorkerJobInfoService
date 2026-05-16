from __future__ import annotations

from typing import List

from .base import BaseCollector
from ...models import RawSourceData


class NaverSearchCollector(BaseCollector):
    """Placeholder adapter for Naver Search API results."""

    source_type = "naver_search"

    def collect(self, keyword: str, limit: int = 10) -> List[RawSourceData]:
        return [
            RawSourceData(
                source_type=self.source_type,
                source_url="manual://naver-search-placeholder",
                search_keyword=keyword,
                raw_title=keyword,
                raw_content="Naver Search API credentials are not configured. Replace this adapter with API-backed collection.",
            )
        ][:limit]
