from __future__ import annotations

import os
import unittest

from foreign_worker_life_info_collector.social.news.collector.google_news_collector import GoogleNewsCollector
from foreign_worker_life_info_collector.social.news.collector.naver_news_collector import (
    NAVER_CLIENT_ID_ENV,
    NAVER_CLIENT_SECRET_ENV,
    NaverNewsCollector,
)
from foreign_worker_life_info_collector.social.news.collector.rss_news_collector import RSSNewsCollector


RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>외국인 취업 비자 정책 안내</title>
      <link>https://example.com/news/visa</link>
      <description>외국인 근로자 취업 지원 정책</description>
    </item>
    <item>
      <title>무관한 소식</title>
      <link>https://example.com/news/other</link>
      <description>다른 기사</description>
    </item>
  </channel>
</rss>
"""


class SocialNewsCollectorsTest(unittest.TestCase):
    def test_rss_collector_parses_and_filters_items(self) -> None:
        collector = RSSNewsCollector(
            feed_urls=["https://example.com/rss.xml"],
            fetch_text=lambda _url, _timeout: RSS_XML,
        )

        items = collector.collect("외국인", limit=10)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "외국인 취업 비자 정책 안내")
        self.assertEqual(items[0].url, "https://example.com/news/visa")
        self.assertEqual(items[0].source, "rss")

    def test_google_collector_builds_rss_search_url(self) -> None:
        seen_urls: list[str] = []

        def fetch_text(url: str, _timeout: int) -> str:
            seen_urls.append(url)
            return RSS_XML

        collector = GoogleNewsCollector(fetch_text=fetch_text)
        items = collector.collect("외국인 취업", limit=1)

        self.assertEqual(len(items), 1)
        self.assertIn("news.google.com/rss/search", seen_urls[0])
        self.assertIn("q=%EC%99%B8%EA%B5%AD%EC%9D%B8+%EC%B7%A8%EC%97%85", seen_urls[0])
        self.assertEqual(items[0].source, "google_news")

    def test_naver_collector_requires_credentials(self) -> None:
        old_client_id = os.environ.pop(NAVER_CLIENT_ID_ENV, None)
        old_client_secret = os.environ.pop(NAVER_CLIENT_SECRET_ENV, None)
        try:
            collector = NaverNewsCollector(fetch_json=lambda _url, _headers, _timeout: {"items": []})
            self.assertEqual(collector.collect("외국인 취업"), [])
        finally:
            if old_client_id is not None:
                os.environ[NAVER_CLIENT_ID_ENV] = old_client_id
            if old_client_secret is not None:
                os.environ[NAVER_CLIENT_SECRET_ENV] = old_client_secret

    def test_naver_collector_parses_openapi_payload(self) -> None:
        old_client_id = os.environ.get(NAVER_CLIENT_ID_ENV)
        old_client_secret = os.environ.get(NAVER_CLIENT_SECRET_ENV)
        os.environ[NAVER_CLIENT_ID_ENV] = "test-client"
        os.environ[NAVER_CLIENT_SECRET_ENV] = "test-secret"
        try:
            collector = NaverNewsCollector(
                fetch_json=lambda _url, _headers, _timeout: {
                    "items": [
                        {
                            "title": "<b>외국인</b> 취업 지원",
                            "originallink": "https://example.com/naver/original",
                            "description": "비자 &amp; 취업 정보",
                        }
                    ]
                }
            )
            items = collector.collect("외국인 취업")
        finally:
            if old_client_id is None:
                os.environ.pop(NAVER_CLIENT_ID_ENV, None)
            else:
                os.environ[NAVER_CLIENT_ID_ENV] = old_client_id
            if old_client_secret is None:
                os.environ.pop(NAVER_CLIENT_SECRET_ENV, None)
            else:
                os.environ[NAVER_CLIENT_SECRET_ENV] = old_client_secret

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "외국인 취업 지원")
        self.assertEqual(items[0].summary, "비자 & 취업 정보")
        self.assertEqual(items[0].source, "naver_news")


if __name__ == "__main__":
    unittest.main()
