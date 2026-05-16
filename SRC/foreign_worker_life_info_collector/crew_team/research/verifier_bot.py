from __future__ import annotations

from typing import Iterable, List, Tuple

from ...models import DataQualityScore, LifeServiceBusiness
from ...research.quality.quality_score_calculator import calculate_quality_score


class VerifierAgent:
    role = "외국인 생활정보 검증 담당"

    def score(self, businesses: Iterable[LifeServiceBusiness]) -> List[Tuple[LifeServiceBusiness, DataQualityScore]]:
        scored: List[Tuple[LifeServiceBusiness, DataQualityScore]] = []
        for business in businesses:
            scored.append((business, calculate_quality_score(business)))
        return scored


VerifierBot = VerifierAgent
