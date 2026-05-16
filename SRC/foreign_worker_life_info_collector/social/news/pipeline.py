"""Dry-run capable social news automation pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ..facebook.post_builder import build_text_post
from ..telegram.notifier import TelegramNotifier
from ...utils.date_utils import utc_now_iso
from .collector.google_news_collector import GoogleNewsCollector
from .collector.naver_news_collector import NaverNewsCollector
from .models import NewsItem
from .repository.news_repository import NewsRepository


class NewsPipeline:
    def __init__(
        self,
        repository: NewsRepository,
        collectors: list | None = None,
        telegram_notifier: TelegramNotifier | None = None,
    ):
        self.repository = repository
        self.collectors = collectors or [NaverNewsCollector(), GoogleNewsCollector()]
        self.telegram_notifier = telegram_notifier or TelegramNotifier()

    def run(self, keyword: str = "외국인 취업 비자", dry_run: bool = True, limit: int = 5) -> dict:
        collected_items = self.collect(keyword)
        saved_candidates = [self.repository.save(item) for item in collected_items]
        ready_candidates = self.repository.mark_ready_to_publish(limit=limit)
        publish_results = [self.publish(candidate, dry_run=dry_run) for candidate in ready_candidates]
        return {
            "dry_run": dry_run,
            "collected_count": len(collected_items),
            "saved": [candidate.to_dict() for candidate in saved_candidates],
            "ready_to_publish": [candidate.to_dict() for candidate in ready_candidates],
            "publish_results": publish_results,
        }

    def collect(self, keyword: str) -> list[NewsItem]:
        items: list[NewsItem] = []
        for collector in self.collectors:
            items.extend(collector.collect(keyword))
        return items or self._dry_run_seed_items(keyword)

    def publish(self, candidate, dry_run: bool = True) -> dict:
        message = build_text_post(candidate.title, candidate.source_url)
        timestamp = utc_now_iso()
        if dry_run:
            facebook_post_id = f"dry-run-news-{candidate.id}"
            self.repository.insert_facebook_log(
                news_candidate_id=candidate.id,
                page_id="dry-run",
                facebook_post_id=facebook_post_id,
                status="DRY_RUN",
                published_at=timestamp,
            )
            self.repository.mark_published(candidate.id, timestamp)
            notice = "\n".join(
                [
                    "[WorkConnect News Published]",
                    f"제목: {candidate.title}",
                    f"출처: {candidate.source_url}",
                    f"Facebook Post ID: {facebook_post_id}",
                    "상태: DRY_RUN",
                ]
            )
            self.repository.insert_telegram_log(
                news_candidate_id=candidate.id,
                message=notice,
                status="DRY_RUN",
                sent_at=timestamp,
            )
            return {
                "news_candidate_id": candidate.id,
                "status": "DRY_RUN",
                "facebook_post_id": facebook_post_id,
                "message": message,
            }

        raise NotImplementedError("Real Facebook/Telegram publishing requires token-backed clients.")

    def _dry_run_seed_items(self, keyword: str) -> list[NewsItem]:
        return [
            NewsItem(
                title=f"{keyword} 지원 정책 안내",
                url="https://example.com/workconnect/news/support-policy",
                source="dry_run",
                summary="Dry-run sample news candidate.",
                category="foreign_worker_policy",
            ),
            NewsItem(
                title=f"{keyword} 지원 정책 안내",
                url="https://example.com/workconnect/news/support-policy",
                source="dry_run",
                summary="Duplicate dry-run sample news candidate.",
                category="foreign_worker_policy",
            ),
        ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the social news automation pipeline.")
    parser.add_argument("--db", required=True, help="SQLite database path.")
    parser.add_argument("--keyword", default="외국인 취업 비자", help="News search keyword.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum candidates to publish.")
    parser.add_argument("--dry-run", action="store_true", help="Run without external Facebook/Telegram calls.")
    args = parser.parse_args(argv)

    pipeline = NewsPipeline(repository=NewsRepository(Path(args.db)))
    result = pipeline.run(keyword=args.keyword, dry_run=args.dry_run, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
