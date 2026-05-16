from __future__ import annotations

from typing import List

from ..config.categories import LANGUAGE_KEYWORDS
from ..models import BusinessLanguageSupport


def parse_languages(text: str) -> List[BusinessLanguageSupport]:
    haystack = text or ""
    found: List[BusinessLanguageSupport] = []
    for code, keywords in LANGUAGE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in haystack.lower():
                found.append(
                    BusinessLanguageSupport(
                        language_code=code,
                        language_name=keywords[0],
                        confidence_score=0.85,
                        evidence_text=keyword,
                    )
                )
                break
    return found
