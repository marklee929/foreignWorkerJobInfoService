"""Generate WorkConnect content card preview images for Telegram review."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .text_normalizer import normalize_plain_text


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PACKAGE_ROOT / "assets" / "templates" / "content_cards"
CONFIG_PATH = TEMPLATE_DIR / "content_card_templates.json"
DEFAULT_OUTPUT_DIR = PACKAGE_ROOT / "storage" / "cache" / "content_cards"
DEFAULT_FOOTER_TEXT = "WORK CONNECT KOREA"
DEFAULT_FOOTER_URL = DEFAULT_FOOTER_TEXT
OUTPUT_SIZE = (1080, 1080)
MIN_FONT_SIZE = 22
TEXT_COLOR = "#0f172a"
MUTED_TEXT_COLOR = "#475569"
CATEGORY_COLOR = TEXT_COLOR
DEFAULT_CATEGORY_SPEC = {
    "enabled": True,
    "x": 700,
    "y": 75,
    "max_width": 300,
    "font_size": 34,
    "max_lines": 1,
    "font_color": CATEGORY_COLOR,
}

CARD_FORMATS = {"CARD_IMAGE", "CHECKLIST_CARD", "SHORT_CARD", "GUIDE_CARD"}
TEMPLATE_POLICY = "USE_WORKCONNECT_TEMPLATE"
NEWS_LINK_TYPES = {"NEWS_ARTICLE"}
BYPASS_CARD_QUALITY_CODES = {
    "BLOCKED_SOURCE_INVALID",
    "BLOCKED_TARGET_COUNTRY_MISMATCH",
    "BLOCKED_GLOBAL_REFERENCE_ONLY",
    "BLOCKED_LOW_USER_NEED",
    "BLOCKED_GENERIC_TRAVEL",
    "BLOCKED_GENERIC_CRYPTO",
    "BLOCKED_DOMESTIC_POLITICS",
    "BLOCKED_GENERIC_ECONOMY",
    "BLOCKED_CONTENT_MISSING",
    "BLOCKED_SYSTEM_TEXT",
    "GLOBAL_REFERENCE_ONLY",
    "WATCH_TOPIC_ONLY",
}
BULLET_MAX_CHARS = 80
MIN_VALID_BULLETS = 3
CARD_TEXT_REVIEW_ONLY_CODES = {
    "CARD_NOT_READY",
    "CARD_POINT_TITLE_ECHO",
    "CARD_POINT_SOURCE_ECHO",
    "CARD_POINT_URL_ECHO",
    "CARD_POINT_DUPLICATE",
    "CARD_POINT_TOO_SHORT",
    "CARD_POINT_GENERIC_LABEL",
    "CARD_POINT_FORBIDDEN_SYSTEM_TEXT",
    "INSUFFICIENT_VALID_CARD_POINTS",
}

FORBIDDEN_CARD_TEXT = (
    "저장된 기사 본문이 없습니다",
    "일부 rss",
    "검색 결과는 원문 html 접근이 제한",
    "관리자 재게시 요청",
    "게시 기준",
    "현재 점수",
    "ready_to_publish",
    "content candidate",
    "candidate_id",
    "candidate id",
    "queue",
    "threshold",
    "publish_status",
    "publish",
    "diagnostic",
    "facebook 게시를 시도",
    "즉시 facebook",
    "no article body was saved",
    "content unavailable",
    "failed to fetch article",
    "parser error",
    "access denied",
)

SOURCE_NAME_MAP = {
    "고용노동부": "MOEL",
    "고용노동부 외국인고용 관련 공지": "MOEL",
    "하이코리아 공지사항": "HiKorea",
    "하이코리아": "HiKorea",
    "법무부": "Ministry of Justice",
    "법무부 공지사항": "Ministry of Justice",
}


@dataclass(frozen=True)
class CardRenderFailure(Exception):
    code: str
    reason: str

    def as_result(self, template_type: str = "") -> dict[str, Any]:
        return {
            "ok": False,
            "status": self.code,
            "reason": self.reason,
            "template_type": template_type,
            "card_required": self.code not in CARD_TEXT_REVIEW_ONLY_CODES,
        }


def build_content_card_preview(candidate: dict[str, Any], output_dir: Path | None = None) -> dict[str, Any]:
    target = card_generation_target(candidate)
    if not target["eligible"]:
        return {
            "ok": False,
            "status": target.get("status", "CARD_NOT_REQUIRED"),
            "reason": target["reason"],
            "card_required": bool(target.get("card_required", False)),
        }
    template_type = select_template_type(candidate)
    try:
        payload = build_content_card_payload(candidate, template_type)
        output_path = render_content_card(payload, output_dir=output_dir)
    except CardRenderFailure as exc:
        return exc.as_result(template_type)
    return {
        "ok": True,
        "status": "CARD_PREVIEW_GENERATED",
        "card_required": True,
        "template_type": template_type,
        "payload": payload,
        "image_path": str(output_path),
        "image_name": output_path.name,
    }


def card_generation_target(candidate: dict[str, Any]) -> dict[str, Any]:
    raw_payload = candidate.get("raw_payload") if isinstance(candidate.get("raw_payload"), dict) else {}
    content_type = clean(candidate.get("content_type")).upper()
    content_format = clean(candidate.get("content_format") or raw_payload.get("content_format")).upper()
    asset_policy = clean(candidate.get("asset_policy") or raw_payload.get("asset_policy")).upper()
    source_domain = clean(candidate.get("source_domain")).upper()
    link_url = clean(candidate.get("link_url") or candidate.get("source_url") or candidate.get("original_source_url"))
    score = parse_score(candidate.get("final_publish_score") or candidate.get("quality_score"))
    quality_code = clean(candidate.get("content_quality_gate_code") or raw_payload.get("content_quality_gate_code")).upper()

    if score <= 0:
        return {"eligible": False, "reason": "CARD_BLOCKED_ZERO_SCORE"}
    if quality_code in BYPASS_CARD_QUALITY_CODES:
        return {"eligible": False, "reason": quality_code}
    if content_type in NEWS_LINK_TYPES and valid_link(link_url):
        return {"eligible": False, "reason": "NEWS_ARTICLE_LINK_PREVIEW_USES_OG"}
    if is_single_living_source_without_topic_evidence(candidate):
        return {
            "eligible": False,
            "status": "CARD_NOT_READY",
            "reason": "single_news_public_card_not_ready",
            "card_required": False,
        }
    if content_format in CARD_FORMATS:
        return {"eligible": True, "reason": "content_format"}
    if asset_policy == TEMPLATE_POLICY:
        return {"eligible": True, "reason": "asset_policy"}
    if source_domain in {"LIVING_INFO", "IMMIGRATION_INFO", "VISA_INFO"} and content_type not in NEWS_LINK_TYPES:
        return {"eligible": True, "reason": "information_domain"}
    if not link_url and clean(candidate.get("source_name")) and clean(candidate.get("body_en") or candidate.get("summary_en")):
        return {"eligible": True, "reason": "structured_info_without_link"}
    return {"eligible": False, "reason": "not_information_card_content"}


def build_content_card_payload(candidate: dict[str, Any], template_type: str) -> dict[str, Any]:
    config = load_template_config().get(template_type)
    if not config:
        raise CardRenderFailure("CARD_TEMPLATE_UNKNOWN", f"Template type is not configured: {template_type}")

    title = clean(candidate.get("card_title") or candidate.get("title") or candidate.get("original_title"))
    subtitle = card_subtitle(candidate)
    source = card_source(candidate)
    bullets = card_bullets(candidate, title=title, source=source)
    date = card_date(candidate)
    footer_url = card_footer(candidate)
    payload = {
        "template_type": template_type,
        "title": title,
        "subtitle": subtitle,
        "bullets": bullets[:3],
        "source": source,
        "date": date,
        "footer_url": footer_url,
    }
    validate_card_payload(payload)
    return payload


def render_content_card(payload: dict[str, Any], output_dir: Path | None = None) -> Path:
    template_type = clean(payload.get("template_type")).upper()
    config = load_template_config().get(template_type)
    if not config:
        raise CardRenderFailure("CARD_TEMPLATE_UNKNOWN", f"Template type is not configured: {template_type}")
    template_path = TEMPLATE_DIR / config["template_file"]
    if not template_path.exists():
        raise CardRenderFailure("CARD_TEMPLATE_MISSING", f"Template file is missing: {template_path}")

    with Image.open(template_path) as source:
        image = source.convert("RGB").resize(OUTPUT_SIZE, Image.LANCZOS)
    draw = ImageDraw.Draw(image)
    positions = config["positions"]

    category_spec = default_text_spec(positions.get("category"), DEFAULT_CATEGORY_SPEC)
    if category_spec.get("enabled", True):
        draw_text_box(draw, category_spec, config["category_label"], str(category_spec.get("font_color") or CATEGORY_COLOR), bold=True)
    draw_text_box(draw, positions["title"], payload["title"], TEXT_COLOR, bold=True)
    draw_text_box(draw, positions["subtitle"], payload["subtitle"], MUTED_TEXT_COLOR)
    bullet_prefix = str(config.get("bullet_prefix", "- "))
    bullet_positions = positions.get("bullets", [])
    if len(payload["bullets"]) > len(bullet_positions):
        raise CardRenderFailure("CARD_TEXT_OVERFLOW", "Card has more bullets than the selected template supports.")
    for index, bullet in enumerate(payload["bullets"][: len(bullet_positions)]):
        draw_text_box(draw, positions["bullets"][index], f"{bullet_prefix}{bullet}", TEXT_COLOR)
    draw_text_box(draw, positions["source"], f"Source: {payload['source']}", MUTED_TEXT_COLOR)
    draw_text_box(draw, positions["date"], payload["date"], MUTED_TEXT_COLOR)
    footer_spec = positions.get("footer_url")
    if footer_spec and footer_spec.get("enabled", True):
        draw_text_box(draw, footer_spec, payload["footer_url"], MUTED_TEXT_COLOR)

    output_base = output_dir or DEFAULT_OUTPUT_DIR
    output_base.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()[:12]
    output_path = output_base / f"workconnect-card-{template_type.lower()}-{digest}.png"
    image.save(output_path, format="PNG", optimize=True)
    return output_path


def draw_text_box(draw: ImageDraw.ImageDraw, spec: dict[str, Any], text: str, fill: str, bold: bool = False) -> None:
    font_path = preferred_font_path(bold=bold)
    lines, font = fit_lines(
        draw,
        clean(text),
        font_path=font_path,
        start_size=int(spec.get("font_size") or 30),
        max_width=int(spec.get("max_width") or 700),
        max_lines=int(spec.get("max_lines") or 1),
    )
    x = int(spec.get("x") or 0)
    y = int(spec.get("y") or 0)
    line_height = int(font.size * 1.18)
    for line in lines:
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height


def default_text_spec(spec: dict[str, Any] | None, defaults: dict[str, Any]) -> dict[str, Any]:
    merged = dict(defaults)
    if spec:
        merged.update(spec)
    return merged


def fit_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    start_size: int,
    max_width: int,
    max_lines: int,
) -> tuple[list[str], ImageFont.FreeTypeFont]:
    for size in range(max(start_size, MIN_FONT_SIZE), MIN_FONT_SIZE - 1, -2):
        font = ImageFont.truetype(font_path, size=size)
        lines = wrap_lines(draw, text, font, max_width)
        if lines and len(lines) <= max_lines:
            return lines, font
    raise CardRenderFailure("CARD_TEXT_OVERFLOW", f"Text does not fit within {max_lines} lines: {text[:80]}")


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = clean(text).split()
    if not words:
        return []
    lines: list[str] = []
    current = ""
    for word in words:
        if text_width(draw, word, font) > max_width:
            return []
        candidate = word if not current else f"{current} {word}"
        if text_width(draw, candidate, font) <= max_width:
            current = candidate
            continue
        lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> int:
    left, _top, right, _bottom = draw.textbbox((0, 0), text, font=font)
    return right - left


def select_template_type(candidate: dict[str, Any]) -> str:
    raw_payload = candidate.get("raw_payload") if isinstance(candidate.get("raw_payload"), dict) else {}
    override = clean(candidate.get("template_type") or raw_payload.get("template_type")).upper()
    if override in load_template_config():
        return override

    source_domain = clean(candidate.get("source_domain")).upper()
    content_type = clean(candidate.get("content_type")).upper()
    category = clean(candidate.get("category")).lower()
    text = normalize_plain_text(
        " ".join(
            clean(candidate.get(key))
            for key in ("title", "summary_en", "why_it_matters_en", "body_en", "review_reason")
        )
    ).lower()
    if bool(candidate.get("sensitive_yn")) or bool(candidate.get("review_required_yn")) or has_any(text, ("source limited", "legal caution", "policy may change", "content incomplete")):
        return "ALERT_REVIEW"
    if source_domain in {"IMMIGRATION_INFO", "VISA_INFO"} or content_type in {"IMMIGRATION_NOTICE", "GOVERNMENT_NOTICE"} or has_any(category, ("visa", "immigration", "visa_policy")):
        return "VISA_IMMIGRATION"
    if has_any(category, ("checklist", "how_to", "required_documents", "step_by_step", "preparation", "application_steps")) or has_any(text, ("checklist", "how to", "documents", "step by step", "prepare", "application steps")):
        return "CHECKLIST_HOWTO"
    if has_any(category, ("labor_rights", "minimum_wage", "employment_policy", "work_contract", "industrial_accident", "wage", "workplace_safety")) or has_any(text, ("labor rights", "minimum wage", "work contract", "industrial accident", "wage", "workplace safety")):
        return "WORK_LABOR_RIGHTS"
    return "LIVING_IN_KOREA"


def card_bullets(candidate: dict[str, Any], title: str = "", source: str = "") -> list[str]:
    raw_bullets = candidate.get("card_bullets")
    if isinstance(raw_bullets, list):
        bullets = [clean(item) for item in raw_bullets if clean(item)]
        compact = False
    else:
        text = clean(candidate.get("summary_en") or candidate.get("body_en"))
        bullets = split_sentences(text)
        compact = True
    if len(bullets) < 3:
        why = clean(candidate.get("why_it_matters_en"))
        bullets.extend(split_sentences(why))
    result: list[str] = []
    rejected: list[str] = []
    seen: set[str] = set()
    for bullet in bullets:
        prepared = compact_card_text(bullet, BULLET_MAX_CHARS) if compact else bullet
        if not prepared:
            continue
        if len(prepared) > BULLET_MAX_CHARS:
            raise CardRenderFailure("CARD_TEXT_OVERFLOW", f"Bullet is too long for card rendering: {prepared[:80]}")
        reason = invalid_card_point_reason(prepared, title=title, source=source, candidate=candidate)
        if reason:
            rejected.append(reason)
            continue
        normalized = normalized_card_point(prepared)
        if normalized in seen:
            rejected.append("CARD_POINT_DUPLICATE")
            continue
        seen.add(normalized)
        result.append(prepared)
        if len(result) == MIN_VALID_BULLETS:
            break
    if len(result) < MIN_VALID_BULLETS:
        code = rejected[0] if rejected else "INSUFFICIENT_VALID_CARD_POINTS"
        raise CardRenderFailure(code, f"Card requires at least {MIN_VALID_BULLETS} validated points before image generation.")
    return result


def card_subtitle(candidate: dict[str, Any]) -> str:
    explicit = clean(candidate.get("card_subtitle"))
    if explicit:
        return explicit
    raw = clean(candidate.get("why_it_matters_en") or candidate.get("summary_en"))
    return compact_card_text(raw, 150)


def compact_card_text(text: str, max_chars: int) -> str:
    cleaned = clean(text).strip(" -")
    if len(cleaned) <= max_chars:
        return cleaned
    for separator in (". ", ";", ":", " - ", " – ", " — ", ",", " and ", " so ", " because "):
        first = trim_trailing_connector(cleaned.split(separator, 1)[0].strip(" -"))
        if 20 <= len(first) <= max_chars:
            return first
    words = cleaned.split()
    result: list[str] = []
    for word in words:
        candidate = " ".join([*result, word])
        if len(candidate) > max_chars:
            break
        result.append(word)
    shortened = trim_trailing_connector(" ".join(result).strip(" ,.;:-"))
    return shortened or cleaned[:max_chars].strip(" ,.;:-")


def trim_trailing_connector(text: str) -> str:
    return re.sub(r"\s+(and|or|so|because|but|with|for|to)$", "", text, flags=re.IGNORECASE).strip(" ,.;:-")


def split_sentences(text: str) -> list[str]:
    cleaned = clean(text)
    if not cleaned:
        return []
    parts = re.split(r"(?<=[.!?])\s+|[\r\n]+", cleaned)
    return [part.strip(" -") for part in parts if part.strip(" -")]


def validate_card_payload(payload: dict[str, Any]) -> None:
    if not clean(payload.get("title")):
        raise CardRenderFailure("CARD_TEXT_MISSING", "Card title is missing.")
    if not clean(payload.get("subtitle")):
        raise CardRenderFailure("CARD_TEXT_MISSING", "Card subtitle is missing.")
    if not payload.get("bullets"):
        raise CardRenderFailure("CARD_TEXT_MISSING", "Card bullets are missing.")
    if len(payload.get("bullets", [])) < MIN_VALID_BULLETS:
        raise CardRenderFailure("INSUFFICIENT_VALID_CARD_POINTS", "Card requires at least 3 validated points before image generation.")
    text_fields = [
        clean(payload.get("title")),
        clean(payload.get("subtitle")),
        *[clean(item) for item in payload.get("bullets", [])],
        clean(payload.get("source")),
        clean(payload.get("date")),
        clean(payload.get("footer_url")),
    ]
    joined = "\n".join(text_fields)
    if contains_forbidden_text(joined):
        raise CardRenderFailure("CARD_TEXT_FORBIDDEN_SYSTEM_TEXT", "Card text contains system or operation wording.")
    if contains_non_english_public_text(joined):
        raise CardRenderFailure("CARD_TEXT_INVALID_LANGUAGE", "Card text must be English-only.")
    if contains_url(clean(payload.get("footer_url"))):
        raise CardRenderFailure("CARD_FOOTER_URL_FORBIDDEN", "Card footer must not contain a URL.")


def contains_forbidden_text(value: str) -> bool:
    text = normalize_plain_text(value).lower()
    return any(term in text for term in FORBIDDEN_CARD_TEXT)


def contains_non_english_public_text(value: str) -> bool:
    return any("\uac00" <= char <= "\ud7a3" or "\u3040" <= char <= "\u30ff" or "\u4e00" <= char <= "\u9fff" for char in value)


def card_source(candidate: dict[str, Any]) -> str:
    raw = clean(candidate.get("source_name") or candidate.get("original_source_name") or "Source")
    mapped = SOURCE_NAME_MAP.get(raw, raw)
    if contains_non_english_public_text(mapped):
        return "Official source"
    return mapped or "Source"


def card_date(candidate: dict[str, Any]) -> str:
    for key in ("original_published_at", "original_collected_at", "created_at", "updated_at"):
        raw = clean(candidate.get(key))
        if not raw:
            continue
        value = raw.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(value).date().isoformat()
        except ValueError:
            match = re.search(r"\d{4}-\d{2}-\d{2}", raw)
            if match:
                return match.group(0)
    return datetime.now(timezone.utc).date().isoformat()


def card_footer(candidate: dict[str, Any]) -> str:
    raw_payload = candidate.get("raw_payload") if isinstance(candidate.get("raw_payload"), dict) else {}
    requested = clean(candidate.get("footer_text") or raw_payload.get("footer_text"))
    if requested and not contains_url(requested) and not contains_forbidden_text(requested) and not contains_non_english_public_text(requested):
        return requested[:80]
    return DEFAULT_FOOTER_TEXT


def is_single_living_source_without_topic_evidence(candidate: dict[str, Any]) -> bool:
    source_domain = clean(candidate.get("source_domain")).upper()
    content_type = clean(candidate.get("content_type")).upper()
    if source_domain != "LIVING_INFO" and content_type != "LIVING_GUIDE":
        return False
    if has_topic_or_fact_evidence(candidate):
        return False
    raw_payload = candidate.get("raw_payload") if isinstance(candidate.get("raw_payload"), dict) else {}
    raw_ref_table = clean(candidate.get("raw_ref_table") or raw_payload.get("raw_ref_table")).lower()
    if raw_ref_table.startswith("social_news."):
        return True
    source_kind = clean(raw_payload.get("source_kind") or raw_payload.get("source_role") or raw_payload.get("content_origin")).lower()
    if source_kind in {"news", "article", "source_signal", "evidence", "single_source"}:
        return True
    return False


def has_topic_or_fact_evidence(candidate: dict[str, Any]) -> bool:
    raw_payload = candidate.get("raw_payload") if isinstance(candidate.get("raw_payload"), dict) else {}
    for key in ("topic_key", "topic_cluster_id", "fact_point_id", "card_point_id"):
        if clean(candidate.get(key) or raw_payload.get(key)):
            return True
    for key in ("source_spread_count", "related_source_count", "group_item_count"):
        if parse_int(candidate.get(key, raw_payload.get(key))) >= 2:
            return True
    for key in ("usable_point_count", "fact_point_count", "card_point_count"):
        if parse_int(candidate.get(key, raw_payload.get(key))) >= MIN_VALID_BULLETS:
            return True
    return False


def invalid_card_point_reason(point: str, title: str, source: str, candidate: dict[str, Any]) -> str:
    cleaned = clean(point)
    if len(cleaned) < 12 or len(cleaned.split()) < 3:
        return "CARD_POINT_TOO_SHORT"
    if contains_url(cleaned):
        return "CARD_POINT_URL_ECHO"
    if contains_forbidden_text(cleaned):
        return "CARD_POINT_FORBIDDEN_SYSTEM_TEXT"
    normalized = normalized_card_point(cleaned)
    title_norm = normalized_card_point(title)
    source_norm = normalized_card_point(source)
    if title_norm and normalized == title_norm:
        return "CARD_POINT_TITLE_ECHO"
    if title_norm and mostly_repeats_title(normalized, title_norm):
        return "CARD_POINT_TITLE_ECHO"
    if source_norm and normalized in {source_norm, f"source {source_norm}", f"from {source_norm}", f"via {source_norm}"}:
        return "CARD_POINT_SOURCE_ECHO"
    if source_norm and normalized.replace("source ", "").strip() == source_norm:
        return "CARD_POINT_SOURCE_ECHO"
    if source_norm and title_norm and title_norm in normalized and source_norm in normalized:
        return "CARD_POINT_TITLE_ECHO"
    category_norm = normalized_card_point(candidate.get("category"))
    if normalized in {"source", "official source", "category", category_norm}:
        return "CARD_POINT_GENERIC_LABEL"
    return ""


def normalized_card_point(value: Any) -> str:
    text = normalize_plain_text(str(value or "")).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"[^0-9a-z]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def mostly_repeats_title(point_norm: str, title_norm: str) -> bool:
    point_tokens = set(point_norm.split())
    title_tokens = set(title_norm.split())
    if not point_tokens or not title_tokens:
        return False
    overlap = len(point_tokens & title_tokens) / max(1, len(title_tokens))
    length_close = len(point_norm) <= int(len(title_norm) * 1.35) + 8
    return overlap >= 0.8 and length_close


def contains_url(value: str) -> bool:
    text = clean(value).lower()
    return bool(re.search(r"https?://|www\.|facebook\.com/profile\.php|facebook\.com/", text))


def valid_link(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def preferred_font_path(bold: bool = False) -> str:
    candidates = [
        "C:/Windows/Fonts/NotoSans-Regular.ttf",
        "C:/Windows/Fonts/NotoSans-Bold.ttf" if bold else "C:/Windows/Fonts/NotoSans-Regular.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return path
    return "arial.ttf"


def load_template_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def clean(value: Any) -> str:
    return normalize_plain_text(str(value or "")).strip()


def parse_score(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def parse_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
