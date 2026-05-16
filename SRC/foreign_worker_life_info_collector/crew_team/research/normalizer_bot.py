from __future__ import annotations

from typing import Iterable, List

from ...models import LifeServiceBusiness, RawSourceData
from ...research.normalizer.business_normalizer import normalize_business
from ...research.parser.business_info_parser import parse_business_info


class NormalizerAgent:
    role = "외국인 생활정보 정규화 담당"

    def normalize(self, raw_rows: Iterable[RawSourceData]) -> List[LifeServiceBusiness]:
        businesses: List[LifeServiceBusiness] = []
        for raw in raw_rows:
            business = parse_business_info(raw)
            businesses.append(normalize_business(business, raw))
        return businesses


NormalizerBot = NormalizerAgent
