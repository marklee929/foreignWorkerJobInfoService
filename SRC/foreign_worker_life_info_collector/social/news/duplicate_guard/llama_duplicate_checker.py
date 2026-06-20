"""Optional local LLaMA semantic duplicate advisory."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

from ..models import NewsCandidate

LOCAL_LLAMA_ENDPOINT_ENV = "LOCAL_LLAMA_ENDPOINT"
LOCAL_LLAMA_MODEL_ENV = "LOCAL_LLAMA_MODEL"
OLLAMA_DUPLICATE_KEEP_ALIVE_ENV = "OLLAMA_DUPLICATE_KEEP_ALIVE"
DEFAULT_DUPLICATE_KEEP_ALIVE = "30s"


class LlamaDuplicateChecker:
    def __init__(self, timeout: int = 8):
        self.timeout = timeout

    def check(self, candidate: NewsCandidate, recent_candidates: list[NewsCandidate]) -> tuple[bool, float, str]:
        endpoint = os.getenv(LOCAL_LLAMA_ENDPOINT_ENV, "").strip()
        if not endpoint or not recent_candidates:
            return False, 0.0, "local_llama_unavailable"

        prompt = self._build_prompt(candidate, recent_candidates[:5])
        body = json.dumps(
            {
                "model": os.getenv(LOCAL_LLAMA_MODEL_ENV) or os.getenv("LOCAL_MODEL_GENERAL") or os.getenv("LOCAL_MODEL_MASTER") or "local",
                "prompt": prompt,
                "stream": False,
                "think": False,
                "format": "json",
                "options": {
                    "temperature": 0,
                    "num_predict": int(os.getenv("OLLAMA_DUPLICATE_NUM_PREDICT", "120")),
                    "num_ctx": int(os.getenv("OLLAMA_DUPLICATE_NUM_CTX", "768")),
                },
                "keep_alive": os.getenv(OLLAMA_DUPLICATE_KEEP_ALIVE_ENV, DEFAULT_DUPLICATE_KEEP_ALIVE),
            }
        ).encode("utf-8")
        request = Request(endpoint, data=body, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception:
            return False, 0.0, "local_llama_timeout_or_error"

        text = str(payload.get("response") or payload.get("text") or "").strip()
        try:
            parsed = json.loads(text)
        except Exception:
            return False, 0.0, "local_llama_unparseable"

        duplicate = bool(parsed.get("duplicate", False))
        confidence = float(parsed.get("confidence", 0.0) or 0.0)
        reason = str(parsed.get("reason") or "local_llama_advisory")
        return duplicate, max(0.0, min(confidence, 1.0)), reason

    def _build_prompt(self, candidate: NewsCandidate, recent_candidates: list[NewsCandidate]) -> str:
        recent = "\n".join(
            f"- {item.title} | {item.short_summary or item.summary} | {item.source_url}"
            for item in recent_candidates
        )
        return "\n".join(
            [
                "Decide whether the candidate describes the same real-world news event as any recent item.",
                "Return only JSON: {\"duplicate\": boolean, \"confidence\": number, \"reason\": string}",
                f"Candidate: {candidate.title} | {candidate.short_summary or candidate.summary} | {candidate.source_url}",
                "Recent items:",
                recent,
            ]
        )
