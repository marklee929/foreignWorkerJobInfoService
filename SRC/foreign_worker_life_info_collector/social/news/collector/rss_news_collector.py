"""RSS news collector."""

from __future__ import annotations

from typing import Callable
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from ....utils.text_normalizer import normalize_plain_text
from ..models import NewsItem
from .article_text_extractor import fetch_article_metadata
from .google_news_url_resolver import (
    is_acceptable_source_url,
    is_google_news_url,
    is_more_specific_article_url,
    resolve_google_news_url,
)


FetchText = Callable[[str, int], str]
FetchArticleText = Callable[[str, int], object]


def _default_fetch_text(url: str, timeout: int) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "WorkConnectKoreaNewsCollector/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _child_text(element: ElementTree.Element, tag: str) -> str:
    child = element.find(tag)
    return normalize_plain_text(child.text or "") if child is not None else ""


def _source_info(element: ElementTree.Element) -> tuple[str, str]:
    child = element.find("source")
    if child is None:
        return "", ""
    return normalize_plain_text(child.text or ""), (child.attrib.get("url") or "").strip()


class RSSNewsCollector:
    def __init__(
        self,
        feed_urls: list[str] | None = None,
        source: str = "rss",
        timeout: int = 10,
        fetch_text: FetchText | None = None,
        fetch_article: FetchArticleText | None = None,
    ):
        self.feed_urls = feed_urls or []
        self.source = source
        self.timeout = timeout
        self.fetch_text = fetch_text or _default_fetch_text
        self.fetch_article = fetch_article or fetch_article_metadata

    def collect(self, keyword: str = "", limit: int = 10) -> list[NewsItem]:
        items: list[NewsItem] = []
        for feed_url in self.feed_urls:
            items.extend(self.collect_feed(feed_url, keyword=keyword, limit=limit - len(items)))
            if len(items) >= limit:
                break
        return items[:limit]

    def collect_feed(self, feed_url: str, keyword: str = "", limit: int = 10) -> list[NewsItem]:
        if limit <= 0:
            return []
        try:
            xml_text = self.fetch_text(feed_url, self.timeout)
            root = ElementTree.fromstring(xml_text)
        except Exception:
            return []

        items: list[NewsItem] = []
        for entry in root.findall(".//item"):
            title = _child_text(entry, "title")
            url = _child_text(entry, "link")
            summary = _child_text(entry, "description")
            rss_source_name, rss_source_url = _source_info(entry)
            if not title or not url:
                continue
            if keyword and keyword.lower() not in f"{title} {summary}".lower():
                continue
            content = ""
            image_url = ""
            image_urls: list[str] = []
            google_news_url = url if is_google_news_url(url) else ""
            resolved_url = resolve_google_news_url(url, self.timeout) if google_news_url else url
            source_url = resolved_url if is_acceptable_source_url(resolved_url) else ""
            canonical_url = ""
            publisher_name = rss_source_name
            if source_url:
                try:
                    article = self.fetch_article(source_url, self.timeout)
                    if isinstance(article, str):
                        content = article
                    else:
                        content = getattr(article, "content", "") or ""
                        image_url = getattr(article, "image_url", "") or ""
                        image_urls = list(getattr(article, "image_urls", None) or [])
                        canonical_url = getattr(article, "canonical_url", "") or ""
                        publisher_name = publisher_name or getattr(article, "publisher_name", "") or ""
                except Exception:
                    content = ""
            if is_more_specific_article_url(canonical_url, source_url):
                source_url = canonical_url
            if not is_acceptable_source_url(source_url):
                source_url = ""
            if canonical_url and not is_acceptable_source_url(canonical_url):
                canonical_url = ""
            items.append(
                NewsItem(
                    title=title,
                    url=source_url,
                    source=self.source,
                    source_name=publisher_name,
                    google_news_url=google_news_url,
                    canonical_url=canonical_url or source_url,
                    publisher_name=publisher_name,
                    summary=summary,
                    content=content,
                    image_url=image_url,
                    image_urls=image_urls,
                    category="foreign_worker_news",
                )
            )
            if len(items) >= limit:
                break
        return items
