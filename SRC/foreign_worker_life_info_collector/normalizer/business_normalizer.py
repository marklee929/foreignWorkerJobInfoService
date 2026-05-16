from __future__ import annotations

import re

from ..config.categories import SERVICE_TAG_KEYWORDS
from ..models import BusinessServiceTag, LifeServiceBusiness, RawSourceData
from .category_normalizer import normalize_category
from .region_normalizer import normalize_sido


def normalize_business(business: LifeServiceBusiness, raw: RawSourceData | None = None) -> LifeServiceBusiness:
    text = " ".join(filter(None, [business.business_name, business.address, raw.raw_content if raw else ""]))
    business.business_name = re.sub(r"\s+", " ", business.business_name).strip()
    business.phone = re.sub(r"\s+", "-", business.phone).strip()
    business.sido = normalize_sido(business.sido)
    business.category = normalize_category(text)
    business.tags = _extract_tags(text)
    return business


def _extract_tags(text: str) -> list[BusinessServiceTag]:
    tags: list[BusinessServiceTag] = []
    lowered = text.lower()
    for tag_name, keywords in SERVICE_TAG_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in lowered:
                tags.append(BusinessServiceTag(tag_name=tag_name, confidence_score=0.8, evidence_text=keyword))
                break
    return tags
