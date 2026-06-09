"""Service layer for official immigration notice operations."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .collectors import default_collectors
from .normalizer import normalize_notice_item
from .repository import ImmigrationNoticeRepository


class ImmigrationNoticeService:
    def __init__(self, repository: ImmigrationNoticeRepository | None = None):
        self.repository = repository or ImmigrationNoticeRepository()
        self.collectors = default_collectors()

    def collect(self, source: str = "", limit: int = 20) -> dict[str, Any]:
        selected = {source: self.collectors[source]} if source and source in self.collectors else self.collectors
        results: list[dict[str, Any]] = []
        total_inserted = 0
        total_updated = 0
        total_failed = 0
        for collector_key, collector in selected.items():
            started_at = datetime.now(timezone.utc).isoformat()
            inserted = 0
            updated = 0
            failed = 0
            requested = 0
            error = ""
            try:
                items = collector.collect(limit=limit)
                requested = len(items)
                for item in items:
                    notice = normalize_notice_item(item)
                    saved, is_inserted = self.repository.upsert_notice(notice)
                    if is_inserted:
                        inserted += 1
                    else:
                        updated += 1
                    if saved.importance_score >= 70 and saved.content_status == "NORMALIZED":
                        self.repository.update_status(saved.id or 0, "READY_TO_REVIEW")
            except Exception as exc:
                failed = 1
                error = str(exc)[:500]
            status = "FAILED" if failed else "SUCCESS"
            self.repository.insert_collect_log(
                {
                    "collector_type": collector.__class__.__name__,
                    "source_name": collector.config.source_name,
                    "status": status,
                    "requested_count": requested,
                    "inserted_count": inserted,
                    "updated_count": updated,
                    "skipped_count": 0,
                    "failed_count": failed,
                    "started_at": started_at,
                    "error_message": error,
                    "request_params": {"source": collector_key, "limit": limit, "list_url": collector.config.list_url},
                }
            )
            total_inserted += inserted
            total_updated += updated
            total_failed += failed
            results.append(
                {
                    "source": collector_key,
                    "source_name": collector.config.source_name,
                    "status": status,
                    "requested_count": requested,
                    "inserted_count": inserted,
                    "updated_count": updated,
                    "failed_count": failed,
                    "error_message": error,
                }
            )
        return {
            "ok": total_failed == 0,
            "source_count": len(selected),
            "inserted_count": total_inserted,
            "updated_count": total_updated,
            "failed_count": total_failed,
            "results": results,
        }

    def summarize(self, notice_id: int) -> dict[str, Any]:
        notice = self.repository.get_notice(notice_id)
        if not notice:
            return {"ok": False, "message": "notice not found"}
        title = notice.get("title_ko", "")
        visa = ", ".join(notice.get("affected_visa_types") or []) or "visa/stay status"
        groups = ", ".join(notice.get("affected_user_groups") or []) or "foreigners in Korea"
        summary = f"- Official notice from {notice.get('source_name')} about {visa}.\n- Check the official source before taking action."
        why = f"- This may affect {groups}.\n- Confirm deadlines, eligibility, and required documents through the official source."
        self._update_summary(notice_id, title, summary, why)
        return {"ok": True, "id": notice_id, "summary_en": summary, "why_it_matters_en": why}

    def _update_summary(self, notice_id: int, title_en: str, summary_en: str, why_it_matters_en: str) -> None:
        from ..storage.db.postgres import connect

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE immigration_info.official_notice
                    SET title_en = %s,
                        summary_en = %s,
                        why_it_matters_en = %s,
                        content_status = CASE
                            WHEN content_status IN ('RAW_COLLECTED', 'NORMALIZED') THEN 'SUMMARIZED'
                            ELSE content_status
                        END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (title_en, summary_en, why_it_matters_en, notice_id),
                )
            conn.commit()

    def approve(self, notice_id: int) -> dict[str, Any]:
        return self.repository.update_status(notice_id, "READY_TO_PUBLISH")

    def publish_stub(self, notice_id: int) -> dict[str, Any]:
        self.repository.insert_publish_log(notice_id, "SKIPPED", "AUTO_PUBLISH_OFF: official immigration notices require review before publishing.")
        return {"ok": False, "id": notice_id, "status": "SKIPPED", "message": "AUTO_PUBLISH_OFF"}
