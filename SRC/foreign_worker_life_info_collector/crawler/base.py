from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from ..models import RawSourceData


class BaseCollector(ABC):
    source_type = "base"

    @abstractmethod
    def collect(self, keyword: str, limit: int = 10) -> List[RawSourceData]:
        raise NotImplementedError
