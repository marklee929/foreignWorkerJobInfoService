"""Rule-based news summarizer with optional local LLaMA advisory support."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

from ..models import NewsCandidate, NewsSummary

LOCAL_LLAMA_ENDPOINT_ENV = "LOCAL_LLAMA_ENDPOINT"
LOCAL_LLAMA_MODEL_ENV = "LOCAL_LLAMA_MODEL"


class NewsSummarizer:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def summarize(self, candidate: NewsCandidate) -> NewsSummary:
        llama_summary = self._summarize_with_llama(candidate)
        if llama_summary:
            return llama_summary

        source_text = candidate.summary or candidate.content or candidate.title
        short_summary = _compact(source_text, max_length=180)
        return NewsSummary(
            short_summary=short_summary,
            key_points=[candidate.title, short_summary],
            relevance_reason=_relevance_reason(candidate),
            risk_notes="Rule-based summary; verify source details before relying on the article.",
        )

    def _summarize_with_llama(self, candidate: NewsCandidate) -> NewsSummary | None:
        endpoint = os.getenv(LOCAL_LLAMA_ENDPOINT_ENV, "").strip()
        if not endpoint:
            return None

        prompt = "\n".join(
            [
                "Summarize this news for foreign workers in Korea.",
                "Return JSON with short_summary, key_points, relevance_reason, risk_notes.",
                f"Title: {candidate.title}",
                f"Summary: {candidate.summary}",
                f"Content: {candidate.content[:1000]}",
            ]
        )
        body = json.dumps(
            {
                "model": os.getenv(LOCAL_LLAMA_MODEL_ENV, "local"),
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0},
            }
        ).encode("utf-8")
        request = Request(endpoint, data=body, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception:
            return None

        text = payload.get("response") or payload.get("text") or ""
        try:
            parsed = json.loads(text)
        except Exception:
            return None

        key_points = parsed.get("key_points") or []
        if isinstance(key_points, str):
            key_points = [key_points]
        return NewsSummary(
            short_summary=str(parsed.get("short_summary") or "")[:500],
            key_points=[str(point) for point in key_points[:5]],
            relevance_reason=str(parsed.get("relevance_reason") or ""),
            risk_notes=str(parsed.get("risk_notes") or ""),
        )


def _compact(value: str, max_length: int) -> str:
    text = " ".join((value or "").split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def _relevance_reason(candidate: NewsCandidate) -> str:
    haystack = f"{candidate.title} {candidate.summary} {candidate.content}".lower()
    if any(token in haystack for token in ("visa", "e-9", "e7", "비자", "체류")):
        return "Mentions visa or stay-status information relevant to foreign workers."
    if any(token in haystack for token in ("foreign worker", "foreigner", "외국인", "이주", "근로자", "노동자")):
        return "Mentions foreign workers or migrant residents in Korea."
    return "General Korea news candidate; relevance should be treated as low."
