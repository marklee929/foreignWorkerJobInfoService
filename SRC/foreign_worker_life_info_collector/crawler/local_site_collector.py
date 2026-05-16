from __future__ import annotations

from typing import Iterable, List

from .base import BaseCollector
from ..models import RawSourceData


class LocalSiteCollector(BaseCollector):
    """Collector for already-known local URLs or manually supplied seed records."""

    source_type = "local_site"

    def __init__(self, seed_records: Iterable[RawSourceData] | None = None):
        self.seed_records = list(seed_records or [])

    def collect(self, keyword: str, limit: int = 10) -> List[RawSourceData]:
        matched = [
            record
            for record in self.seed_records
            if keyword.lower() in f"{record.raw_title} {record.raw_content}".lower()
        ]
        return matched[:limit]
