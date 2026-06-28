from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from foreign_worker_life_info_collector.storage.db.postgres import (
    connect,
    load_env_file,
    safe_connection_summary,
)


SOURCE_DOMAIN = "LIVING_INFO"
SOCIAL_REF_TABLE = "social_news.candidate"
DEFAULT_LIMIT = 500
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "storage" / "generated" / "living_info"

CONTENT_COLUMNS = (
    "id",
    "source_domain",
    "content_type",
    "priority_group",
    "category",
    "title",
    "summary_en",
    "why_it_matters_en",
    "body_en",
    "source_url",
    "source_name",
    "original_source_url",
    "original_source_name",
    "original_title",
    "original_published_at",
    "original_collected_at",
    "image_url",
    "link_url",
    "hashtags",
    "language",
    "quality_score",
    "relevance_score",
    "practical_value_score",
    "urgency_score",
    "freshness_score",
    "source_reliability_score",
    "content_potential_score",
    "rotation_score",
    "final_publish_score",
    "sensitive_yn",
    "review_required_yn",
    "review_reason",
    "status",
    "publish_attempt_count",
    "last_publish_error",
    "next_retry_at",
    "published_at",
    "facebook_post_id",
    "facebook_post_url",
    "created_at",
    "updated_at",
    "content_created_at",
    "content_updated_at",
    "raw_ref_table",
    "raw_ref_id",
    "raw_payload",
)

SOCIAL_COLUMNS = (
    "id",
    "source_type",
    "source_url",
    "canonical_url",
    "source_name",
    "publisher_name",
    "title",
    "summary",
    "content",
    "language",
    "category",
    "content_category",
    "content_priority_group",
    "settlement_relevance_score",
    "practical_value_score",
    "category_rotation_score",
    "content_potential_score",
    "category_selection_reason",
    "is_sensitive",
    "review_required_reason",
    "hash_key",
    "similarity_key",
    "short_summary",
    "key_points",
    "relevance_reason",
    "risk_notes",
    "evaluation_score",
    "duplicate_risk_score",
    "foreign_worker_relevance_score",
    "korea_relevance_score",
    "visa_or_labor_policy_score",
    "freshness_score",
    "source_reliability_score",
    "facebook_post_suitability_score",
    "selection_reason",
    "skip_reason",
    "duplicate_group_id",
    "facebook_post_url",
    "facebook_post_id",
    "publish_status",
    "status",
    "collected_at",
    "published_at",
    "related_source_count",
    "duplicate_count",
    "group_item_count",
    "last_seen_at",
    "is_representative",
)

PREVIEW_FIELDS = (
    "content_candidate_id",
    "raw_ref_table",
    "raw_ref_id",
    "source_url",
    "canonical_url",
    "effective_url",
    "source_name",
    "source_type",
    "language",
    "raw_title",
    "raw_summary",
    "raw_body_available_yn",
    "published_at",
    "collected_at",
    "source_trust_level",
    "privacy_risk_level",
    "duplicate_key",
    "content_hash",
    "normalized_primary_category",
    "normalized_secondary_category",
    "source_usage",
    "info_signal_type",
    "target_user",
    "action_type",
    "topic_key_candidate",
    "validation_needed_yn",
    "validation_source_type",
    "actionability_score",
    "repeatability_score",
    "source_reliability_score",
    "normalization_confidence",
    "normalization_reason",
    "backfill_action",
    "backfill_reason",
    "current_category",
    "current_source_domain",
    "current_content_type",
    "current_status",
    "final_publish_score",
    "quality_score",
    "practical_value_score",
    "facebook_post_url",
    "published_state_yn",
)

CATEGORY_MAP = {
    "housing": ("HOUSING", "housing"),
    "rent": ("HOUSING", "rent"),
    "banking": ("BANKING_FINANCE", "banking"),
    "finance": ("BANKING_FINANCE", "finance"),
    "bank": ("BANKING_FINANCE", "banking"),
    "healthcare": ("HEALTHCARE", "healthcare"),
    "health": ("HEALTHCARE", "healthcare"),
    "insurance": ("HEALTHCARE", "insurance"),
    "transportation": ("TRANSPORTATION", "transportation"),
    "transport": ("TRANSPORTATION", "transportation"),
    "telecom": ("TELECOM", "telecom"),
    "mobile": ("TELECOM", "mobile"),
    "education": ("EDUCATION_LANGUAGE", "education"),
    "korean_language": ("EDUCATION_LANGUAGE", "korean_language"),
    "language": ("EDUCATION_LANGUAGE", "language"),
    "local_support": ("REGIONAL_SUPPORT", "local_support"),
    "local_community": ("REGIONAL_SUPPORT", "local_community"),
    "settlement_life": ("DAILY_LIFE", "settlement_life"),
    "settlement": ("DAILY_LIFE", "settlement"),
    "daily_life": ("DAILY_LIFE", "daily_life"),
    "living": ("DAILY_LIFE", "living"),
    "safety": ("SAFETY_SCAM", "safety"),
}

LOW_VALUE_CATEGORIES = {
    "travel",
    "tourism",
    "culture",
    "entertainment",
    "local_events",
    "event",
    "lifestyle",
    "sports",
    "stock",
    "crypto",
    "politics",
}

SYSTEM_TEXT_PATTERNS = (
    "saved article body is missing",
    "no article body was saved",
    "content unavailable",
    "failed to fetch article",
    "parser error",
    "access denied",
    "ready_to_publish",
    "publish_status",
    "score threshold",
    "current score",
    "candidate queue",
    "admin repost",
)

ACTION_WORDS = (
    "apply",
    "check",
    "register",
    "renew",
    "update",
    "report",
    "call",
    "visit",
    "prepare",
    "confirm",
    "pay",
    "submit",
    "contract",
    "insurance",
    "bank",
    "clinic",
    "hospital",
    "school",
    "address",
    "visa",
    "housing",
    "rent",
    "phone",
    "mobile",
    "support center",
)


@dataclass(frozen=True)
class OutputPaths:
    preview_json: Path | None
    preview_csv: Path | None
    summary_json: Path


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    rows = sample_rows() if args.sample else fetch_living_info_rows(args.limit)
    previews = build_previews(rows)
    summary = build_summary(previews, args.sample)
    paths = write_outputs(previews, summary, output_dir, args.format)
    result = {
        "ok": True,
        "sample_mode": bool(args.sample),
        "connection": "sample" if args.sample else safe_connection_summary(),
        "row_count": len(previews),
        "output_dir": str(output_dir),
        "preview_json": str(paths.preview_json) if paths.preview_json is not None else "",
        "preview_csv": str(paths.preview_csv) if paths.preview_csv is not None else "",
        "summary_json": str(paths.summary_json),
        "summary": summary,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preview LIVING_INFO content candidate backfill actions.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--format", choices=("json", "csv", "both"), default="both")
    parser.add_argument("--sample", action="store_true", help="Use built-in rows without opening PostgreSQL.")
    return parser.parse_args(argv)


def fetch_living_info_rows(limit: int) -> list[dict[str, dict[str, Any]]]:
    load_env_file()
    limit = max(1, min(int(limit or DEFAULT_LIMIT), 5000))
    with connect() as conn:
        with conn.cursor() as cur:
            content_columns = table_columns(cur, "content", "content_candidate")
            if not content_columns:
                raise RuntimeError("content.content_candidate table was not found.")
            social_exists = table_exists(cur, "social_news", "candidate")
            social_columns = table_columns(cur, "social_news", "candidate") if social_exists else set()
            content_select = [name for name in CONTENT_COLUMNS if name in content_columns]
            social_select = [name for name in SOCIAL_COLUMNS if name in social_columns]
            fragments = [f"c.{name} AS content__{name}" for name in content_select]
            join_sql = ""
            params: list[Any] = [SOURCE_DOMAIN]
            if social_select and {"raw_ref_table", "raw_ref_id"}.issubset(content_columns):
                fragments.extend(f"s.{name} AS social__{name}" for name in social_select)
                join_sql = (
                    " LEFT JOIN social_news.candidate s"
                    " ON c.raw_ref_table = %s AND c.raw_ref_id = s.id"
                )
                params.insert(0, SOCIAL_REF_TABLE)
            order_sql = order_clause(content_columns)
            sql = (
                f"SELECT {', '.join(fragments)}"
                " FROM content.content_candidate c"
                f"{join_sql}"
                " WHERE c.source_domain = %s"
                f" {order_sql}"
                " LIMIT %s"
            )
            params.append(limit)
            cur.execute(sql, tuple(params))
            names = [column.name for column in cur.description]
            fetched = cur.fetchall()
    return [split_joined_row(dict(zip(names, row))) for row in fetched]


def table_exists(cur: Any, schema: str, table: str) -> bool:
    cur.execute(
        """
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_name = %s
        LIMIT 1
        """,
        (schema, table),
    )
    return cur.fetchone() is not None


def table_columns(cur: Any, schema: str, table: str) -> set[str]:
    cur.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        """,
        (schema, table),
    )
    return {str(row[0]) for row in cur.fetchall()}


def order_clause(columns: set[str]) -> str:
    if {"original_collected_at", "updated_at", "created_at", "id"}.issubset(columns):
        return "ORDER BY COALESCE(c.original_collected_at, c.updated_at, c.created_at) DESC NULLS LAST, c.id DESC"
    if {"updated_at", "id"}.issubset(columns):
        return "ORDER BY c.updated_at DESC NULLS LAST, c.id DESC"
    if "id" in columns:
        return "ORDER BY c.id DESC"
    return ""


def split_joined_row(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    content: dict[str, Any] = {}
    social: dict[str, Any] = {}
    for key, value in row.items():
        if key.startswith("content__"):
            content[key.removeprefix("content__")] = value
        elif key.startswith("social__"):
            social[key.removeprefix("social__")] = value
    return {"content": content, "social": social}


def build_previews(rows: list[dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    previews = [classify_row(row.get("content", {}), row.get("social", {})) for row in rows]
    apply_duplicate_actions(previews)
    return [{key: normalize_json_value(item.get(key, "")) for key in PREVIEW_FIELDS} for item in previews]


def classify_row(content: dict[str, Any], social: dict[str, Any]) -> dict[str, Any]:
    title = first_text(content.get("title"), content.get("original_title"), social.get("title"))
    summary = first_text(content.get("summary_en"), social.get("short_summary"), social.get("summary"))
    body = first_text(content.get("body_en"), social.get("content"))
    source_name = first_text(content.get("source_name"), content.get("original_source_name"), social.get("source_name"), social.get("publisher_name"))
    source_url = first_text(content.get("source_url"), content.get("original_source_url"), social.get("source_url"))
    canonical_url = first_text(social.get("canonical_url"), content.get("link_url"), content.get("original_source_url"), source_url)
    effective_url = first_text(canonical_url, source_url, content.get("link_url"))
    category = normalize_token(first_text(content.get("category"), social.get("content_category"), social.get("category")))
    normalized_primary, normalized_secondary = normalized_category(category, f"{title} {summary} {body}")
    current_status = first_text(content.get("status"))
    raw_ref_table = first_text(content.get("raw_ref_table"))
    raw_ref_id = content.get("raw_ref_id") or ""
    text_blob = " ".join([title, summary, body, source_name, effective_url]).strip()
    usable_url = is_usable_url(effective_url)
    low_value = is_low_value(category, text_blob, normalized_primary)
    trust_level = source_trust_level(source_name, effective_url)
    validation_source = validation_source_type(trust_level)
    actionability = actionability_score(category, text_blob, content)
    repeatability = repeatability_score(normalized_primary, text_blob)
    reliability = max(to_float(content.get("source_reliability_score")), to_float(social.get("source_reliability_score")), reliability_score(trust_level))
    body_available = bool(body.strip())
    content_hash = stable_hash("|".join([title, summary, body, effective_url]))
    duplicate_key = build_duplicate_key(effective_url, title, source_name, summary, raw_ref_table, raw_ref_id)
    source_type = first_text(social.get("source_type"), trust_level.lower())
    published_state = bool(content.get("published_at") or content.get("facebook_post_url") or social.get("published_at") or social.get("facebook_post_url"))

    source_usage = determine_source_usage(normalized_primary, trust_level, actionability, low_value, text_blob)
    info_type = determine_info_signal_type(normalized_primary, trust_level, low_value, source_type)
    confidence = normalization_confidence(usable_url, normalized_primary, low_value, actionability, trust_level)
    action, reason = determine_backfill_action(
        title=title,
        summary=summary,
        body=body,
        effective_url=effective_url,
        text_blob=text_blob,
        low_value=low_value,
        normalized_primary=normalized_primary,
        actionability=actionability,
        repeatability=repeatability,
        trust_level=trust_level,
        current_status=current_status,
        published_state=published_state,
    )
    if action == "LOW_VALUE_ARCHIVE":
        source_usage = "LOW_VALUE_ARCHIVE"
        info_type = "LOW_VALUE_NOISE"
    elif action == "DO_NOT_MIGRATE":
        source_usage = "BLOCK_PUBLIC_CONTENT"
    elif action == "NEEDS_MANUAL_REVIEW":
        source_usage = "TEXT_REVIEW_ONLY"

    return {
        "content_candidate_id": content.get("id") or "",
        "raw_ref_table": raw_ref_table,
        "raw_ref_id": raw_ref_id,
        "source_url": source_url,
        "canonical_url": canonical_url,
        "effective_url": effective_url,
        "source_name": source_name,
        "source_type": source_type,
        "language": first_text(content.get("language"), social.get("language"), "en"),
        "raw_title": title,
        "raw_summary": summary,
        "raw_body_available_yn": body_available,
        "published_at": first_text(content.get("published_at"), social.get("published_at")),
        "collected_at": first_text(content.get("original_collected_at"), social.get("collected_at"), content.get("created_at")),
        "source_trust_level": trust_level,
        "privacy_risk_level": privacy_risk_level(text_blob),
        "duplicate_key": duplicate_key,
        "content_hash": content_hash,
        "normalized_primary_category": normalized_primary,
        "normalized_secondary_category": normalized_secondary,
        "source_usage": source_usage,
        "info_signal_type": info_type,
        "target_user": "FOREIGN_RESIDENTS_IN_KOREA",
        "action_type": action_type(normalized_primary, text_blob),
        "topic_key_candidate": topic_key(normalized_primary, title, summary),
        "validation_needed_yn": validation_needed(action, trust_level, normalized_primary, text_blob),
        "validation_source_type": validation_source,
        "actionability_score": actionability,
        "repeatability_score": repeatability,
        "source_reliability_score": reliability,
        "normalization_confidence": confidence,
        "normalization_reason": normalization_reason(normalized_primary, category, trust_level, actionability),
        "backfill_action": action,
        "backfill_reason": reason,
        "current_category": category,
        "current_source_domain": first_text(content.get("source_domain")),
        "current_content_type": first_text(content.get("content_type")),
        "current_status": current_status,
        "final_publish_score": to_float(content.get("final_publish_score")),
        "quality_score": to_float(content.get("quality_score")),
        "practical_value_score": to_float(content.get("practical_value_score")),
        "facebook_post_url": first_text(content.get("facebook_post_url"), social.get("facebook_post_url")),
        "published_state_yn": published_state,
        "_usable_url": usable_url,
        "_completeness": len(summary) + len(body),
        "_rank_time": first_text(content.get("original_collected_at"), social.get("collected_at"), content.get("updated_at"), content.get("created_at")),
    }


def determine_backfill_action(
    *,
    title: str,
    summary: str,
    body: str,
    effective_url: str,
    text_blob: str,
    low_value: bool,
    normalized_primary: str,
    actionability: float,
    repeatability: float,
    trust_level: str,
    current_status: str,
    published_state: bool,
) -> tuple[str, str]:
    if not title and not summary and not body:
        return "DO_NOT_MIGRATE", "No usable title, summary, or body."
    if contains_system_text(text_blob):
        return "DO_NOT_MIGRATE", "System or diagnostic text detected."
    if not effective_url and not source_trace_exists(text_blob):
        return "DO_NOT_MIGRATE", "Missing source link and source trace."
    if low_value:
        return "LOW_VALUE_ARCHIVE", "Low-value travel, lifestyle, politics, economy, or event item."
    if target_country_mismatch(text_blob):
        return "DO_NOT_MIGRATE", "Current item appears outside Korea settlement scope."
    if not is_usable_url(effective_url):
        return "NEEDS_MANUAL_REVIEW", "Missing or weak final source URL."
    if published_state and normalized_primary in {"LOW_VALUE_NOISE", "UNKNOWN"}:
        return "NEEDS_MANUAL_REVIEW", "Already posted but living value is unclear."
    if sensitive_without_strong_source(normalized_primary, trust_level, text_blob):
        return "NEEDS_MANUAL_REVIEW", "Sensitive living domain needs stronger validation source."
    if normalized_primary != "UNKNOWN" and actionability > 0 and repeatability > 0:
        return "MIGRATE_NORMALIZED_ITEM", "Usable living information with source evidence and practical category."
    if current_status == "ARCHIVED":
        return "MIGRATE_SOURCE_ITEM", "Archived item can be preserved as source evidence only."
    return "MIGRATE_SOURCE_ITEM", "Usable source evidence, normalization confidence is limited."


def apply_duplicate_actions(previews: list[dict[str, Any]]) -> None:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in previews:
        key = str(item.get("duplicate_key") or "")
        if key:
            groups[f"duplicate:{key}"].append(item)
        raw_ref_table = str(item.get("raw_ref_table") or "")
        raw_ref_id = str(item.get("raw_ref_id") or "")
        if raw_ref_table and raw_ref_id:
            groups[f"raw:{raw_ref_table}:{raw_ref_id}"].append(item)

    duplicate_ids: set[int] = set()
    for group_items in groups.values():
        if len(group_items) < 2:
            continue
        representative = sorted(group_items, key=representative_rank, reverse=True)[0]
        representative_id = int(representative.get("content_candidate_id") or 0)
        for item in group_items:
            item_id = int(item.get("content_candidate_id") or 0)
            if item_id == representative_id or item_id in duplicate_ids:
                continue
            if item.get("backfill_action") == "DO_NOT_MIGRATE":
                continue
            item["backfill_action"] = "DUPLICATE_SKIP"
            item["backfill_reason"] = f"Duplicate of representative content_candidate_id {representative_id}."
            item["source_usage"] = "SOURCE_EVIDENCE"
            item["validation_needed_yn"] = True
            duplicate_ids.add(item_id)


def representative_rank(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        bool(item.get("_usable_url")),
        str(item.get("current_status") or "") != "ARCHIVED",
        to_float(item.get("final_publish_score")),
        to_float(item.get("quality_score")),
        int(item.get("_completeness") or 0),
        str(item.get("_rank_time") or ""),
        -int(item.get("content_candidate_id") or 0),
    )


def build_summary(previews: list[dict[str, Any]], sample_mode: bool) -> dict[str, Any]:
    action_counts = Counter(str(item.get("backfill_action") or "") for item in previews)
    category_counts = Counter(str(item.get("normalized_primary_category") or "") for item in previews)
    status_counts = Counter(str(item.get("current_status") or "") for item in previews)
    url_counts = Counter(str(item.get("effective_url") or "") for item in previews if item.get("effective_url"))
    duplicate_url_groups = {url: count for url, count in url_counts.items() if count > 1}
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_mode": sample_mode,
        "source_domain": SOURCE_DOMAIN,
        "total_rows_inspected": len(previews),
        "action_counts": dict(sorted(action_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "status_counts": dict(sorted(status_counts.items())),
        "duplicate_url_group_count": len(duplicate_url_groups),
        "duplicate_url_row_count": sum(duplicate_url_groups.values()),
        "missing_url_count": sum(1 for item in previews if not item.get("effective_url")),
        "low_value_category_count": action_counts.get("LOW_VALUE_ARCHIVE", 0),
        "already_posted_count": sum(1 for item in previews if item.get("published_state_yn")),
        "manual_review_count": action_counts.get("NEEDS_MANUAL_REVIEW", 0),
        "duplicate_skip_count": action_counts.get("DUPLICATE_SKIP", 0),
        "do_not_migrate_count": action_counts.get("DO_NOT_MIGRATE", 0),
    }


def write_outputs(previews: list[dict[str, Any]], summary: dict[str, Any], output_dir: Path, output_format: str) -> OutputPaths:
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_json = output_dir / "backfill_preview.json"
    preview_csv = output_dir / "backfill_preview.csv"
    summary_json = output_dir / "backfill_summary.json"
    if output_format in {"json", "both"}:
        preview_json.write_text(json.dumps(previews, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        preview_json = None
    if output_format in {"csv", "both"}:
        with preview_csv.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(PREVIEW_FIELDS))
            writer.writeheader()
            writer.writerows(previews)
    else:
        preview_csv = None
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return OutputPaths(preview_json=preview_json, preview_csv=preview_csv, summary_json=summary_json)


def sample_rows() -> list[dict[str, dict[str, Any]]]:
    now = datetime(2026, 6, 28, tzinfo=timezone.utc)
    return [
        {
            "content": {
                "id": 1,
                "source_domain": SOURCE_DOMAIN,
                "content_type": "LIVING_GUIDE",
                "category": "housing",
                "title": "How foreign residents can check a housing contract in Korea",
                "summary_en": "Before signing, check deposit terms, address registration, and maintenance fees.",
                "body_en": "Keep receipts and ask a local support center if contract terms are unclear.",
                "source_url": "https://example.go.kr/housing-guide",
                "source_name": "Local Support Center",
                "language": "en",
                "status": "SCORED",
                "final_publish_score": 82,
                "quality_score": 80,
                "practical_value_score": 75,
                "source_reliability_score": 70,
                "created_at": now,
                "raw_ref_table": SOCIAL_REF_TABLE,
                "raw_ref_id": 101,
            },
            "social": {},
        },
        {
            "content": {
                "id": 2,
                "source_domain": SOURCE_DOMAIN,
                "content_type": "LIVING_GUIDE",
                "category": "travel",
                "title": "Bali travel confidence rises after tourism campaign",
                "summary_en": "A tourism campaign promoted travel confidence.",
                "source_url": "https://example.com/bali-travel",
                "source_name": "Travel Wire",
                "status": "SCORED",
                "raw_ref_table": SOCIAL_REF_TABLE,
                "raw_ref_id": 102,
            },
            "social": {},
        },
        {
            "content": {
                "id": 3,
                "source_domain": SOURCE_DOMAIN,
                "content_type": "LIVING_GUIDE",
                "category": "healthcare",
                "title": "Health insurance payment status can affect clinic visits",
                "summary_en": "Foreign residents should confirm payment status before deadlines.",
                "source_url": "",
                "source_name": "NHIS",
                "status": "READY_TO_REVIEW",
                "raw_ref_table": SOCIAL_REF_TABLE,
                "raw_ref_id": 103,
            },
            "social": {},
        },
    ]


def normalized_category(category: str, text_blob: str) -> tuple[str, str]:
    token = normalize_token(category)
    if token in LOW_VALUE_CATEGORIES:
        return "LOW_VALUE_NOISE", token
    if token in CATEGORY_MAP:
        return CATEGORY_MAP[token]
    lowered = text_blob.lower()
    keyword_map = (
        ("HOUSING", "housing", ("housing", "rent", "lease", "deposit", "landlord")),
        ("BANKING_FINANCE", "finance", ("bank", "remittance", "tax", "pension", "wage payment")),
        ("HEALTHCARE", "healthcare", ("health", "clinic", "hospital", "nhis", "insurance")),
        ("TRANSPORTATION", "transportation", ("transport", "subway", "bus", "driver", "license")),
        ("TELECOM", "telecom", ("phone", "mobile", "telecom", "sim card")),
        ("EDUCATION_LANGUAGE", "education", ("school", "education", "korean language", "class")),
        ("REGIONAL_SUPPORT", "local_support", ("support center", "resident center", "local office")),
    )
    for primary, secondary, keywords in keyword_map:
        if any(keyword in lowered for keyword in keywords):
            return primary, secondary
    return "UNKNOWN", token


def determine_source_usage(primary: str, trust_level: str, actionability: float, low_value: bool, text_blob: str) -> str:
    if low_value or primary == "LOW_VALUE_NOISE":
        return "LOW_VALUE_ARCHIVE"
    if is_community_signal(text_blob):
        return "COMMUNITY_SIGNAL"
    if trust_level == "PRIMARY":
        return "OFFICIAL_VALIDATION_SOURCE"
    if primary != "UNKNOWN" and actionability >= 60:
        return "TOPIC_CLUSTER_MATERIAL"
    return "SOURCE_EVIDENCE"


def determine_info_signal_type(primary: str, trust_level: str, low_value: bool, source_type: str) -> str:
    if low_value or primary == "LOW_VALUE_NOISE":
        return "LOW_VALUE_NOISE"
    if trust_level == "PRIMARY":
        return "OFFICIAL_UPDATE"
    if "community" in source_type.lower() or "reddit" in source_type.lower():
        return "TREND_SIGNAL"
    if source_type.lower() in {"news", "rss", "media"}:
        return "NEWS_EVENT"
    return "INFORMATIONAL"


def action_type(primary: str, text_blob: str) -> str:
    lowered = text_blob.lower()
    if "apply" in lowered or "application" in lowered:
        return "APPLICATION_CHECK"
    if "renew" in lowered or "deadline" in lowered:
        return "DEADLINE_CHECK"
    if "contract" in lowered or "deposit" in lowered:
        return "CONTRACT_CHECK"
    if "pay" in lowered or "payment" in lowered:
        return "PAYMENT_CHECK"
    if primary in {"HEALTHCARE", "BANKING_FINANCE", "HOUSING", "TELECOM"}:
        return "PRACTICAL_CHECK"
    return "INFORMATION_REVIEW"


def actionability_score(category: str, text_blob: str, content: dict[str, Any]) -> float:
    base = max(to_float(content.get("practical_value_score")), to_float(content.get("relevance_score")))
    lowered = text_blob.lower()
    keyword_bonus = min(35, sum(7 for keyword in ACTION_WORDS if keyword in lowered))
    category_bonus = 25 if normalize_token(category) in CATEGORY_MAP else 0
    return clamp(max(base, category_bonus + keyword_bonus), 0, 100)


def repeatability_score(primary: str, text_blob: str) -> float:
    if primary in {"HOUSING", "BANKING_FINANCE", "HEALTHCARE", "TRANSPORTATION", "TELECOM", "EDUCATION_LANGUAGE", "REGIONAL_SUPPORT", "DAILY_LIFE"}:
        return 80
    if any(word in text_blob.lower() for word in ("guide", "checklist", "how to", "before", "after")):
        return 65
    return 20


def reliability_score(trust_level: str) -> float:
    return {"PRIMARY": 90, "TRUSTED_MEDIA": 70, "SECONDARY": 60, "DISCOVERY": 35}.get(trust_level, 45)


def normalization_confidence(usable_url: bool, primary: str, low_value: bool, actionability: float, trust_level: str) -> float:
    if low_value:
        return 30
    score = 35
    if usable_url:
        score += 20
    if primary != "UNKNOWN":
        score += 20
    if actionability >= 60:
        score += 15
    if trust_level in {"PRIMARY", "TRUSTED_MEDIA", "SECONDARY"}:
        score += 10
    return clamp(score, 0, 100)


def normalization_reason(primary: str, category: str, trust_level: str, actionability: float) -> str:
    return f"category={category or '-'} mapped_to={primary}; trust={trust_level}; actionability={actionability:.1f}"


def validation_needed(action: str, trust_level: str, primary: str, text_blob: str) -> bool:
    if action in {"NEEDS_MANUAL_REVIEW", "DO_NOT_MIGRATE", "DUPLICATE_SKIP"}:
        return True
    if primary in {"HEALTHCARE", "BANKING_FINANCE", "SAFETY_SCAM"} and trust_level not in {"PRIMARY", "SECONDARY"}:
        return True
    return contains_sensitive_terms(text_blob)


def validation_source_type(trust_level: str) -> str:
    return {
        "PRIMARY": "OFFICIAL_OR_PRIMARY",
        "TRUSTED_MEDIA": "TRUSTED_MEDIA",
        "SECONDARY": "SECONDARY_SOURCE",
        "DISCOVERY": "DISCOVERY_SOURCE",
    }.get(trust_level, "UNKNOWN_SOURCE")


def source_trust_level(source_name: str, url: str) -> str:
    lowered = f"{source_name} {url}".lower()
    if any(term in lowered for term in ("go.kr", "hikorea", "moel", "moj", "nhis", "korea immigration", "government", "ministry")):
        return "PRIMARY"
    if any(term in lowered for term in ("korea herald", "yonhap", "joongang", "korea times", "chosun")):
        return "TRUSTED_MEDIA"
    if any(term in lowered for term in ("support center", "ngo", "university", "hospital", "bank", "insurance")):
        return "SECONDARY"
    if any(term in lowered for term in ("reddit", "community", "blog", "naver", "rss", "search")):
        return "DISCOVERY"
    return "UNKNOWN"


def privacy_risk_level(text_blob: str) -> str:
    lowered = text_blob.lower()
    if re.search(r"\b\d{6}-\d{7}\b", text_blob) or re.search(r"\b\d{3}-\d{3,4}-\d{4}\b", text_blob):
        return "HIGH"
    if any(term in lowered for term in ("passport number", "alien registration number", "phone number", "private message")):
        return "HIGH"
    return "LOW"


def is_low_value(category: str, text_blob: str, primary: str) -> bool:
    token = normalize_token(category)
    lowered = text_blob.lower()
    if token in LOW_VALUE_CATEGORIES or primary == "LOW_VALUE_NOISE":
        return not practical_exception(lowered)
    low_terms = ("travel confidence", "tourism", "tourist", "crypto", "stock market", "election", "president", "festival", "concert", "k-pop")
    return any(term in lowered for term in low_terms) and not practical_exception(lowered)


def practical_exception(lowered: str) -> bool:
    return any(
        term in lowered
        for term in (
            "foreign resident",
            "foreign worker",
            "visa",
            "health insurance",
            "bank account",
            "remittance",
            "housing contract",
            "labor rights",
            "resident center",
        )
    )


def contains_system_text(text_blob: str) -> bool:
    lowered = text_blob.lower()
    return any(pattern in lowered for pattern in SYSTEM_TEXT_PATTERNS)


def target_country_mismatch(text_blob: str) -> bool:
    lowered = text_blob.lower()
    korea_terms = ("korea", "korean", "seoul", "busan", "incheon", "gyeonggi", "foreign residents in korea")
    other_terms = ("bali", "japan", "united states", "u.s.", "america", "australia", "canada")
    return any(term in lowered for term in other_terms) and not any(term in lowered for term in korea_terms)


def sensitive_without_strong_source(primary: str, trust_level: str, text_blob: str) -> bool:
    if primary not in {"HEALTHCARE", "BANKING_FINANCE", "SAFETY_SCAM"}:
        return False
    return contains_sensitive_terms(text_blob) and trust_level not in {"PRIMARY", "SECONDARY"}


def contains_sensitive_terms(text_blob: str) -> bool:
    lowered = text_blob.lower()
    return any(term in lowered for term in ("legal", "lawsuit", "medical", "diagnosis", "tax", "debt", "fraud", "scam", "visa status"))


def source_trace_exists(text_blob: str) -> bool:
    return bool(text_blob.strip())


def is_community_signal(text_blob: str) -> bool:
    lowered = text_blob.lower()
    return any(term in lowered for term in ("reddit", "community", "forum", "comment thread"))


def is_usable_url(url: str) -> bool:
    if not url or url.strip() == "-":
        return False
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    lowered = url.lower()
    if "news.google.com/rss" in lowered or "google.com/search" in lowered:
        return False
    path = parsed.path.strip("/")
    return bool(path) or parsed.netloc.endswith(".go.kr") or "hikorea" in parsed.netloc.lower()


def build_duplicate_key(effective_url: str, title: str, source_name: str, summary: str, raw_ref_table: str, raw_ref_id: Any) -> str:
    if is_usable_url(effective_url):
        return f"url:{normalize_url(effective_url)}"
    if raw_ref_table and raw_ref_id:
        return f"raw:{raw_ref_table}:{raw_ref_id}"
    return "text:" + stable_hash("|".join([normalize_text(title), normalize_text(source_name), normalize_text(summary)]))


def topic_key(primary: str, title: str, summary: str) -> str:
    words = re.findall(r"[a-z0-9]+", f"{title} {summary}".lower())
    meaningful = [word for word in words if len(word) > 3 and word not in {"foreign", "resident", "residents", "korea", "korean", "should", "before", "after"}]
    return f"{primary.lower()}:" + "-".join(meaningful[:6])


def first_text(*values: Any) -> str:
    for value in values:
        text = stringify(value).strip()
        if text:
            return text
    return ""


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def normalize_json_value(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def to_float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def clamp(value: float, minimum: float, maximum: float) -> float:
    return round(max(minimum, min(maximum, value)), 4)


def normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", (value or "").strip().lower()).strip("_")


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip())
    netloc = parsed.netloc.lower()
    path = re.sub(r"/+$", "", parsed.path or "")
    return f"{parsed.scheme.lower()}://{netloc}{path}"


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


if __name__ == "__main__":
    raise SystemExit(main())
