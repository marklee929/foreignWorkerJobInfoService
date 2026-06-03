"""Article body extraction for collected news URLs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from ....utils.text_normalizer import normalize_plain_text


@dataclass
class ArticleMetadata:
    content: str = ""
    image_url: str = ""
    image_urls: list[str] | None = None
    canonical_url: str = ""
    publisher_name: str = ""


class ParagraphExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._capture_tag = ""
        self._buffer: list[str] = []
        self.paragraphs: list[str] = []
        self.meta_description = ""
        self.image_urls: list[str] = []
        self.canonical_url = ""
        self.publisher_name = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        if tag in {"script", "style", "noscript", "svg", "header", "footer", "nav", "aside"}:
            self._skip_depth += 1
            return
        if tag == "meta":
            name = attrs_dict.get("name", "").lower()
            prop = attrs_dict.get("property", "").lower()
            if name == "description" or prop in {"og:description", "twitter:description"}:
                self.meta_description = normalize_plain_text(attrs_dict.get("content", ""))
            if prop in {"og:url", "twitter:url"} and not self.canonical_url:
                self.canonical_url = attrs_dict.get("content", "").strip()
            if prop == "og:site_name" or name in {"application-name", "publisher"}:
                self.publisher_name = normalize_plain_text(attrs_dict.get("content", "")) or self.publisher_name
            if prop in {"og:image", "og:image:url"} or name in {"twitter:image", "twitter:image:src"}:
                self._append_image(attrs_dict.get("content", ""))
            return
        if tag == "link":
            rel = attrs_dict.get("rel", "").lower()
            if "canonical" in rel and not self.canonical_url:
                self.canonical_url = attrs_dict.get("href", "").strip()
            return
        if tag == "img":
            self._append_image(attrs_dict.get("src", "") or attrs_dict.get("data-src", ""))
            return
        if tag in {"p", "article", "section"} and self._skip_depth == 0:
            self._capture_tag = tag
            self._buffer = []

    def _append_image(self, url: str) -> None:
        url = (url or "").strip()
        if not url or url.startswith("data:"):
            return
        if url not in self.image_urls:
            self.image_urls.append(url)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg", "header", "footer", "nav", "aside"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._capture_tag and tag == self._capture_tag:
            text = normalize_plain_text(" ".join(self._buffer))
            if len(text) >= 60:
                self.paragraphs.append(text)
            self._capture_tag = ""
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and self._capture_tag:
            cleaned = normalize_plain_text(unescape(data))
            if cleaned:
                self._buffer.append(cleaned)


def fetch_article_text(url: str, timeout: int = 12, max_chars: int = 12000) -> str:
    return fetch_article_metadata(url, timeout=timeout, max_chars=max_chars).content


def fetch_article_metadata(url: str, timeout: int = 12, max_chars: int = 12000) -> ArticleMetadata:
    if not url:
        return ArticleMetadata()
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 WorkConnectKoreaNewsCollector/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,ko;q=0.7",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        raw = response.read(max_chars * 8)
        charset = response.headers.get_content_charset() or "utf-8"
        html = raw.decode(charset, errors="replace")
    parser = ParagraphExtractor()
    parser.feed(html)
    paragraphs = dedupe_paragraphs(parser.paragraphs)
    content = "\n\n".join(paragraphs)
    if len(content) < 200 and parser.meta_description:
        content = parser.meta_description
    image_urls = []
    for image_url in parser.image_urls:
        absolute_url = urljoin(url, image_url)
        if absolute_url not in image_urls:
            image_urls.append(absolute_url)
    return ArticleMetadata(
        content=normalize_plain_text(content[:max_chars]),
        image_url=image_urls[0] if image_urls else "",
        image_urls=image_urls[:12],
        canonical_url=urljoin(url, parser.canonical_url) if parser.canonical_url else "",
        publisher_name=parser.publisher_name,
    )


def dedupe_paragraphs(paragraphs: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for paragraph in paragraphs:
        key = re.sub(r"\W+", "", paragraph.lower())[:120]
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(paragraph)
    return result
