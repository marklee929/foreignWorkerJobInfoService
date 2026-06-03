"""Helpers for resolving Google News article URLs to publisher URLs."""

from __future__ import annotations

import html
import json
import re
from urllib.parse import parse_qs, quote, unquote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

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

    decoded_url = _decode_with_batchexecute(text, timeout=timeout)
    if decoded_url and not is_google_news_url(decoded_url):
        return decoded_url

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


def _decode_with_batchexecute(text: str, timeout: int = 10) -> str:
    decoded = html.unescape(text or "")
    match = re.search(
        r'data-n-a-id=["\'](?P<id>[^"\']+)["\'][^>]+data-n-a-ts=["\'](?P<ts>\d+)["\'][^>]+data-n-a-sg=["\'](?P<sg>[^"\']+)["\']',
        decoded,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return ""
    article_id = normalize_plain_text(unquote(match.group("id"))).strip()
    timestamp = match.group("ts")
    signature = normalize_plain_text(unquote(match.group("sg"))).strip()
    if not article_id or not timestamp or not signature:
        return ""
    request_payload = [
        [
            [
                "Fbv4je",
                (
                    '["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],'
                    '"X","X",1,[1,1,1],1,1,null,0,0,null,0],'
                    f'"{article_id}",{timestamp},"{signature}"]'
                ),
                None,
                "generic",
            ]
        ]
    ]
    body = f"f.req={quote(json.dumps(request_payload, separators=(',', ':')))}".encode("utf-8")
    request = Request(
        "https://news.google.com/_/DotsSplashUi/data/batchexecute",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WorkConnectKoreaNewsCollector/1.0",
            "Accept": "*/*",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            response_text = response.read(512_000).decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except Exception:
        return ""
    for candidate in _extract_batchexecute_urls(response_text):
        if is_acceptable_source_url(candidate):
            return candidate
    return ""


def _extract_batchexecute_urls(text: str) -> list[str]:
    candidates: list[str] = []
    for value in re.findall(r'https?://[^"\\\]\s]+', text or ""):
        cleaned = normalize_plain_text(value.replace("\\/", "/")).strip()
        cleaned = cleaned.rstrip("\\")
        if not cleaned or _reject_url_candidate(cleaned):
            continue
        if cleaned not in candidates:
            candidates.append(cleaned)
    try:
        payload = json.loads((text or "").split("\n\n", 1)[1])
    except Exception:
        payload = []
    for row in payload if isinstance(payload, list) else []:
        if not isinstance(row, list) or len(row) < 3:
            continue
        try:
            decoded = json.loads(row[2])
        except Exception:
            continue
        for candidate in _walk_urls(decoded):
            if candidate not in candidates:
                candidates.append(candidate)
    return candidates


def _walk_urls(value) -> list[str]:
    urls: list[str] = []
    if isinstance(value, str):
        cleaned = normalize_plain_text(value).strip()
        if cleaned.startswith(("http://", "https://")) and not _reject_url_candidate(cleaned):
            urls.append(cleaned)
    elif isinstance(value, list):
        for item in value:
            urls.extend(_walk_urls(item))
    elif isinstance(value, dict):
        for item in value.values():
            urls.extend(_walk_urls(item))
    return urls


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
