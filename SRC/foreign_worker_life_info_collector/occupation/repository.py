from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..storage.db.postgres import connect, load_env_file


MIGRATION_PATH = Path(__file__).resolve().parents[1] / "storage" / "db" / "migrations" / "2026_06_03_occupation_info.sql"


class OccupationRepository:
    def __init__(self) -> None:
        load_env_file()
        self.initialize()

    def initialize(self) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(MIGRATION_PATH.read_text(encoding="utf-8"))
            conn.commit()

    def start_log(self, collector_type: str, request_params: dict[str, Any]) -> int:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO occupation.collect_log(collector_type, status, request_params)
                    VALUES (%s, 'STARTED', %s::jsonb)
                    RETURNING id
                    """,
                    (collector_type, json.dumps(request_params, ensure_ascii=False)),
                )
                row = cur.fetchone()
            conn.commit()
        return int(row[0])

    def finish_log(self, log_id: int, values: dict[str, Any]) -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE occupation.collect_log
                    SET status = %s,
                        requested_count = %s,
                        inserted_count = %s,
                        updated_count = %s,
                        skipped_count = %s,
                        failed_count = %s,
                        finished_at = CURRENT_TIMESTAMP,
                        error_message = %s
                    WHERE id = %s
                    """,
                    (
                        values.get("status", "SUCCESS"),
                        int(values.get("requested_count", 0)),
                        int(values.get("inserted_count", 0)),
                        int(values.get("updated_count", 0)),
                        int(values.get("skipped_count", 0)),
                        int(values.get("failed_count", 0)),
                        values.get("error_message"),
                        log_id,
                    ),
                )
            conn.commit()

    def save_raw_response(self, collector_type: str, request_url_without_key: str, response_body: str, parsed: bool, error_message: str = "") -> None:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO occupation.raw_api_response
                        (collector_type, request_url_without_key, response_body, parsed_yn, error_message)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (collector_type, request_url_without_key, response_body, "Y" if parsed else "N", error_message or None),
                )
            conn.commit()

    def upsert_job(self, item: dict[str, Any]) -> str:
        code = str(item.get("job_code") or "").strip()
        name = str(item.get("job_name_ko") or "").strip()
        if not code or not name:
            return "skipped"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT raw_response FROM occupation.job_info WHERE source = %s AND job_code = %s", (item.get("source", "employment24"), code))
                existing = cur.fetchone()
                cur.execute(
                    """
                    INSERT INTO occupation.job_info (
                        source, job_code, job_name_ko, job_name_en, job_category_code, job_category_name,
                        description_ko, description_en, required_skills, related_keywords, raw_response, active_yn
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT(source, job_code) DO UPDATE SET
                        job_name_ko = EXCLUDED.job_name_ko,
                        job_name_en = EXCLUDED.job_name_en,
                        job_category_code = EXCLUDED.job_category_code,
                        job_category_name = EXCLUDED.job_category_name,
                        description_ko = EXCLUDED.description_ko,
                        description_en = EXCLUDED.description_en,
                        required_skills = EXCLUDED.required_skills,
                        related_keywords = EXCLUDED.related_keywords,
                        raw_response = EXCLUDED.raw_response,
                        active_yn = EXCLUDED.active_yn,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        item.get("source", "employment24"),
                        code,
                        name,
                        item.get("job_name_en"),
                        item.get("job_category_code"),
                        item.get("job_category_name"),
                        item.get("description_ko"),
                        item.get("description_en"),
                        item.get("required_skills"),
                        item.get("related_keywords"),
                        json.dumps(item.get("raw_response") or {}, ensure_ascii=False),
                        item.get("active_yn", "Y"),
                    ),
                )
            conn.commit()
        return "updated" if existing else "inserted"

    def upsert_occupation(self, item: dict[str, Any]) -> str:
        code = str(item.get("occupation_code") or "").strip()
        name = str(item.get("occupation_name_ko") or "").strip()
        if not code or not name:
            return "skipped"
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT raw_response FROM occupation.occupation_info WHERE source = %s AND occupation_code = %s", (item.get("source", "employment24"), code))
                existing = cur.fetchone()
                cur.execute(
                    """
                    INSERT INTO occupation.occupation_info (
                        source, occupation_code, occupation_name_ko, occupation_name_en,
                        occupation_category_code, occupation_category_name, work_description_ko, work_description_en,
                        required_education, required_certificates, related_jobs, outlook, raw_response, active_yn
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    ON CONFLICT(source, occupation_code) DO UPDATE SET
                        occupation_name_ko = EXCLUDED.occupation_name_ko,
                        occupation_name_en = EXCLUDED.occupation_name_en,
                        occupation_category_code = EXCLUDED.occupation_category_code,
                        occupation_category_name = EXCLUDED.occupation_category_name,
                        work_description_ko = EXCLUDED.work_description_ko,
                        work_description_en = EXCLUDED.work_description_en,
                        required_education = EXCLUDED.required_education,
                        required_certificates = EXCLUDED.required_certificates,
                        related_jobs = EXCLUDED.related_jobs,
                        outlook = EXCLUDED.outlook,
                        raw_response = EXCLUDED.raw_response,
                        active_yn = EXCLUDED.active_yn,
                        updated_at = CURRENT_TIMESTAMP
                    """,
                    (
                        item.get("source", "employment24"),
                        code,
                        name,
                        item.get("occupation_name_en"),
                        item.get("occupation_category_code"),
                        item.get("occupation_category_name"),
                        item.get("work_description_ko"),
                        item.get("work_description_en"),
                        item.get("required_education"),
                        item.get("required_certificates"),
                        item.get("related_jobs"),
                        item.get("outlook"),
                        json.dumps(item.get("raw_response") or {}, ensure_ascii=False),
                        item.get("active_yn", "Y"),
                    ),
                )
            conn.commit()
        return "updated" if existing else "inserted"

    def dashboard(self) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        (SELECT COUNT(*)::int FROM occupation.job_info) AS job_count,
                        (SELECT COUNT(*)::int FROM occupation.occupation_info) AS occupation_count,
                        (SELECT COUNT(*)::int FROM occupation.keyword_mapping WHERE active_yn = 'Y') AS keyword_mapping_count,
                        (SELECT COUNT(*)::int FROM occupation.collect_log WHERE status IN ('FAILED', 'PARTIAL_FAILED')) AS failed_count,
                        (SELECT MAX(started_at) FROM occupation.collect_log) AS latest_collected_at,
                        (SELECT status FROM occupation.collect_log ORDER BY started_at DESC, id DESC LIMIT 1) AS latest_status
                    """
                )
                row = cur.fetchone()
                columns = [column.name for column in cur.description]
        return dict(zip(columns, row)) if row else {}

    def list_jobs(self, page: int = 1, size: int = 20, keyword: str = "", job_code: str = "", active_yn: str = "") -> dict[str, Any]:
        return self._list_table("job_info", page, size, keyword, job_code, active_yn)

    def list_occupations(self, page: int = 1, size: int = 20, keyword: str = "", occupation_code: str = "", active_yn: str = "") -> dict[str, Any]:
        return self._list_table("occupation_info", page, size, keyword, occupation_code, active_yn)

    def _list_table(self, table: str, page: int, size: int, keyword: str, code: str, active_yn: str) -> dict[str, Any]:
        page = max(1, int(page))
        size = max(1, min(int(size), 100))
        offset = (page - 1) * size
        where: list[str] = []
        params: list[Any] = []
        code_column = "job_code" if table == "job_info" else "occupation_code"
        name_column = "job_name_ko" if table == "job_info" else "occupation_name_ko"
        if keyword:
            where.append(f"({name_column} ILIKE %s OR raw_response::text ILIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if code:
            where.append(f"{code_column} = %s")
            params.append(code)
        if active_yn in {"Y", "N"}:
            where.append("active_yn = %s")
            params.append(active_yn)
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*)::int FROM occupation.{table} {where_sql}", tuple(params))
                total = int(cur.fetchone()[0])
                cur.execute(
                    f"""
                    SELECT *
                    FROM occupation.{table}
                    {where_sql}
                    ORDER BY {code_column} ASC, id ASC
                    LIMIT %s OFFSET %s
                    """,
                    tuple(params + [size, offset]),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return {"items": [dict(zip(columns, row)) for row in rows], "total_count": total, "page": page, "size": size}

    def get_job(self, item_id: int) -> dict[str, Any]:
        return self._get_by_id("job_info", item_id)

    def get_occupation(self, item_id: int) -> dict[str, Any]:
        return self._get_by_id("occupation_info", item_id)

    def _get_by_id(self, table: str, item_id: int) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM occupation.{table} WHERE id = %s", (item_id,))
                row = cur.fetchone()
                columns = [column.name for column in cur.description] if cur.description else []
        return dict(zip(columns, row)) if row else {}

    def list_keyword_mappings(self, page: int = 1, size: int = 50, keyword: str = "", language_code: str = "") -> dict[str, Any]:
        page = max(1, int(page))
        size = max(1, min(int(size), 100))
        offset = (page - 1) * size
        where: list[str] = []
        params: list[Any] = []
        if keyword:
            where.append("(external_keyword ILIKE %s OR normalized_keyword ILIKE %s OR mapped_name_ko ILIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
        if language_code:
            where.append("language_code = %s")
            params.append(language_code)
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*)::int FROM occupation.keyword_mapping {where_sql}", tuple(params))
                total = int(cur.fetchone()[0])
                cur.execute(
                    f"""
                    SELECT *
                    FROM occupation.keyword_mapping
                    {where_sql}
                    ORDER BY priority ASC, updated_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    tuple(params + [size, offset]),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return {"items": [dict(zip(columns, row)) for row in rows], "total_count": total, "page": page, "size": size}

    def upsert_keyword_mapping(self, values: dict[str, Any], item_id: int | None = None) -> dict[str, Any]:
        with connect() as conn:
            with conn.cursor() as cur:
                if item_id:
                    cur.execute(
                        """
                        UPDATE occupation.keyword_mapping
                        SET language_code = %s, external_keyword = %s, normalized_keyword = %s,
                            keyword_type = %s, job_code = %s, occupation_code = %s,
                            mapped_name_ko = %s, mapped_name_en = %s, match_score = %s,
                            mapping_source = %s, priority = %s, active_yn = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING *
                        """,
                        keyword_values(values) + [item_id],
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO occupation.keyword_mapping
                            (language_code, external_keyword, normalized_keyword, keyword_type, job_code, occupation_code,
                             mapped_name_ko, mapped_name_en, match_score, mapping_source, priority, active_yn)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        RETURNING *
                        """,
                        keyword_values(values),
                    )
                row = cur.fetchone()
                columns = [column.name for column in cur.description] if cur.description else []
            conn.commit()
        return dict(zip(columns, row)) if row else {}

    def generate_keyword_mappings(self) -> dict[str, int]:
        inserted = 0
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO occupation.keyword_mapping
                        (language_code, external_keyword, normalized_keyword, keyword_type, job_code, mapped_name_ko, mapped_name_en, mapping_source, priority)
                    SELECT 'ko', job_name_ko, lower(job_name_ko), 'job_name', job_code, job_name_ko, job_name_en, 'auto_job', 50
                    FROM occupation.job_info
                    WHERE active_yn = 'Y' AND COALESCE(job_name_ko, '') <> ''
                    ON CONFLICT DO NOTHING
                    """
                )
                inserted += cur.rowcount or 0
                cur.execute(
                    """
                    INSERT INTO occupation.keyword_mapping
                        (language_code, external_keyword, normalized_keyword, keyword_type, occupation_code, mapped_name_ko, mapped_name_en, mapping_source, priority)
                    SELECT 'ko', occupation_name_ko, lower(occupation_name_ko), 'occupation_name', occupation_code, occupation_name_ko, occupation_name_en, 'auto_occupation', 50
                    FROM occupation.occupation_info
                    WHERE active_yn = 'Y' AND COALESCE(occupation_name_ko, '') <> ''
                    ON CONFLICT DO NOTHING
                    """
                )
                inserted += cur.rowcount or 0
            conn.commit()
        return {"inserted_count": int(inserted)}

    def collect_logs(self, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT *
                    FROM occupation.collect_log
                    ORDER BY started_at DESC, id DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset),
                )
                rows = cur.fetchall()
                columns = [column.name for column in cur.description]
        return [dict(zip(columns, row)) for row in rows]


def keyword_values(values: dict[str, Any]) -> list[Any]:
    return [
        values.get("language_code") or "en",
        values.get("external_keyword") or "",
        values.get("normalized_keyword") or values.get("external_keyword") or "",
        values.get("keyword_type") or "manual",
        values.get("job_code") or None,
        values.get("occupation_code") or None,
        values.get("mapped_name_ko") or None,
        values.get("mapped_name_en") or None,
        float(values.get("match_score") or 1.0),
        values.get("mapping_source") or "manual",
        int(values.get("priority") or 100),
        values.get("active_yn") or "Y",
    ]
