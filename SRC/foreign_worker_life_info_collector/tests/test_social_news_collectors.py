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
from foreign_worker_life_info_collector.social.news.collector.article_text_extractor import ArticleMetadata


RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>외국인 취업 비자 정책 안내</title>
      <link>https://example.com/news/visa</link>
      <description>&lt;a href=&quot;https://example.com&quot;&gt;외국인 근로자&lt;/a&gt; &lt;font color=&quot;red&quot;&gt;취업 지원 정책&lt;/font&gt;</description>
    </item>
    <item>
      <title>무관한 소식</title>
      <link>https://example.com/news/other</link>
      <description>다른 기사</description>
    </item>
  </channel>
</rss>
"""

GOOGLE_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Korea visa reform - Example Daily</title>
      <link>https://news.google.com/rss/articles/google-token?oc=5</link>
      <source url="https://example.com">Example Daily</source>
      <description>Korea announced employment visa support for foreign workers.</description>
    </item>
  </channel>
</rss>
"""

GOOGLE_RSS_WITH_QUERY_URL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Korea foreign worker policy - Publisher</title>
      <link>https://news.google.com/rss/articles/story?url=https%3A%2F%2Fpublisher.example%2Fnews%2Fkorea-worker-visa-2026&amp;oc=5</link>
      <source url="https://publisher.example">Publisher</source>
      <description>Korea foreign worker visa policy update.</description>
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
        self.assertEqual(items[0].summary, "외국인 근로자 취업 지원 정책")

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

    def test_google_rss_keeps_google_url_separate_and_rejects_publisher_root(self) -> None:
        calls: list[str] = []

        def fetch_article(url: str, _timeout: int) -> ArticleMetadata:
            calls.append(url)
            return ArticleMetadata(content="Should not be fetched")

        collector = RSSNewsCollector(
            feed_urls=["https://news.google.com/rss/search?q=korea"],
            source="google_news",
            fetch_text=lambda _url, _timeout: GOOGLE_RSS_XML,
            fetch_article=fetch_article,
        )

        items = collector.collect(limit=1)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].url, "")
        self.assertEqual(items[0].canonical_url, "")
        self.assertTrue(items[0].google_news_url.startswith("https://news.google.com/rss/articles/"))
        self.assertEqual(calls, [])

    def test_google_rss_uses_resolved_article_url_and_fetches_content(self) -> None:
        calls: list[str] = []

        def fetch_article(url: str, _timeout: int) -> ArticleMetadata:
            calls.append(url)
            return ArticleMetadata(
                content="Full article body for Korea foreign worker visa policy.",
                canonical_url="https://publisher.example/news/korea-worker-visa-2026",
                publisher_name="Publisher",
            )

        collector = RSSNewsCollector(
            feed_urls=["https://news.google.com/rss/search?q=korea"],
            source="google_news",
            fetch_text=lambda _url, _timeout: GOOGLE_RSS_WITH_QUERY_URL_XML,
            fetch_article=fetch_article,
        )

        items = collector.collect(limit=1)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].url, "https://publisher.example/news/korea-worker-visa-2026")
        self.assertEqual(items[0].canonical_url, "https://publisher.example/news/korea-worker-visa-2026")
        self.assertTrue(items[0].google_news_url.startswith("https://news.google.com/rss/articles/"))
        self.assertEqual(calls, ["https://publisher.example/news/korea-worker-visa-2026"])
        self.assertIn("Full article body", items[0].content)

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
