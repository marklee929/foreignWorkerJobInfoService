from __future__ import annotations

from typing import List

from .base import BaseCollector
from ..models import RawSourceData


class GoogleSearchCollector(BaseCollector):
    """Placeholder adapter for Google programmable search or SerpAPI style results."""

    source_type = "google_search"

    def collect(self, keyword: str, limit: int = 10) -> List[RawSourceData]:
        return [
            RawSourceData(
                source_type=self.source_type,
                source_url="manual://google-search-placeholder",
                search_keyword=keyword,
                raw_title=keyword,
                raw_content="Google Search API credentials are not configured. Replace this adapter with API-backed collection.",
            )
        ][:limit]
