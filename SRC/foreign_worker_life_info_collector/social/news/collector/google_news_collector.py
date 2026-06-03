"""Google News RSS collector."""

from __future__ import annotations

from urllib.parse import quote_plus

from .rss_news_collector import FetchArticleText, FetchText, RSSNewsCollector
from ..models import NewsItem


class GoogleNewsCollector:
    def __init__(
        self,
        locale: str = "en-US",
        region: str = "US",
        timeout: int = 10,
        fetch_text: FetchText | None = None,
        fetch_article: FetchArticleText | None = None,
    ):
        self.locale = locale
        self.region = region
        self.timeout = timeout
        self.fetch_text = fetch_text
        self.fetch_article = fetch_article

    def collect(self, keyword: str, limit: int = 10) -> list[NewsItem]:
        query = quote_plus(keyword or "foreign worker visa Korea")
        language = self.locale.split("-")[0]
        feed_url = (
            "https://news.google.com/rss/search"
            f"?q={query}&hl={self.locale}&gl={self.region}&ceid={self.region}:{language}"
        )
        collector = RSSNewsCollector(
            feed_urls=[feed_url],
            source="google_news",
            timeout=self.timeout,
            fetch_text=self.fetch_text,
            fetch_article=self.fetch_article,
        )
        return collector.collect(keyword="", limit=limit)
