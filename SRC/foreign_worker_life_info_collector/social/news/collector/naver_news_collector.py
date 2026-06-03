"""Naver News OpenAPI collector."""

from __future__ import annotations

import json
import os
import re
from html import unescape
from typing import Callable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from ..models import NewsItem
from .article_text_extractor import fetch_article_metadata


FetchJson = Callable[[str, dict[str, str], int], dict]
FetchArticleText = Callable[[str, int], object]

NAVER_CLIENT_ID_ENV = "NAVER_CLIENT_ID"
NAVER_CLIENT_SECRET_ENV = "NAVER_CLIENT_SECRET"


def _default_fetch_json(url: str, headers: dict[str, str], timeout: int) -> dict:
    request = Request(url, headers=headers)
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _clean_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value or "")
    return unescape(re.sub(r"\s+", " ", text).strip())


class NaverNewsCollector:
    def __init__(
        self,
        client_id_env: str = NAVER_CLIENT_ID_ENV,
        client_secret_env: str = NAVER_CLIENT_SECRET_ENV,
        timeout: int = 10,
        fetch_json: FetchJson | None = None,
        fetch_article: FetchArticleText | None = None,
    ):
        self.client_id_env = client_id_env
        self.client_secret_env = client_secret_env
        self.timeout = timeout
        self.fetch_json = fetch_json or _default_fetch_json
        self.fetch_article = fetch_article or fetch_article_metadata

    def collect(self, keyword: str, limit: int = 10) -> list[NewsItem]:
        client_id = os.getenv(self.client_id_env, "").strip()
        client_secret = os.getenv(self.client_secret_env, "").strip()
        if not client_id or not client_secret:
            return []

        display = max(1, min(limit, 100))
        url = f"https://openapi.naver.com/v1/search/news.json?query={quote_plus(keyword)}&display={display}&sort=date"
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
            "User-Agent": "WorkConnectKoreaNewsCollector/1.0",
        }
        try:
            payload = self.fetch_json(url, headers, self.timeout)
        except Exception:
            return []

        items: list[NewsItem] = []
        for entry in payload.get("items", []):
            title = _clean_html(entry.get("title", ""))
            summary = _clean_html(entry.get("description", ""))
            url = (entry.get("originallink") or entry.get("link") or "").strip()
            if not title or not url:
                continue
            content = ""
            image_url = ""
            image_urls: list[str] = []
            canonical_url = ""
            publisher_name = ""
            try:
                article = self.fetch_article(url, self.timeout)
                if isinstance(article, str):
                    content = article
                else:
                    content = getattr(article, "content", "") or ""
                    image_url = getattr(article, "image_url", "") or ""
                    image_urls = list(getattr(article, "image_urls", None) or [])
                    canonical_url = getattr(article, "canonical_url", "") or ""
                    publisher_name = getattr(article, "publisher_name", "") or ""
            except Exception:
                content = ""
            items.append(
                NewsItem(
                    title=title,
                    url=url,
                    source="naver_news",
                    source_name=publisher_name,
                    canonical_url=canonical_url or url,
                    publisher_name=publisher_name,
                    summary=summary,
                    content=content,
                    image_url=image_url,
                    image_urls=image_urls,
                    category="foreign_worker_news",
                )
            )
        return items[:limit]
