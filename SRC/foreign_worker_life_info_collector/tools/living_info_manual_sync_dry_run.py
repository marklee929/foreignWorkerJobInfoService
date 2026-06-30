"""Local dry-run for the manual living-info content preparation path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ..content.service import ContentService


DEFAULT_OUTPUT = Path(__file__).resolve().parents[1] / "storage" / "generated" / "living_info" / "manual_sync_dry_run.json"


class DryRunContentRepository:
    def __init__(self) -> None:
        self.payloads: list[dict[str, Any]] = []

    def upsert_candidate(self, payload: dict[str, Any]) -> int:
        self.payloads.append(payload)
        return len(self.payloads)


class DryRunLivingInfoService:
    def __init__(self, mode: str = "ready") -> None:
        self.mode = mode
        self.evidence_requests: list[int] = []

    def list_ready_topic_clusters(self, limit: int = 100) -> list[dict[str, Any]]:
        if self.mode == "empty":
            return []
        return [
            {
                "id": 77,
                "topic_key": "healthcare:insurance-check",
                "primary_category": "HEALTHCARE",
                "secondary_category": "insurance",
                "target_user": "FOREIGN_RESIDENTS_IN_KOREA",
                "action_type": "PRACTICAL_CHECK",
                "source_count": 1,
                "evidence_count": 0 if self.mode == "community-only" else 1,
                "community_signal_count": 5 if self.mode == "community-only" else 0,
                "official_source_count": 0 if self.mode == "community-only" else 1,
                "secondary_source_count": 0,
                "source_spread_count": 1,
                "readiness_score": 82,
                "public_candidate_ready_yn": "Y",
                "validation_status": "VALIDATED",
                "cluster_status": "READY",
            }
        ][:limit]

    def topic_cluster_evidence(self, topic_cluster_id: int) -> list[dict[str, Any]]:
        self.evidence_requests.append(topic_cluster_id)
        if self.mode == "community-only":
            return []
        return [
            {
                "source_item_id": 501,
                "normalized_item_id": 601,
                "source_url": "https://www.nhis.or.kr/guide",
                "canonical_url": "https://www.nhis.or.kr/guide",
                "publishable_link_url": "https://www.nhis.or.kr/guide",
                "source_name": "NHIS",
                "source_trust_level": "PRIMARY",
                "raw_title": "Health insurance guide",
                "raw_summary": "Foreign residents should confirm health insurance status before clinic visits.",
                "actionability_score": 80,
                "source_reliability_score": 95,
                "weight_score": 1,
            }
        ]

    def topic_cluster_to_content_candidate_payload(self, cluster: dict[str, Any], evidence: list[dict[str, Any]]) -> dict[str, Any]:
        from ..living_info.service import topic_cluster_to_content_candidate_payload

        return topic_cluster_to_content_candidate_payload(cluster, evidence)


def run_dry_run(mode: str = "ready") -> dict[str, Any]:
    repository = DryRunContentRepository()
    living_info_service = DryRunLivingInfoService(mode=mode)
    result = ContentService(repository=repository, living_info_service=living_info_service).sync_living_info(limit=10)
    return {
        "ok": True,
        "mode": mode,
        "result": result,
        "created_candidates": repository.payloads,
        "evidence_requests": living_info_service.evidence_requests,
        "external_output": {
            "telegram_sent": False,
            "facebook_posted": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dry-run manual living-info sync without DB writes or external output.")
    parser.add_argument("--mode", choices=("ready", "community-only", "empty"), default="ready")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)

    payload = run_dry_run(mode=args.mode)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output_path), **payload["result"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
