"""SQLite repository for social news automation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from ..models import NewsCandidate
from ..normalizer.news_normalizer import normalize_news_item


NEWS_COLUMNS = (
    "id",
    "source_type",
    "source_url",
    "title",
    "summary",
    "content",
    "language",
    "category",
    "keyword",
    "hash_key",
    "similarity_key",
    "short_summary",
    "key_points",
    "relevance_reason",
    "risk_notes",
    "evaluation_score",
    "duplicate_risk_score",
    "duplicate_group_id",
    "status",
    "collected_at",
    "published_at",
)


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
            self._ensure_news_columns(conn)
            conn.commit()
        finally:
            conn.close()

    def _ensure_news_columns(self, conn: sqlite3.Connection) -> None:
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(news_candidate)").fetchall()}
        migrations = {
            "keyword": "ALTER TABLE news_candidate ADD COLUMN keyword TEXT",
            "short_summary": "ALTER TABLE news_candidate ADD COLUMN short_summary TEXT",
            "key_points": "ALTER TABLE news_candidate ADD COLUMN key_points TEXT",
            "relevance_reason": "ALTER TABLE news_candidate ADD COLUMN relevance_reason TEXT",
            "risk_notes": "ALTER TABLE news_candidate ADD COLUMN risk_notes TEXT",
            "evaluation_score": "ALTER TABLE news_candidate ADD COLUMN evaluation_score REAL DEFAULT 0",
            "duplicate_risk_score": "ALTER TABLE news_candidate ADD COLUMN duplicate_risk_score REAL DEFAULT 0",
        }
        for column, statement in migrations.items():
            if column not in existing:
                conn.execute(statement)

    def list_candidates(self) -> list[NewsCandidate]:
        conn = self.connect()
        try:
            rows = conn.execute(
                """
                SELECT id, source_type, source_url, title, summary, content, language, category,
                       keyword, hash_key, similarity_key, short_summary, key_points, relevance_reason,
                       risk_notes, evaluation_score, duplicate_risk_score, duplicate_group_id,
                       status, collected_at, published_at
                FROM news_candidate
                ORDER BY id
                """
            ).fetchall()
        finally:
            conn.close()
        return [self._row_to_candidate(row) for row in rows]

    def list_recent_published(self, limit: int = 20) -> list[NewsCandidate]:
        conn = self.connect()
        try:
            rows = conn.execute(
                f"""
                SELECT {', '.join(NEWS_COLUMNS)}
                FROM news_candidate
                WHERE status IN ('PUBLISHED', 'NOTIFIED')
                ORDER BY published_at DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        finally:
            conn.close()
        return [self._row_to_candidate(row) for row in rows]

    def save(self, item) -> NewsCandidate:
        candidate = normalize_news_item(item)
        candidate.status = candidate.status or "NORMALIZED"

        conn = self.connect()
        try:
            cur = conn.execute(
                """
                INSERT INTO news_candidate
                (source_type, source_url, title, summary, content, language, category, hash_key,
                 similarity_key, keyword, short_summary, key_points, relevance_reason, risk_notes,
                 evaluation_score, duplicate_risk_score, duplicate_group_id, status, collected_at, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    candidate.keyword,
                    candidate.short_summary,
                    candidate.key_points,
                    candidate.relevance_reason,
                    candidate.risk_notes,
                    candidate.evaluation_score,
                    candidate.duplicate_risk_score,
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

    def update_candidate(self, candidate: NewsCandidate) -> NewsCandidate:
        if candidate.id is None:
            raise ValueError("candidate.id is required for update")
        conn = self.connect()
        try:
            conn.execute(
                """
                UPDATE news_candidate
                SET source_type = ?, source_url = ?, title = ?, summary = ?, content = ?,
                    language = ?, category = ?, keyword = ?, hash_key = ?, similarity_key = ?,
                    short_summary = ?, key_points = ?, relevance_reason = ?, risk_notes = ?,
                    evaluation_score = ?, duplicate_risk_score = ?, duplicate_group_id = ?,
                    status = ?, collected_at = ?, published_at = ?
                WHERE id = ?
                """,
                (
                    candidate.source_type,
                    candidate.source_url,
                    candidate.title,
                    candidate.summary,
                    candidate.content,
                    candidate.language,
                    candidate.category,
                    candidate.keyword,
                    candidate.hash_key,
                    candidate.similarity_key,
                    candidate.short_summary,
                    candidate.key_points,
                    candidate.relevance_reason,
                    candidate.risk_notes,
                    candidate.evaluation_score,
                    candidate.duplicate_risk_score,
                    candidate.duplicate_group_id,
                    candidate.status,
                    candidate.collected_at,
                    candidate.published_at,
                    candidate.id,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return candidate

    def mark_status(
        self,
        candidate_id: int,
        status: str,
        published_at: str | None = None,
        evaluation_score: float | None = None,
        duplicate_risk_score: float | None = None,
        duplicate_group_id: int | None = None,
    ) -> None:
        assignments = ["status = ?"]
        values: list = [status]
        if published_at is not None:
            assignments.append("published_at = ?")
            values.append(published_at)
        if evaluation_score is not None:
            assignments.append("evaluation_score = ?")
            values.append(evaluation_score)
        if duplicate_risk_score is not None:
            assignments.append("duplicate_risk_score = ?")
            values.append(duplicate_risk_score)
        if duplicate_group_id is not None:
            assignments.append("duplicate_group_id = ?")
            values.append(duplicate_group_id)
        values.append(candidate_id)
        conn = self.connect()
        try:
            conn.execute(f"UPDATE news_candidate SET {', '.join(assignments)} WHERE id = ?", values)
            conn.commit()
        finally:
            conn.close()

    def mark_ready_to_publish(self, limit: int = 5) -> list[NewsCandidate]:
        conn = self.connect()
        try:
            rows = conn.execute(
                """
                SELECT id, source_type, source_url, title, summary, content, language, category,
                       keyword, hash_key, similarity_key, short_summary, key_points, relevance_reason,
                       risk_notes, evaluation_score, duplicate_risk_score, duplicate_group_id,
                       status, collected_at, published_at
                FROM news_candidate
                WHERE status = 'READY_TO_PUBLISH'
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

    def mark_notified(self, candidate_id: int) -> None:
        self.mark_status(candidate_id, "NOTIFIED")

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
            keyword=row["keyword"] or "",
            hash_key=row["hash_key"] or "",
            similarity_key=row["similarity_key"] or "",
            short_summary=row["short_summary"] or "",
            key_points=row["key_points"] or "",
            relevance_reason=row["relevance_reason"] or "",
            risk_notes=row["risk_notes"] or "",
            evaluation_score=float(row["evaluation_score"] or 0.0),
            duplicate_risk_score=float(row["duplicate_risk_score"] or 0.0),
            duplicate_group_id=row["duplicate_group_id"],
            status=status or row["status"],
            collected_at=row["collected_at"],
            published_at=row["published_at"],
        )
