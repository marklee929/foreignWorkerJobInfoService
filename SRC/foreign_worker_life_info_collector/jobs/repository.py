from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..storage.db.postgres import connect, load_env_file


DEFAULT_SETTINGS = {
    "display": 100,
    "startPageFrom": 1,
    "startPageTo": 10,
    "sortOrderBy": "DESC",
    "intervalMinutes": 60,
    "filterEnabled": False,
    "schedulerEnabled": False,
}
MIGRATION_PATH = Path(__file__).resolve().parents[1] / "storage" / "db" / "migrations" / "2026_06_02_postgres_runtime_storage.sql"


class JobCollectorRepository:
    def __init__(self) -> None:
        load_env_file()
        self.initialize()

    def initialize(self) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(MIGRATION_PATH.read_text(encoding="utf-8"))
            conn.commit()

    def settings(self) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT display, start_page_from, start_page_to, sort_order_by, interval_minutes, filter_enabled, scheduler_enabled
                    FROM admin.employment_job_collector_settings
                    WHERE id = 1
                    """
                )
                row = cur.fetchone()
        if not row:
            return dict(DEFAULT_SETTINGS)
        return {
            "display": int(row[0]),
            "startPageFrom": int(row[1]),
            "startPageTo": int(row[2]),
            "sortOrderBy": row[3] or "DESC",
            "intervalMinutes": int(row[4]),
            "filterEnabled": bool(row[5]),
            "schedulerEnabled": bool(row[6]),
        }

    def update_settings(self, values: dict[str, Any]) -> dict[str, Any]:
        current = self.settings()
        next_values = {
            "display": int(values.get("display", current["display"])),
            "startPageFrom": int(values.get("startPageFrom", current["startPageFrom"])),
            "startPageTo": int(values.get("startPageTo", current["startPageTo"])),
            "sortOrderBy": str(values.get("sortOrderBy", current["sortOrderBy"]) or "DESC").upper(),
            "intervalMinutes": int(values.get("intervalMinutes", current["intervalMinutes"])),
            "filterEnabled": bool(values.get("filterEnabled", current["filterEnabled"])),
            "schedulerEnabled": bool(values.get("schedulerEnabled", current.get("schedulerEnabled", False))),
        }
        next_values["display"] = max(1, min(next_values["display"], 100))
        next_values["startPageFrom"] = max(1, next_values["startPageFrom"])
        next_values["startPageTo"] = max(next_values["startPageFrom"], next_values["startPageTo"])
        next_values["intervalMinutes"] = max(5, next_values["intervalMinutes"])
        if next_values["sortOrderBy"] not in {"ASC", "DESC"}:
            next_values["sortOrderBy"] = "DESC"

        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE admin.employment_job_collector_settings
                    SET display = %s, start_page_from = %s, start_page_to = %s, sort_order_by = %s,
                        interval_minutes = %s, filter_enabled = %s, scheduler_enabled = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                    """,
                    (
                        next_values["display"],
                        next_values["startPageFrom"],
                        next_values["startPageTo"],
                        next_values["sortOrderBy"],
                        next_values["intervalMinutes"],
                        next_values["filterEnabled"],
                        next_values["schedulerEnabled"],
                    ),
                )
            conn.commit()
        return next_values

    def set_scheduler_enabled(self, enabled: bool) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE admin.employment_job_collector_settings
                    SET scheduler_enabled = %s,
                        scheduler_started_at = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE scheduler_started_at END,
                        scheduler_stopped_at = CASE WHEN %s THEN scheduler_stopped_at ELSE CURRENT_TIMESTAMP END,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = 1
                    """,
                    (enabled, enabled, enabled),
                )
            conn.commit()
        return self.settings()

    def start_run(self, started_at: str, page_from: int, page_to: int, display: int, sort_order_by: str, request_params: dict[str, Any]) -> int:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO admin.employment_job_collector_log
                        (started_at, page_from, page_to, display, sort_order_by, status, request_params_json)
                    VALUES (%s, %s, %s, %s, %s, 'RUNNING', %s::jsonb)
                    RETURNING id
                    """,
                    (started_at, page_from, page_to, display, sort_order_by, json.dumps(request_params, ensure_ascii=False)),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0])

    def finish_run(self, run_id: int, values: dict[str, Any]) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE admin.employment_job_collector_log
                    SET ended_at = %s, total_received = %s, inserted_count = %s, updated_count = %s,
                        skipped_count = %s, failed_count = %s, failed_pages_json = %s::jsonb,
                        status = %s, error_message = %s
                    WHERE id = %s
                    """,
                    (
                        values.get("ended_at"),
                        int(values.get("total_received", 0)),
                        int(values.get("inserted_count", 0)),
                        int(values.get("updated_count", 0)),
                        int(values.get("skipped_count", 0)),
                        int(values.get("failed_count", 0)),
                        json.dumps(values.get("failed_pages", []), ensure_ascii=False),
                        values.get("status", "COMPLETED"),
                        values.get("error_message"),
                        run_id,
                    ),
                )
            conn.commit()

    def upsert_posting(self, posting: dict[str, Any]) -> str:
        wanted_auth_no = str(posting.get("wantedAuthNo") or "").strip()
        if not wanted_auth_no:
            return "skipped"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT smodify_dtm, raw_xml FROM admin.employment_job_posting WHERE wanted_auth_no = %s",
                    (wanted_auth_no,),
                )
                existing = cur.fetchone()
                if existing and (existing[0] or "") == (posting.get("smodifyDtm") or "") and (existing[1] or "") == (posting.get("rawXml") or ""):
                    return "skipped"
                cur.execute(
                    """
                    INSERT INTO admin.employment_job_posting (
                        wanted_auth_no, company, busino, ind_tp_nm, title, sal_tp_nm, sal, min_sal, max_sal,
                        region, holiday_tp_nm, min_edubg, max_edubg, career, reg_dt, close_dt, info_svc,
                        wanted_info_url, wanted_mobile_info_url, zip_cd, strtnm_cd, basic_addr, detail_addr,
                        emp_tp_cd, jobs_cd, smodify_dtm, raw_xml, collected_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT(wanted_auth_no) DO UPDATE SET
                        company = EXCLUDED.company,
                        busino = EXCLUDED.busino,
                        ind_tp_nm = EXCLUDED.ind_tp_nm,
                        title = EXCLUDED.title,
                        sal_tp_nm = EXCLUDED.sal_tp_nm,
                        sal = EXCLUDED.sal,
                        min_sal = EXCLUDED.min_sal,
                        max_sal = EXCLUDED.max_sal,
                        region = EXCLUDED.region,
                        holiday_tp_nm = EXCLUDED.holiday_tp_nm,
                        min_edubg = EXCLUDED.min_edubg,
                        max_edubg = EXCLUDED.max_edubg,
                        career = EXCLUDED.career,
                        reg_dt = EXCLUDED.reg_dt,
                        close_dt = EXCLUDED.close_dt,
                        info_svc = EXCLUDED.info_svc,
                        wanted_info_url = EXCLUDED.wanted_info_url,
                        wanted_mobile_info_url = EXCLUDED.wanted_mobile_info_url,
                        zip_cd = EXCLUDED.zip_cd,
                        strtnm_cd = EXCLUDED.strtnm_cd,
                        basic_addr = EXCLUDED.basic_addr,
                        detail_addr = EXCLUDED.detail_addr,
                        emp_tp_cd = EXCLUDED.emp_tp_cd,
                        jobs_cd = EXCLUDED.jobs_cd,
                        smodify_dtm = EXCLUDED.smodify_dtm,
                        raw_xml = EXCLUDED.raw_xml,
                        collected_at = EXCLUDED.collected_at,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        wanted_auth_no,
                        posting.get("company"),
                        posting.get("busino"),
                        posting.get("indTpNm"),
                        posting.get("title"),
                        posting.get("salTpNm"),
                        posting.get("sal"),
                        posting.get("minSal"),
                        posting.get("maxSal"),
                        posting.get("region"),
                        posting.get("holidayTpNm"),
                        posting.get("minEdubg"),
                        posting.get("maxEdubg"),
                        posting.get("career"),
                        posting.get("regDt"),
                        posting.get("closeDt"),
                        posting.get("infoSvc"),
                        posting.get("wantedInfoUrl"),
                        posting.get("wantedMobileInfoUrl"),
                        posting.get("zipCd"),
                        posting.get("strtnmCd"),
                        posting.get("basicAddr"),
                        posting.get("detailAddr"),
                        posting.get("empTpCd"),
                        posting.get("jobsCd"),
                        posting.get("smodifyDtm"),
                        posting.get("rawXml"),
                        posting.get("collectedAt"),
                    ),
                )
            conn.commit()
        return "updated" if existing else "inserted"

    def recent_logs(self, limit: int = 30, offset: int = 0) -> list[dict[str, Any]]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, started_at, ended_at, page_from, page_to, display, sort_order_by,
                           total_received, inserted_count, updated_count, skipped_count, failed_count,
                           failed_pages_json, status, error_message
                    FROM admin.employment_job_collector_log
                    ORDER BY id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        result = []
        for row in rows:
            item = dict(zip(columns, row))
            failed_pages = item.pop("failed_pages_json") or []
            item["failedPages"] = failed_pages if isinstance(failed_pages, list) else json.loads(failed_pages)
            result.append(item)
        return result

    def latest_log(self) -> dict[str, Any] | None:
        logs = self.recent_logs(limit=1)
        return logs[0] if logs else None

    def list_postings(self, limit: int = 200) -> list[dict[str, Any]]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT wanted_auth_no, company, busino, ind_tp_nm, title, sal_tp_nm, sal, min_sal, max_sal,
                           region, holiday_tp_nm, min_edubg, max_edubg, career, reg_dt, close_dt, info_svc,
                           wanted_info_url, wanted_mobile_info_url, zip_cd, basic_addr, detail_addr,
                           emp_tp_cd, jobs_cd, smodify_dtm, collected_at
                    FROM admin.employment_job_posting
                    ORDER BY collected_at DESC, reg_dt DESC, wanted_auth_no DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [dict(zip(columns, row)) for row in rows]
