"""Generate validated WorkConnect card payload JSON with local LLaMA."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .content_card_renderer import (
    CardRenderFailure,
    TEMPLATE_DIR,
    contains_forbidden_text,
    contains_non_english_public_text,
    load_template_config,
    render_content_card,
    select_template_type,
)
from .text_normalizer import normalize_plain_text


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PAYLOAD_DIR = TEMPLATE_DIR / "json_payloads"
GENERATED_OUTPUT_DIR = PACKAGE_ROOT / "storage" / "generated" / "content_cards"
DEFAULT_FOOTER_URL = "WorkConnect Korea"
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TEMPLATE_SAMPLE_FILES = {
    "ALERT_REVIEW": "alert_review.json",
    "CHECKLIST_HOWTO": "checklist_howto.json",
    "LIVING_IN_KOREA": "living_in_korea.json",
    "VISA_IMMIGRATION": "visa_immigration.json",
    "WORK_LABOR_RIGHTS": "work_labor_right.json",
}
TEMPLATE_BULLET_COUNTS = {
    "CHECKLIST_HOWTO": 4,
    "ALERT_REVIEW": 3,
    "LIVING_IN_KOREA": 3,
    "VISA_IMMIGRATION": 3,
    "WORK_LABOR_RIGHTS": 3,
}
REQUIRED_FIELDS = ("template_type", "title", "subtitle", "bullets", "source", "date", "footer_url")


@dataclass(frozen=True)
class CardPayloadRequest:
    content_text: str
    source: str
    link: str
    date: str = ""
    template_type: str = ""
    category: str = ""
    source_domain: str = ""


@dataclass(frozen=True)
class CardPayloadError(Exception):
    code: str
    message: str

    def as_result(self, **extra: Any) -> dict[str, Any]:
        return {"ok": False, "status": self.code, "validation_status": self.code, "error_message": self.message, **extra}


def generate_card_from_text(
    request: CardPayloadRequest,
    output_dir: Path | None = None,
    use_llama: bool = True,
    sample_mode: bool = False,
    endpoint: str = "",
    model: str = "",
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    try:
        normalized_request = normalize_request(request)
        template_type = resolve_template_type(normalized_request)
        if sample_mode:
            payload = sample_payload_for_request(normalized_request, template_type)
            llama_status = "SAMPLE_MODE"
        elif use_llama:
            prompt = build_llama_prompt(normalized_request, template_type)
            raw_response = request_llama_payload(prompt, endpoint=endpoint, model=model, timeout_seconds=timeout_seconds)
            payload = parse_llama_json(raw_response)
            llama_status = "LLAMA_GENERATED"
        else:
            raise CardPayloadError("LLAMA_UNAVAILABLE", "LLaMA generation is disabled and sample mode was not requested.")

        validated = validate_generated_payload(payload, normalized_request, template_type)
        image_path, payload_path = render_generated_payload(validated, output_dir=output_dir)
        return {
            "ok": True,
            "status": "CARD_PREVIEW_GENERATED",
            "validation_status": "VALID",
            "llama_status": llama_status,
            "template_type": validated["template_type"],
            "source": validated["source"],
            "date": validated["date"],
            "generated_image_path": str(image_path),
            "generated_payload_path": str(payload_path),
            "payload": validated,
        }
    except CardPayloadError as exc:
        return exc.as_result(template_type=resolve_template_type_safe(request), source=request.source, date=request.date)
    except CardRenderFailure as exc:
        return {"ok": False, "status": exc.code, "validation_status": exc.code, "error_message": exc.reason, "template_type": resolve_template_type_safe(request), "source": request.source, "date": request.date}


def normalize_request(request: CardPayloadRequest) -> CardPayloadRequest:
    date = normalize_date(request.date)
    content_text = normalize_plain_text(request.content_text)
    source = normalize_plain_text(request.source)
    link = normalize_plain_text(request.link)
    if not content_text:
        raise CardPayloadError("CARD_TEXT_MISSING", "content_text is required.")
    if not source:
        raise CardPayloadError("CARD_SOURCE_INVALID", "source is required.")
    if not link:
        raise CardPayloadError("REVIEW_REQUIRED_SOURCE_LIMITED", "source link is required.")
    return CardPayloadRequest(
        content_text=content_text,
        source=source,
        link=link,
        date=date,
        template_type=normalize_plain_text(request.template_type).upper(),
        category=normalize_plain_text(request.category),
        source_domain=normalize_plain_text(request.source_domain).upper(),
    )


def resolve_template_type(request: CardPayloadRequest) -> str:
    allowed = load_template_config()
    template_type = normalize_plain_text(request.template_type).upper()
    if template_type:
        if template_type not in allowed:
            raise CardPayloadError("CARD_TEMPLATE_UNKNOWN", f"Unsupported template_type: {template_type}")
        return template_type
    return select_template_type(
        {
            "source_domain": request.source_domain,
            "category": request.category,
            "title": request.content_text[:160],
            "summary_en": request.content_text,
            "final_publish_score": 100,
        }
    )


def resolve_template_type_safe(request: CardPayloadRequest) -> str:
    try:
        return resolve_template_type(request)
    except Exception:
        return normalize_plain_text(request.template_type).upper()


def load_sample_payload(template_type: str) -> dict[str, Any]:
    file_name = TEMPLATE_SAMPLE_FILES.get(template_type)
    if not file_name:
        raise CardPayloadError("CARD_TEMPLATE_UNKNOWN", f"Unsupported template_type: {template_type}")
    path = SAMPLE_PAYLOAD_DIR / file_name
    if not path.exists():
        raise CardPayloadError("CARD_TEMPLATE_SAMPLE_MISSING", f"Sample payload is missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_llama_prompt(request: CardPayloadRequest, template_type: str) -> str:
    sample = load_sample_payload(template_type)
    llama_rules = sample.get("llama_rule") if isinstance(sample.get("llama_rule"), list) else []
    example = {key: sample[key] for key in REQUIRED_FIELDS if key in sample}
    bullet_count = TEMPLATE_BULLET_COUNTS[template_type]
    prompt_payload = {
        "task": "Create one WorkConnect content card payload JSON.",
        "output_rules": [
            "Return JSON only.",
            "Do not use markdown.",
            "Do not use a code fence.",
            "Do not add explanations.",
            "Use English only.",
            f"template_type must be exactly {template_type}.",
            "date must be YYYY-MM-DD.",
            f"Generate exactly {bullet_count} bullets.",
            "Each bullet must be short, practical, and action-oriented.",
            "Do not include system or operation messages.",
            "Do not include legal certainty.",
            "Use the provided source as source.",
            f"Use footer_url exactly as {DEFAULT_FOOTER_URL}.",
        ],
        "template_rules": llama_rules,
        "json_schema": {
            "template_type": template_type,
            "title": "English title",
            "subtitle": "English subtitle",
            "bullets": ["English bullet"],
            "source": request.source,
            "date": request.date,
            "footer_url": DEFAULT_FOOTER_URL,
        },
        "example": example,
        "input": {
            "template_type": template_type,
            "content_text": request.content_text,
            "source": request.source,
            "source_link": request.link,
            "date": request.date,
            "category": request.category,
            "source_domain": request.source_domain,
        },
    }
    return json.dumps(prompt_payload, ensure_ascii=False, indent=2)


def request_llama_payload(prompt: str, endpoint: str = "", model: str = "", timeout_seconds: int | None = None) -> str:
    if os.environ.get("LOCAL_LLAMA_ENABLED", "true").lower() not in {"1", "true", "yes", "on"}:
        raise CardPayloadError("LLAMA_UNAVAILABLE", "Local LLaMA is disabled by configuration.")
    base_endpoint = (endpoint or os.environ.get("LOCAL_LLAMA_ENDPOINT") or os.environ.get("OLLAMA_BASE_URL") or "http://localhost:11434").rstrip("/")
    generate_url = base_endpoint if base_endpoint.endswith("/api/generate") else f"{base_endpoint}/api/generate"
    model_name = model or os.environ.get("LOCAL_LLAMA_MODEL") or os.environ.get("LOCAL_MODEL_GENERAL") or os.environ.get("LOCAL_MODEL_MASTER") or "llama3.1"
    timeout = timeout_seconds if timeout_seconds is not None else int(os.environ.get("OLLAMA_API_REQUEST_TIMEOUT_SECONDS", "60"))
    body = json.dumps(
        {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "num_predict": int(os.environ.get("OLLAMA_CARD_PAYLOAD_NUM_PREDICT", "700")),
                "num_ctx": int(os.environ.get("OLLAMA_CARD_PAYLOAD_NUM_CTX", os.environ.get("OLLAMA_NUM_CTX", "2048"))),
            },
            "keep_alive": os.environ.get("OLLAMA_KEEP_ALIVE", "30s"),
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(generate_url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8", errors="replace"))
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        raise CardPayloadError("LLAMA_UNAVAILABLE", f"Local LLaMA request failed: {exc.__class__.__name__}") from exc
    raw = str(result.get("response") or "").strip()
    if not raw:
        raise CardPayloadError("LLAMA_RESPONSE_EMPTY", "Local LLaMA returned an empty response.")
    return raw


def parse_llama_json(raw_response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise CardPayloadError("LLAMA_RESPONSE_INVALID_JSON", "Local LLaMA response was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise CardPayloadError("LLAMA_RESPONSE_INVALID_JSON", "Local LLaMA response JSON must be an object.")
    return parsed


def sample_payload_for_request(request: CardPayloadRequest, template_type: str) -> dict[str, Any]:
    sample = load_sample_payload(template_type)
    payload = {key: sample[key] for key in REQUIRED_FIELDS if key in sample}
    payload["template_type"] = template_type
    payload["source"] = request.source
    payload["date"] = request.date
    payload["footer_url"] = DEFAULT_FOOTER_URL
    return payload


def validate_generated_payload(payload: dict[str, Any], request: CardPayloadRequest, template_type: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise CardPayloadError("CARD_PAYLOAD_INVALID", "Generated payload must be a JSON object.")
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise CardPayloadError("CARD_PAYLOAD_MISSING_FIELD", f"Generated payload is missing fields: {', '.join(missing)}")

    allowed = load_template_config()
    actual_template = normalize_plain_text(payload.get("template_type")).upper()
    if actual_template not in allowed:
        raise CardPayloadError("CARD_TEMPLATE_UNKNOWN", f"Unsupported template_type: {actual_template}")
    if actual_template != template_type:
        raise CardPayloadError("CARD_TEMPLATE_MISMATCH", "Generated template_type does not match the requested template.")

    source = normalize_plain_text(payload.get("source"))
    if source != request.source:
        source = request.source
    footer_url = normalize_plain_text(payload.get("footer_url") or DEFAULT_FOOTER_URL) or DEFAULT_FOOTER_URL
    date = normalize_plain_text(payload.get("date")) or request.date
    if not DATE_PATTERN.match(date):
        raise CardPayloadError("CARD_DATE_INVALID", "date must be YYYY-MM-DD.")

    bullets = payload.get("bullets")
    if not isinstance(bullets, list) or not all(isinstance(item, str) for item in bullets):
        raise CardPayloadError("CARD_BULLETS_INVALID", "bullets must be an array of strings.")
    expected_count = TEMPLATE_BULLET_COUNTS[template_type]
    if len(bullets) != expected_count:
        raise CardPayloadError("CARD_BULLET_COUNT_INVALID", f"{template_type} requires exactly {expected_count} bullets.")

    validated = {
        "template_type": actual_template,
        "title": normalize_plain_text(payload.get("title")),
        "subtitle": normalize_plain_text(payload.get("subtitle")),
        "bullets": [normalize_plain_text(item) for item in bullets],
        "source": source,
        "date": date,
        "footer_url": footer_url,
    }
    if not validated["title"] or not validated["subtitle"]:
        raise CardPayloadError("CARD_TEXT_MISSING", "title and subtitle are required.")

    public_text = "\n".join(
        [
            validated["title"],
            validated["subtitle"],
            *validated["bullets"],
            validated["source"],
            validated["footer_url"],
        ]
    )
    if contains_non_english_public_text(public_text):
        raise CardPayloadError("CARD_TEXT_INVALID_LANGUAGE", "Card payload public text must be English-only.")
    if contains_forbidden_text(public_text):
        raise CardPayloadError("CARD_TEXT_FORBIDDEN_SYSTEM_TEXT", "Card payload contains system or operation wording.")
    return validated


def render_generated_payload(payload: dict[str, Any], output_dir: Path | None = None) -> tuple[Path, Path]:
    output_base = output_dir or GENERATED_OUTPUT_DIR
    output_base.mkdir(parents=True, exist_ok=True)
    rendered_path = render_content_card(payload, output_dir=output_base)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:10]
    stem = f"{payload['template_type']}_{timestamp}_{short_hash}"
    image_path = output_base / f"{stem}.png"
    payload_path = output_base / f"{stem}.json"
    if rendered_path != image_path:
        rendered_path.replace(image_path)
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return image_path, payload_path


def normalize_date(value: str) -> str:
    raw = normalize_plain_text(value)
    if DATE_PATTERN.match(raw):
        return raw
    if raw:
        match = re.search(r"\d{4}-\d{2}-\d{2}", raw)
        if match:
            return match.group(0)
    return datetime.now(timezone.utc).date().isoformat()
