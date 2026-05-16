from __future__ import annotations


def source_reliability_score(source_url: str) -> float:
    url = (source_url or "").lower()
    if ".go.kr" in url or "gov.kr" in url:
        return 1.0
    if "or.kr" in url or "center" in url:
        return 0.8
    if url.startswith("manual://"):
        return 0.4
    if url.startswith(("http://", "https://")):
        return 0.6
    return 0.2
