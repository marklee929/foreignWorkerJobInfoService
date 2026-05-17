"""Social news orchestration bot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ...social.news.pipeline import NewsPipeline
from ...social.news.repository.news_repository import NewsRepository


class NewsBot:
    def __init__(self, pipeline: NewsPipeline | None = None):
        self.pipeline = pipeline

    def run(self, keyword: str = "외국인 취업 비자", db_path: str | Path = "logs/news.db", dry_run: bool = True, limit: int = 1) -> dict:
        pipeline = self.pipeline or NewsPipeline(repository=NewsRepository(Path(db_path)))
        return pipeline.run(keyword=keyword, dry_run=dry_run, limit=limit)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the social news automation bot.")
    parser.add_argument("--db", default="SRC/foreign_worker_life_info_collector/logs/news.db", help="SQLite database path.")
    parser.add_argument("--keyword", default="외국인 취업 비자", help="News search keyword.")
    parser.add_argument("--limit", type=int, default=1, help="Maximum candidates to publish in one cycle.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run without external Facebook/Telegram calls.")
    parser.add_argument("--real", action="store_true", help="Run real Facebook/Telegram calls when environment variables are set.")
    parser.add_argument("--json", action="store_true", help="Print full JSON output.")
    parser.add_argument("--verbose", action="store_true", help="Print full JSON output.")
    args = parser.parse_args(argv)

    result = NewsBot().run(
        keyword=args.keyword,
        db_path=args.db,
        dry_run=not args.real,
        limit=args.limit,
    )
    if args.json or args.verbose:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(result["report"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
