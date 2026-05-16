"""SQLite repository for social news automation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..duplicate_guard.duplicate_detector import find_duplicate
from ..models import NewsCandidate
from ..normalizer.news_normalizer import normalize_news_item


class NewsRepository:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize(self) -> None:
        schema_path = Path(__file__).resolve().parents[3] / "storage" / "db" / "migrations" / "schema.sql"
        conn = self.connect()
        try:
            conn.executescript(schema_path.read_text(encoding="utf-8"))
            conn.commit()
        finally:
            conn.close()

    def list_candidates(self) -> list[NewsCandidate]:
        conn = self.connect()
        try:
            rows = conn.execute(
                """
                SELECT id, source_type, source_url, title, summary, content, language, category,
                       hash_key, similarity_key, duplicate_group_id, status, collected_at, published_at
                FROM news_candidate
                ORDER BY id
                """
            ).fetchall()
        finally:
            conn.close()
        return [self._row_to_candidate(row) for row in rows]

    def save(self, item) -> NewsCandidate:
        candidate = normalize_news_item(item)
        duplicate = find_duplicate(candidate, self.list_candidates())
        if duplicate:
            candidate.status = "DUPLICATE"
            candidate.duplicate_group_id = duplicate.duplicate_group_id or duplicate.id

        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO news_candidate
                (source_type, source_url, title, summary, content, language, category, hash_key,
                 similarity_key, duplicate_group_id, status, collected_at, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.source_type,
                    candidate.source_url,
                    candidate.title,
                    candidate.summary,
                    candidate.content,
                    candidate.language,
                    candidate.category,
                    candidate.hash_key,
                    candidate.similarity_key,
                    candidate.duplicate_group_id,
                    candidate.status,
                    candidate.collected_at,
                    candidate.published_at,
                ),
            )
            candidate.id = int(cur.lastrowid)
            if not candidate.duplicate_group_id:
                candidate.duplicate_group_id = candidate.id
                conn.execute(
                    "UPDATE news_candidate SET duplicate_group_id = ? WHERE id = ?",
                    (candidate.duplicate_group_id, candidate.id),
                )
            conn.commit()
        finally:
            conn.close()
        return candidate

    def mark_ready_to_publish(self, limit: int = 5) -> list[NewsCandidate]:
        conn = self.connect()
        try:
            rows = conn.execute(
                """
                SELECT id, source_type, source_url, title, summary, content, language, category,
                       hash_key, similarity_key, duplicate_group_id, status, collected_at, published_at
                FROM news_candidate
                WHERE status = 'CANDIDATE'
                ORDER BY collected_at, id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            ids = [int(row["id"]) for row in rows]
            if ids:
                conn.executemany(
                    "UPDATE news_candidate SET status = 'READY_TO_PUBLISH' WHERE id = ?",
                    [(candidate_id,) for candidate_id in ids],
                )
                conn.commit()
        finally:
            conn.close()
        return [self._row_to_candidate(row, status="READY_TO_PUBLISH") for row in rows]

    def mark_published(self, candidate_id: int, published_at: str) -> None:
        conn = self.connect()
        try:
            conn.execute(
                "UPDATE news_candidate SET status = 'PUBLISHED', published_at = ? WHERE id = ?",
                (published_at, candidate_id),
            )
            conn.commit()
        finally:
            conn.close()

    def insert_facebook_log(
        self,
        news_candidate_id: int,
        status: str,
        published_at: str,
        page_id: str = "",
        facebook_post_id: str = "",
        error_code: str = "",
        error_message: str = "",
    ) -> int:
        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO facebook_publish_log
                (news_candidate_id, page_id, facebook_post_id, status, error_code, error_message, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (news_candidate_id, page_id, facebook_post_id, status, error_code, error_message, published_at),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def insert_telegram_log(
        self,
        message: str,
        status: str,
        sent_at: str,
        news_candidate_id: int | None = None,
        error_message: str = "",
    ) -> int:
        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO telegram_notify_log
                (news_candidate_id, message, status, error_message, sent_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (news_candidate_id, message, status, error_message, sent_at),
            )
            conn.commit()
            return int(cur.lastrowid)
        finally:
            conn.close()

    def _row_to_candidate(self, row: sqlite3.Row, status: str | None = None) -> NewsCandidate:
        return NewsCandidate(
            id=int(row["id"]),
            source_type=row["source_type"],
            source_url=row["source_url"] or "",
            title=row["title"],
            summary=row["summary"] or "",
            content=row["content"] or "",
            language=row["language"] or "ko",
            category=row["category"] or "",
            hash_key=row["hash_key"] or "",
            similarity_key=row["similarity_key"] or "",
            duplicate_group_id=row["duplicate_group_id"],
            status=status or row["status"],
            collected_at=row["collected_at"],
            published_at=row["published_at"],
        )
