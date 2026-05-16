from __future__ import annotations

from ..models import DataQualityScore, LifeServiceBusiness


def calculate_quality_score(business: LifeServiceBusiness, duplicate_score: float = 0.0) -> DataQualityScore:
    contact_validity = 1.0 if business.phone or business.website_url else 0.35
    foreigner_relevance = 1.0 if business.tags or business.languages or "외국" in business.business_name else 0.45
    freshness = 0.8 if business.is_active else 0.2
    total = (1.0 - duplicate_score) * 0.25 + freshness * 0.20 + contact_validity * 0.25 + foreigner_relevance * 0.30
    return DataQualityScore(
        business_id=business.id,
        duplicate_score=round(duplicate_score, 4),
        freshness_score=round(freshness, 4),
        contact_validity_score=round(contact_validity, 4),
        foreigner_relevance_score=round(foreigner_relevance, 4),
        total_score=round(total, 4),
    )
