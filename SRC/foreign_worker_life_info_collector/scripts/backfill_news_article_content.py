from __future__ import annotations

import argparse

from ..social.news.collector.article_text_extractor import fetch_article_text
from ..storage.db.postgres import connect, load_env_file


def backfill(limit: int = 50, timeout: int = 12) -> dict[str, int]:
    load_env_file()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, source_url, title
                FROM social_news.candidate
                WHERE COALESCE(content, '') = ''
                  AND COALESCE(source_url, '') <> ''
                ORDER BY collected_at DESC, id DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

    updated = 0
    failed = 0
    for candidate_id, source_url, title in rows:
        try:
            content = fetch_article_text(source_url, timeout=timeout)
        except Exception:
            content = ""
        if len(content) < 120:
            failed += 1
            continue
        with connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE social_news.candidate
                    SET content = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (content, candidate_id),
                )
                cur.execute(
                    """
                    UPDATE social_news.normalized_item
                    SET content = %s,
                        normalized_at = CURRENT_TIMESTAMP
                    WHERE source_url = %s
                    """,
                    (content, source_url),
                )
                cur.execute(
                    """
                    UPDATE social_news.raw_item
                    SET raw_content = %s
                    WHERE source_url = %s
                    """,
                    (content, source_url),
                )
            conn.commit()
        print(f"본문 저장: {candidate_id} {str(title)[:80]}")
        updated += 1
    return {"target": len(rows), "updated": updated, "failed": failed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Backfill article body text into PostgreSQL social news tables.")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args(argv)
    result = backfill(limit=args.limit, timeout=args.timeout)
    print(f"본문 백필 완료: 대상 {result['target']}건, 저장 {result['updated']}건, 실패 {result['failed']}건")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

