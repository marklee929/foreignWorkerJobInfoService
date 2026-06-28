from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from foreign_worker_life_info_collector.living_info.models import LivingNormalizedItem, LivingSourceItem
from foreign_worker_life_info_collector.living_info.repository import LivingInfoRepository


DEFAULT_PREVIEW_PATH = (
    Path(__file__).resolve().parents[1] / "storage" / "generated" / "living_info" / "backfill_preview.json"
)
DEFAULT_OUTPUT_PATH = (
    Path(__file__).resolve().parents[1] / "storage" / "generated" / "living_info" / "backfill_apply_result.json"
)
DEFAULT_ALLOWED_ACTIONS = {"MIGRATE_SOURCE_ITEM", "MIGRATE_NORMALIZED_ITEM"}


@dataclass
class BackfillPlan:
    source_item: LivingSourceItem
    normalized_item: LivingNormalizedItem | None
    preview_row: dict[str, Any]
    action: str


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    preview_path = Path(args.preview)
    output_path = Path(args.output)
    rows = load_preview(preview_path)
    candidate_ids = parse_ids(args.candidate_ids)
    source_only_candidate_ids = parse_ids(args.source_only_candidate_ids)
    allowed_actions = parse_actions(args.allowed_actions)
    if not candidate_ids and not source_only_candidate_ids and not args.allow_all_matching:
        result = {
            "ok": False,
            "status": "APPROVED_CANDIDATE_IDS_REQUIRED",
            "message": "--candidate-ids or --source-only-candidate-ids is required unless --allow-all-matching is explicitly set.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 2

    selected = select_rows(
        rows,
        candidate_ids,
        source_only_candidate_ids,
        allowed_actions,
        args.allow_all_matching,
        args.limit,
    )
    plans, skipped = build_plans(selected)
    repo = LivingInfoRepository()
    before_counts = repo.counts()
    inserted: list[dict[str, Any]] = []
    if args.execute:
        for plan in plans:
            source_item_id = repo.upsert_source_item(plan.source_item)
            normalized_item_id = 0
            if plan.normalized_item:
                plan.normalized_item.source_item_id = source_item_id
                normalized_item_id = repo.upsert_normalized_item(plan.normalized_item)
            inserted.append(
                {
                    "content_candidate_id": plan.preview_row.get("content_candidate_id"),
                    "action": plan.action,
                    "source_item_id": source_item_id,
                    "normalized_item_id": normalized_item_id,
                }
            )
    after_counts = repo.counts()
    result = {
        "ok": True,
        "dry_run": not args.execute,
        "execute": bool(args.execute),
        "preview_path": str(preview_path),
        "allowed_actions": sorted(allowed_actions),
        "candidate_ids": sorted(candidate_ids),
        "source_only_candidate_ids": sorted(source_only_candidate_ids),
        "allow_all_matching": bool(args.allow_all_matching),
        "limit": args.limit,
        "before_counts": before_counts,
        "after_counts": after_counts,
        "selected_count": len(selected),
        "planned_count": len(plans),
        "skipped_count": len(skipped),
        "inserted_count": len(inserted),
        "planned": [public_plan(plan) for plan in plans],
        "skipped": skipped,
        "inserted": inserted,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(public_result(result, output_path), ensure_ascii=False, indent=2))
    return 0


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manual/dev-only LIVING_INFO backfill from preview output.")
    parser.add_argument("--preview", default=str(DEFAULT_PREVIEW_PATH), help="Path to backfill_preview.json.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH), help="Path to write apply/dry-run result JSON.")
    parser.add_argument("--candidate-ids", default="", help="Comma-separated approved content_candidate_id list.")
    parser.add_argument(
        "--source-only-candidate-ids",
        default="",
        help="Comma-separated approved content_candidate_id list to migrate as source_item only.",
    )
    parser.add_argument(
        "--allowed-actions",
        default=",".join(sorted(DEFAULT_ALLOWED_ACTIONS)),
        help="Comma-separated approved preview actions.",
    )
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--allow-all-matching", action="store_true", help="Explicitly allow all rows matching allowed actions.")
    parser.add_argument("--execute", action="store_true", help="Actually write to living_info tables. Default is dry-run.")
    return parser.parse_args(argv)


def load_preview(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("Preview JSON must contain a list.")
    return [row for row in data if isinstance(row, dict)]


def parse_ids(raw: str) -> set[int]:
    ids: set[int] = set()
    for part in (raw or "").replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        ids.add(int(part))
    return ids


def parse_actions(raw: str) -> set[str]:
    actions = {part.strip() for part in (raw or "").replace(";", ",").split(",") if part.strip()}
    return actions or set(DEFAULT_ALLOWED_ACTIONS)


def select_rows(
    rows: list[dict[str, Any]],
    candidate_ids: set[int],
    source_only_candidate_ids: set[int],
    allowed_actions: set[str],
    allow_all_matching: bool,
    limit: int,
) -> list[dict[str, Any]]:
    selected = []
    limit = max(1, min(int(limit or 50), 500))
    for row in rows:
        action = str(row.get("backfill_action") or "")
        content_candidate_id = int(row.get("content_candidate_id") or 0)
        if content_candidate_id in source_only_candidate_ids:
            selected_row = dict(row)
            selected_row["backfill_action"] = "MIGRATE_SOURCE_ITEM"
            selected_row["source_only_override_yn"] = True
            selected.append(selected_row)
            if len(selected) >= limit:
                break
            continue
        if action not in allowed_actions:
            continue
        if not allow_all_matching and content_candidate_id not in candidate_ids:
            continue
        selected.append(row)
        if len(selected) >= limit:
            break
    return selected


def build_plans(rows: list[dict[str, Any]]) -> tuple[list[BackfillPlan], list[dict[str, Any]]]:
    plans: list[BackfillPlan] = []
    skipped: list[dict[str, Any]] = []
    for row in rows:
        valid, reason = validate_row(row)
        if not valid:
            skipped.append(
                {
                    "content_candidate_id": row.get("content_candidate_id"),
                    "action": row.get("backfill_action"),
                    "reason": reason,
                }
            )
            continue
        source_item = row_to_source_item(row)
        normalized_item = row_to_normalized_item(row) if row.get("backfill_action") == "MIGRATE_NORMALIZED_ITEM" else None
        plans.append(
            BackfillPlan(
                source_item=source_item,
                normalized_item=normalized_item,
                preview_row=row,
                action=str(row.get("backfill_action") or ""),
            )
        )
    return plans, skipped


def validate_row(row: dict[str, Any]) -> tuple[bool, str]:
    if str(row.get("backfill_action") or "") not in DEFAULT_ALLOWED_ACTIONS:
        return False, "action_not_allowed"
    effective_url = str(row.get("effective_url") or row.get("source_url") or row.get("canonical_url") or "").strip()
    if not effective_url:
        return False, "missing_effective_url"
    duplicate_key = str(row.get("duplicate_key") or "").strip()
    if not duplicate_key:
        return False, "missing_duplicate_key"
    title = str(row.get("raw_title") or "").strip()
    if not title:
        return False, "missing_title"
    return True, ""


def row_to_source_item(row: dict[str, Any]) -> LivingSourceItem:
    effective_url = str(row.get("effective_url") or row.get("source_url") or row.get("canonical_url") or "")
    return LivingSourceItem(
        source_url=str(row.get("source_url") or effective_url),
        canonical_url=str(row.get("canonical_url") or effective_url),
        publishable_link_url=effective_url,
        source_name=str(row.get("source_name") or ""),
        source_type=str(row.get("source_type") or "DISCOVERY"),
        language=str(row.get("language") or "en"),
        raw_title=str(row.get("raw_title") or ""),
        raw_summary=str(row.get("raw_summary") or ""),
        raw_body="",
        published_at=str(row.get("published_at") or ""),
        collected_at=str(row.get("collected_at") or ""),
        source_trust_level=str(row.get("source_trust_level") or "DISCOVERY"),
        privacy_risk_level=str(row.get("privacy_risk_level") or "LOW"),
        duplicate_key=str(row.get("duplicate_key") or ""),
        content_hash=str(row.get("content_hash") or ""),
        source_status="COLLECTED",
        raw_ref_table="content.content_candidate",
        raw_ref_id=int(row.get("content_candidate_id") or 0),
        raw_payload={
            "source": "living_info_backfill_preview",
            "preview_row": row,
        },
    )


def row_to_normalized_item(row: dict[str, Any]) -> LivingNormalizedItem:
    return LivingNormalizedItem(
        normalized_primary_category=str(row.get("normalized_primary_category") or ""),
        normalized_secondary_category=str(row.get("normalized_secondary_category") or ""),
        source_usage=str(row.get("source_usage") or "SOURCE_EVIDENCE"),
        info_signal_type=str(row.get("info_signal_type") or "INFORMATIONAL"),
        target_user=str(row.get("target_user") or "FOREIGN_RESIDENTS_IN_KOREA"),
        action_type=str(row.get("action_type") or ""),
        topic_key_candidate=str(row.get("topic_key_candidate") or ""),
        validation_needed_yn=bool_to_yn(row.get("validation_needed_yn")),
        validation_source_type=str(row.get("validation_source_type") or ""),
        actionability_score=to_float(row.get("actionability_score")),
        repeatability_score=to_float(row.get("repeatability_score")),
        source_reliability_score=to_float(row.get("source_reliability_score")),
        normalization_confidence=to_float(row.get("normalization_confidence")),
        normalization_reason=str(row.get("normalization_reason") or ""),
        status="NORMALIZED",
    )


def bool_to_yn(value: Any) -> str:
    if isinstance(value, bool):
        return "Y" if value else "N"
    return "Y" if str(value).strip().lower() in {"1", "true", "y", "yes"} else "N"


def to_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def public_plan(plan: BackfillPlan) -> dict[str, Any]:
    return {
        "content_candidate_id": plan.preview_row.get("content_candidate_id"),
        "action": plan.action,
        "source_url": plan.source_item.source_url,
        "duplicate_key": plan.source_item.duplicate_key,
        "normalized_primary_category": plan.normalized_item.normalized_primary_category if plan.normalized_item else "",
        "will_insert_normalized_item": plan.normalized_item is not None,
    }


def public_result(result: dict[str, Any], output_path: Path) -> dict[str, Any]:
    return {
        "ok": result["ok"],
        "dry_run": result["dry_run"],
        "execute": result["execute"],
        "output_path": str(output_path),
        "before_counts": result["before_counts"],
        "after_counts": result["after_counts"],
        "selected_count": result["selected_count"],
        "planned_count": result["planned_count"],
        "skipped_count": result["skipped_count"],
        "inserted_count": result["inserted_count"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
