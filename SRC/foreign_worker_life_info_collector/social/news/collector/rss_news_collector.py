"""RSS news collector."""

from __future__ import annotations

from html import unescape
from typing import Callable
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from ..models import NewsItem


FetchText = Callable[[str, int], str]


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
    return unescape((child.text or "").strip()) if child is not None else ""


class RSSNewsCollector:
    def __init__(
        self,
        feed_urls: list[str] | None = None,
        source: str = "rss",
        timeout: int = 10,
        fetch_text: FetchText | None = None,
    ):
        self.feed_urls = feed_urls or []
        self.source = source
        self.timeout = timeout
        self.fetch_text = fetch_text or _default_fetch_text

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
            if not title or not url:
                continue
            if keyword and keyword.lower() not in f"{title} {summary}".lower():
                continue
            items.append(
                NewsItem(
                    title=title,
                    url=url,
                    source=self.source,
                    summary=summary,
                    category="foreign_worker_news",
                )
            )
            if len(items) >= limit:
                break
        return items
