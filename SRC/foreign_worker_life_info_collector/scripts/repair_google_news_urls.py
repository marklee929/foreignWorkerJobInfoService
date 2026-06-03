"""Repair Google News URL field mappings in PostgreSQL.

Rules:
- Google News RSS links belong in google_news_url only.
- source_url must be a real publisher article URL.
- publisher root URLs are not accepted as source_url or canonical_url.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..social.news.collector.google_news_url_resolver import is_acceptable_source_url, is_google_news_url
from ..storage.db.postgres import connect


@dataclass
class RepairStats:
    table_name: str
    inspected: int = 0
    updated: int = 0


def clean_google_url(google_news_url: str, source_url: str) -> str:
    if google_news_url:
        return google_news_url
    return source_url if is_google_news_url(source_url) else ""


def clean_source_url(source_url: str) -> str:
    return source_url if is_acceptable_source_url(source_url) else ""


def clean_canonical_url(canonical_url: str) -> str:
    return canonical_url if is_acceptable_source_url(canonical_url) else ""


def repair_raw_item() -> RepairStats:
    stats = RepairStats("social_news.raw_item")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, source_url, google_news_url FROM social_news.raw_item")
            rows = cur.fetchall()
            stats.inspected = len(rows)
            for row_id, source_url, google_news_url in rows:
                new_google = clean_google_url(google_news_url or "", source_url or "")
                new_source = clean_source_url(source_url or "")
                if new_google != (google_news_url or "") or new_source != (source_url or ""):
                    cur.execute(
                        """
                        UPDATE social_news.raw_item
                        SET source_url = %s,
                            google_news_url = %s
                        WHERE id = %s
                        """,
                        (new_source, new_google, row_id),
                    )
                    stats.updated += 1
        conn.commit()
    return stats


def repair_normalized_item() -> RepairStats:
    stats = RepairStats("social_news.normalized_item")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, source_url, canonical_url, google_news_url FROM social_news.normalized_item")
            rows = cur.fetchall()
            stats.inspected = len(rows)
            for row_id, source_url, canonical_url, google_news_url in rows:
                new_google = clean_google_url(google_news_url or "", source_url or "")
                new_source = clean_source_url(source_url or "")
                new_canonical = clean_canonical_url(canonical_url or "")
                if (
                    new_google != (google_news_url or "")
                    or new_source != (source_url or "")
                    or new_canonical != (canonical_url or "")
                ):
                    cur.execute(
                        """
                        UPDATE social_news.normalized_item
                        SET source_url = %s,
                            canonical_url = %s,
                            google_news_url = %s
                        WHERE id = %s
                        """,
                        (new_source, new_canonical, new_google, row_id),
                    )
                    stats.updated += 1
        conn.commit()
    return stats


def repair_candidate() -> RepairStats:
    stats = RepairStats("social_news.candidate")
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, source_url, canonical_url, google_news_url FROM social_news.candidate")
            rows = cur.fetchall()
            stats.inspected = len(rows)
            for row_id, source_url, canonical_url, google_news_url in rows:
                new_google = clean_google_url(google_news_url or "", source_url or "")
                new_source = clean_source_url(source_url or "")
                new_canonical = clean_canonical_url(canonical_url or "")
                if (
                    new_google != (google_news_url or "")
                    or new_source != (source_url or "")
                    or new_canonical != (canonical_url or "")
                ):
                    cur.execute(
                        """
                        UPDATE social_news.candidate
                        SET source_url = %s,
                            canonical_url = %s,
                            google_news_url = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """,
                        (new_source, new_canonical, new_google, row_id),
                    )
                    stats.updated += 1
        conn.commit()
    return stats


def main() -> int:
    stats = [repair_raw_item(), repair_normalized_item(), repair_candidate()]
    for item in stats:
        print(f"{item.table_name}: inspected={item.inspected} updated={item.updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
