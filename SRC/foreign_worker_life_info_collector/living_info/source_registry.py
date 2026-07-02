"""Curated public source candidates for Living Information evidence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LivingInfoSourceCandidate:
    key: str
    name: str
    url: str
    domain: str
    category: str
    trust_level: str
    intended_use: str


OFFICIAL_LIVING_INFO_SOURCES: tuple[LivingInfoSourceCandidate, ...] = (
    LivingInfoSourceCandidate(
        key="seoul-global-center",
        name="Seoul Global Center",
        url="https://global.seoul.go.kr/",
        domain="global.seoul.go.kr",
        category="REGIONAL_SUPPORT",
        trust_level="PRIMARY",
        intended_use="Seoul foreign resident living support and local service evidence",
    ),
    LivingInfoSourceCandidate(
        key="seoul-city",
        name="Seoul Metropolitan Government",
        url="https://www.seoul.go.kr/",
        domain="seoul.go.kr",
        category="REGIONAL_SUPPORT",
        trust_level="PRIMARY",
        intended_use="Local government public service evidence",
    ),
    LivingInfoSourceCandidate(
        key="hikorea",
        name="HiKorea",
        url="https://www.hikorea.go.kr/",
        domain="hikorea.go.kr",
        category="REGIONAL_SUPPORT",
        trust_level="PRIMARY",
        intended_use="Stay, immigration, and public-service guide validation",
    ),
    LivingInfoSourceCandidate(
        key="nhis",
        name="National Health Insurance Service",
        url="https://www.nhis.or.kr/",
        domain="nhis.or.kr",
        category="HEALTHCARE",
        trust_level="PRIMARY",
        intended_use="Health insurance and healthcare evidence",
    ),
    LivingInfoSourceCandidate(
        key="nps",
        name="National Pension Service",
        url="https://www.nps.or.kr/",
        domain="nps.or.kr",
        category="BANKING_FINANCE",
        trust_level="PRIMARY",
        intended_use="Pension and social insurance evidence",
    ),
    LivingInfoSourceCandidate(
        key="moel",
        name="Ministry of Employment and Labor",
        url="https://www.moel.go.kr/",
        domain="moel.go.kr",
        category="SAFETY_SCAM",
        trust_level="PRIMARY",
        intended_use="Labor rights and workplace safety evidence",
    ),
    LivingInfoSourceCandidate(
        key="gov-kr",
        name="Gov.kr",
        url="https://www.gov.kr/",
        domain="gov.kr",
        category="DAILY_LIFE",
        trust_level="PRIMARY",
        intended_use="General public service evidence",
    ),
    LivingInfoSourceCandidate(
        key="gyeonggi-foreign-resident-support",
        name="Gyeonggi foreign resident support source",
        url="https://www.gg.go.kr/",
        domain="gg.go.kr",
        category="REGIONAL_SUPPORT",
        trust_level="PRIMARY",
        intended_use="Regional foreign resident support evidence",
    ),
)


def official_living_info_sources() -> list[dict[str, str]]:
    return [
        {
            "key": source.key,
            "name": source.name,
            "url": source.url,
            "domain": source.domain,
            "category": source.category,
            "trust_level": source.trust_level,
            "intended_use": source.intended_use,
        }
        for source in OFFICIAL_LIVING_INFO_SOURCES
    ]
