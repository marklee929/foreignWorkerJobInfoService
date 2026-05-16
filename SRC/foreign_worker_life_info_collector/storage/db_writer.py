from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional

from ..models import DataQualityScore, LifeServiceBusiness, RawSourceData


class SQLiteDBWriter:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or Path.cwd() / "foreign_worker_life_info.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def initialize(self) -> None:
        schema_path = Path(__file__).resolve().parent / "db" / "migrations" / "schema.sql"
        conn = self.connect()
        try:
            conn.executescript(schema_path.read_text(encoding="utf-8"))
            conn.commit()
        finally:
            conn.close()

    def insert_raw(self, raw: RawSourceData) -> int:
        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO source_raw_data
                (source_type, source_url, search_keyword, raw_title, raw_content, raw_phone, raw_address, collected_at, hash_key)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    raw.source_type,
                    raw.source_url,
                    raw.search_keyword,
                    raw.raw_title,
                    raw.raw_content,
                    raw.raw_phone,
                    raw.raw_address,
                    raw.collected_at,
                    raw.hash_key,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def insert_business(self, business: LifeServiceBusiness) -> int:
        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO life_service_business
                (business_name, category, sub_category, phone, address, sido, sigungu, latitude, longitude,
                 website_url, kakao_url, naver_place_url, google_place_url, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    business.business_name,
                    business.category,
                    business.sub_category,
                    business.phone,
                    business.address,
                    business.sido,
                    business.sigungu,
                    business.latitude,
                    business.longitude,
                    business.website_url,
                    business.kakao_url,
                    business.naver_place_url,
                    business.google_place_url,
                    1 if business.is_active else 0,
                    business.created_at,
                    business.updated_at,
                ),
            )
            business_id = int(cur.lastrowid)
            for language in business.languages:
                conn.execute(
                    """
                    INSERT INTO business_language_support
                    (business_id, language_code, language_name, confidence_score, evidence_text)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (business_id, language.language_code, language.language_name, language.confidence_score, language.evidence_text),
                )
            for tag in business.tags:
                conn.execute(
                    """
                    INSERT INTO business_service_tag
                    (business_id, tag_name, confidence_score, evidence_text)
                    VALUES (?, ?, ?, ?)
                    """,
                    (business_id, tag.tag_name, tag.confidence_score, tag.evidence_text),
                )
            conn.commit()
            return business_id
        finally:
            conn.close()

    def insert_quality_score(self, score: DataQualityScore) -> int:
        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO data_quality_score
                (business_id, duplicate_score, freshness_score, contact_validity_score, foreigner_relevance_score, total_score, calculated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    score.business_id,
                    score.duplicate_score,
                    score.freshness_score,
                    score.contact_validity_score,
                    score.foreigner_relevance_score,
                    score.total_score,
                    score.calculated_at,
                ),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()
