"""Helpers for resolving Google News article URLs to publisher URLs."""

from __future__ import annotations

import html
import re
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from ....utils.text_normalizer import normalize_plain_text


GOOGLE_NEWS_HOSTS = {"news.google.com", "www.news.google.com"}


def is_google_news_url(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    return parsed.netloc.lower() in GOOGLE_NEWS_HOSTS


def resolve_google_news_url(url: str, timeout: int = 10) -> str:
    """Best-effort Google News URL resolver.

    Google News RSS links sometimes resolve through HTTP redirects, but some
    feeds return a Google article shell. In that case, inspect known URL hints
    in the HTML and return the first non-Google https URL.
    """

    url = (url or "").strip()
    if not is_google_news_url(url):
        return url

    direct = _query_url(url)
    if direct and not is_google_news_url(direct):
        return direct

    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WorkConnectKoreaNewsCollector/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    opener = build_opener(HTTPRedirectHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            if final_url and not is_google_news_url(final_url):
                return final_url
            body = response.read(512_000)
            charset = response.headers.get_content_charset() or "utf-8"
            text = body.decode(charset, errors="replace")
    except Exception:
        return url

    for candidate in _extract_url_candidates(text):
        if not is_google_news_url(candidate):
            return candidate
    return url


def is_probable_article_url(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return False
    path = (parsed.path or "").strip("/")
    if not path:
        return False
    if len(path) < 8 and not parsed.query:
        return False
    return True


def is_domain_root_url(url: str) -> bool:
    parsed = urlparse((url or "").strip())
    path = (parsed.path or "").strip("/")
    return bool(parsed.scheme and parsed.netloc) and not path and not parsed.query and not parsed.fragment


def is_acceptable_source_url(url: str) -> bool:
    """Return True only when a URL is usable as a publisher article URL."""

    url = (url or "").strip()
    return bool(url) and not is_google_news_url(url) and not is_domain_root_url(url) and is_probable_article_url(url)


def article_url_specificity(url: str) -> int:
    parsed = urlparse((url or "").strip())
    if not parsed.scheme or not parsed.netloc:
        return 0
    if is_domain_root_url(url):
        return 1
    path_parts = [part for part in parsed.path.split("/") if part]
    score = max(2, len(path_parts) * 10)
    if parsed.query:
        score += 8
    if any(ch.isdigit() for ch in parsed.path):
        score += 6
    if parsed.path.lower().endswith((".html", ".htm", ".php", ".aspx")):
        score += 4
    return score


def is_more_specific_article_url(candidate_url: str, current_url: str = "") -> bool:
    candidate_url = (candidate_url or "").strip()
    current_url = (current_url or "").strip()
    if not candidate_url or is_google_news_url(candidate_url) or is_domain_root_url(candidate_url):
        return False
    if not current_url or is_google_news_url(current_url):
        return True
    return article_url_specificity(candidate_url) > article_url_specificity(current_url)


def best_article_url(*urls: str) -> str:
    candidates: list[str] = []
    for value in urls:
        url = (value or "").strip()
        if not url or is_google_news_url(url):
            continue
        if url not in candidates:
            candidates.append(url)
    if not candidates:
        return ""
    non_root = [url for url in candidates if not is_domain_root_url(url)]
    if not non_root:
        return ""
    return sorted(non_root, key=article_url_specificity, reverse=True)[0]


def prefer_article_url(candidate_url: str, fallback_url: str = "") -> str:
    candidate_url = (candidate_url or "").strip()
    fallback_url = (fallback_url or "").strip()
    if candidate_url and not is_google_news_url(candidate_url) and is_probable_article_url(candidate_url):
        return candidate_url
    if fallback_url:
        return fallback_url
    return candidate_url


def _query_url(url: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    for key in ("url", "u"):
        values = params.get(key)
        if values:
            return normalize_plain_text(unquote(values[0]))
    return ""


def _extract_url_candidates(text: str) -> list[str]:
    decoded = html.unescape(text or "")
    candidates: list[str] = []
    patterns = [
        r'data-n-au=["\'](?P<url>https?://[^"\']+)["\']',
        r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\'](?P<url>https?://[^"\']+)["\']',
        r'<meta[^>]+property=["\']og:url["\'][^>]+content=["\'](?P<url>https?://[^"\']+)["\']',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, decoded, flags=re.IGNORECASE):
            value = normalize_plain_text(unquote(match.group("url"))).strip()
            if not value or _reject_url_candidate(value):
                continue
            if value not in candidates:
                candidates.append(value)
    return candidates


def _reject_url_candidate(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if not host:
        return True
    if "google" in host or host.endswith(("gstatic.com", "ggpht.com", "w3.org")):
        return True
    if path.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico", ".js", ".css")):
        return True
    if "svg" in url.lower():
        return True
    return False
