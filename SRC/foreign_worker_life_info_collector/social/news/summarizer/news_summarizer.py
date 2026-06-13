"""News summarizer with optional local LLaMA support."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

from ..models import NewsCandidate, NewsSummary

LOCAL_LLAMA_ENDPOINT_ENV = "LOCAL_LLAMA_ENDPOINT"
LOCAL_LLAMA_MODEL_ENV = "LOCAL_LLAMA_MODEL"


class NewsSummarizer:
    def __init__(self, timeout: int | None = None):
        env_timeout = int(os.getenv("OLLAMA_API_REQUEST_TIMEOUT_SECONDS", "60"))
        self.timeout = timeout or max(env_timeout, 240)

    def summarize(self, candidate: NewsCandidate) -> NewsSummary:
        llama_summary = self._summarize_with_llama(candidate)
        if llama_summary:
            return llama_summary

        source_text = candidate.content or candidate.summary or candidate.title
        short_summary = _compact(source_text, max_length=180)
        summary_lines = _fallback_summary_lines(candidate, short_summary)
        why_lines = _fallback_why_lines(candidate)
        return NewsSummary(
            short_summary=short_summary,
            key_points=summary_lines,
            relevance_reason="\n".join(why_lines),
            risk_notes="Rule-based summary; verify source details before relying on the article.",
            generated_title=_compact(candidate.title, 180),
            generated_summary_en=_bullet_text(summary_lines),
            generated_why_it_matters_en=_bullet_text(why_lines),
        )

    def _summarize_with_llama(self, candidate: NewsCandidate) -> NewsSummary | None:
        endpoint = os.getenv(LOCAL_LLAMA_ENDPOINT_ENV, "").strip()
        if not endpoint:
            return None
        generate_url = endpoint.rstrip("/")
        if not generate_url.endswith("/api/generate"):
            generate_url = f"{generate_url}/api/generate"

        prompt = "\n".join(
            [
                "You are writing Facebook content for foreign workers and job seekers in Korea.",
                "Use English only.",
                "Base the content only on the article text below. Do not add facts not supported by the article.",
                "Keep the tone factual and practical. Avoid hype.",
                "Return JSON only. No markdown. No explanation.",
                "{",
                '  "generated_title": "concise English title",',
                '  "summary_bullets": ["3 to 5 factual English bullets"],',
                '  "why_it_matters": ["2 to 4 English bullets from the foreign worker/job seeker perspective"],',
                '  "risk_notes": "short English caution if needed"',
                "}",
                f"Title: {candidate.title}",
                f"Publisher: {candidate.publisher_name or candidate.source_name}",
                f"Summary: {candidate.summary}",
                f"Content: {candidate.content[: int(os.getenv('OLLAMA_SUMMARY_MAX_INPUT_CHARS', '2500'))]}",
            ]
        )
        body = json.dumps(
            {
                "model": os.getenv(LOCAL_LLAMA_MODEL_ENV) or os.getenv("LOCAL_MODEL_GENERAL") or os.getenv("LOCAL_MODEL_MASTER") or "local",
                "prompt": prompt,
                "stream": False,
                "think": False,
                "format": "json",
                "options": {
                    "temperature": 0,
                    "num_predict": int(os.getenv("OLLAMA_SUMMARY_NUM_PREDICT", "420")),
                    "num_ctx": int(os.getenv("OLLAMA_SUMMARY_NUM_CTX", os.getenv("OLLAMA_NUM_CTX", "1536"))),
                },
                "keep_alive": os.getenv("OLLAMA_KEEP_ALIVE", "30s"),
            }
        ).encode("utf-8")
        request = Request(generate_url, data=body, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception:
            return None

        if payload.get("error"):
            return None
        text = payload.get("response") or payload.get("text") or payload.get("thinking") or ""
        try:
            parsed = json.loads(_extract_json_object(text))
        except Exception:
            return None

        title = _compact(str(parsed.get("generated_title") or candidate.title), 180)
        summary_lines = _as_list(parsed.get("summary_bullets"))[:5]
        why_lines = _as_list(parsed.get("why_it_matters"))[:4]
        if len(summary_lines) < 3 or len(why_lines) < 2:
            return None
        risk_notes = str(parsed.get("risk_notes") or "")
        return NewsSummary(
            short_summary=summary_lines[0],
            key_points=summary_lines,
            relevance_reason="\n".join(why_lines),
            risk_notes=risk_notes,
            generated_title=title,
            generated_summary_en=_bullet_text(summary_lines),
            generated_why_it_matters_en=_bullet_text(why_lines),
        )


def _compact(value: str, max_length: int) -> str:
    text = " ".join((value or "").split())
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def _extract_json_object(value: str) -> str:
    text = (value or "").strip()
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def _as_list(value: object) -> list[str]:
    if isinstance(value, str):
        return [_compact(value, 260)] if value.strip() else []
    if isinstance(value, list):
        return [_compact(str(item), 260) for item in value if str(item).strip()]
    return []


def _bullet_text(lines: list[str]) -> str:
    return "\n".join(f"- {line.strip().lstrip('-').strip()}" for line in lines if line.strip())


def _fallback_summary_lines(candidate: NewsCandidate, short_summary: str) -> list[str]:
    lines = [
        _compact(candidate.title, 220),
        _compact(short_summary, 220),
        "The article is being reviewed as a Korea employment, visa, or foreign worker news item.",
    ]
    return [line for line in lines if line]


def _fallback_why_lines(candidate: NewsCandidate) -> list[str]:
    haystack = f"{candidate.title} {candidate.summary} {candidate.content}".lower()
    lines: list[str] = []
    if any(token in haystack for token in ("visa", "immigration", "e-9", "e-7", "residence")):
        lines.append("Visa or immigration details may affect eligibility and timing for foreign job seekers.")
    if any(token in haystack for token in ("worker", "labor", "employment", "hiring", "job")):
        lines.append("Employment policy changes may affect hiring conditions for foreign workers in Korea.")
    if any(token in haystack for token in ("student", "settle", "resident", "support")):
        lines.append("Foreign residents should monitor official updates for settlement and support details.")
    if not lines:
        lines.append("Foreign workers should verify whether this news affects jobs, visas, or settlement plans.")
    return lines[:4]
