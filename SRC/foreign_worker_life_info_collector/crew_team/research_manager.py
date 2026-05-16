from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import List, Optional

from ..models import DataQualityScore, LifeServiceBusiness, RawSourceData
from ..storage.db.sqlite_client import SQLiteDBWriter
from .research.collector_bot import CollectorAgent
from .research.normalizer_bot import NormalizerAgent
from .research.verifier_bot import VerifierAgent


@dataclass
class ResearchResult:
    keyword: str
    raw_rows: List[RawSourceData]
    businesses: List[LifeServiceBusiness]
    quality_scores: List[DataQualityScore]

    def to_dict(self) -> dict:
        return asdict(self)


class ResearchManager:
    """PyQLE crew_team의 작업 분배 개념을 외국인 생활정보 수집팀에 맞게 일반화한 관리자."""

    def __init__(
        self,
        collector_agent: Optional[CollectorAgent] = None,
        normalizer_agent: Optional[NormalizerAgent] = None,
        verifier_agent: Optional[VerifierAgent] = None,
        db_writer: Optional[SQLiteDBWriter] = None,
    ):
        self.collector_agent = collector_agent or CollectorAgent()
        self.normalizer_agent = normalizer_agent or NormalizerAgent()
        self.verifier_agent = verifier_agent or VerifierAgent()
        self.db_writer = db_writer

    def run_keyword(self, keyword: str, persist: bool = True) -> ResearchResult:
        raw_rows = self.collector_agent.collect(keyword)
        businesses = self.normalizer_agent.normalize(raw_rows)
        scored = self.verifier_agent.score(businesses)
        quality_scores = [score for _, score in scored]

        if self.db_writer and persist:
            for raw in raw_rows:
                self.db_writer.insert_raw(raw)
            for business, score in scored:
                business.id = self.db_writer.insert_business(business)
                score.business_id = business.id
                self.db_writer.insert_quality_score(score)

        return ResearchResult(
            keyword=keyword,
            raw_rows=raw_rows,
            businesses=businesses,
            quality_scores=quality_scores,
        )
