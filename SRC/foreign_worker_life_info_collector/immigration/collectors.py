"""Official-source collectors for immigration and visa notices."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import OfficialNoticeItem
from .normalizer import absolute_url, normalize_text


@dataclass(frozen=True)
class OfficialSourceConfig:
    source: str
    source_name: str
    source_type: str
    notice_type: str
    list_url: str
    allowed_domains: tuple[str, ...]
    detail_patterns: tuple[str, ...]


OFFICIAL_SOURCES: dict[str, OfficialSourceConfig] = {
    "moj_notice": OfficialSourceConfig(
        source="moj_notice",
        source_name="법무부 공지사항",
        source_type="MINISTRY_OF_JUSTICE",
        notice_type="ANNOUNCEMENT",
        list_url="https://www.moj.go.kr/bbs/moj/184/artclList.do",
        allowed_domains=("moj.go.kr", "mojhome.moj.go.kr"),
        detail_patterns=("artclView.do",),
    ),
    "moj_press": OfficialSourceConfig(
        source="moj_press",
        source_name="법무부 보도자료",
        source_type="MINISTRY_OF_JUSTICE",
        notice_type="PRESS_RELEASE",
        list_url="https://www.moj.go.kr/bbs/moj/182/artclList.do",
        allowed_domains=("moj.go.kr", "mojhome.moj.go.kr"),
        detail_patterns=("artclView.do",),
    ),
    "hikorea": OfficialSourceConfig(
        source="hikorea",
        source_name="하이코리아 공지사항",
        source_type="HIKOREA",
        notice_type="STAY_STATUS",
        list_url="https://www.hikorea.go.kr/board/BoardNtcListR.pt?BBS_GB_CD=BS10",
        allowed_domains=("hikorea.go.kr",),
        detail_patterns=("BoardNtcDetailR.pt", "NTCCTT_SEQ="),
    ),
    "eps": OfficialSourceConfig(
        source="eps",
        source_name="EPS 고용허가제 공지사항",
        source_type="EPS",
        notice_type="EMPLOYMENT_POLICY",
        list_url="https://eps.hrdkorea.or.kr/h2/brd/noticeList.do",
        allowed_domains=("eps.hrdkorea.or.kr",),
        detail_patterns=("noticeDetail.do", "brdSeq="),
    ),
    "moel": OfficialSourceConfig(
        source="moel",
        source_name="고용노동부 외국인고용 관련 공지",
        source_type="MOEL",
        notice_type="EMPLOYMENT_POLICY",
        list_url="https://www.moel.go.kr/news/enews/report/enewsList.do",
        allowed_domains=("moel.go.kr",),
        detail_patterns=("view.do", "bbs_seq=", "news_seq="),
    ),
}


class OfficialNoticeCollector:
    def __init__(self, config: OfficialSourceConfig, timeout: int = 12):
        self.config = config
        self.timeout = timeout

    def collect(self, limit: int = 20) -> list[OfficialNoticeItem]:
        html = fetch_html(self.config.list_url, timeout=self.timeout)
        parser = LinkTitleParser(self.config.list_url)
        parser.feed(html)
        items: list[OfficialNoticeItem] = []
        seen: set[str] = set()
        for title, url in parser.links:
            if len(items) >= limit:
                break
            if not is_allowed_official_url(url, self.config.allowed_domains):
                continue
            if not is_notice_detail_url(url, self.config.detail_patterns):
                continue
            if url in seen:
                continue
            if not title or len(title) < 4:
                continue
            seen.add(url)
            items.append(
                OfficialNoticeItem(
                    source=self.config.source,
                    source_name=self.config.source_name,
                    source_type=self.config.source_type,
                    notice_type=infer_notice_type(self.config.notice_type, title),
                    title=title,
                    url=url,
                    summary="",
                    content="",
                    raw_payload={"list_url": self.config.list_url, "collector": self.__class__.__name__},
                )
            )
        return items


class MinistryJusticeNoticeCollector(OfficialNoticeCollector):
    def __init__(self):
        super().__init__(OFFICIAL_SOURCES["moj_notice"])


class MinistryJusticePressCollector(OfficialNoticeCollector):
    def __init__(self):
        super().__init__(OFFICIAL_SOURCES["moj_press"])


class HiKoreaNoticeCollector(OfficialNoticeCollector):
    def __init__(self):
        super().__init__(OFFICIAL_SOURCES["hikorea"])


class EpsNoticeCollector(OfficialNoticeCollector):
    def __init__(self):
        super().__init__(OFFICIAL_SOURCES["eps"])


class MoelForeignWorkerNoticeCollector(OfficialNoticeCollector):
    def __init__(self):
        super().__init__(OFFICIAL_SOURCES["moel"])


def default_collectors() -> dict[str, OfficialNoticeCollector]:
    return {
        "moj_notice": MinistryJusticeNoticeCollector(),
        "moj_press": MinistryJusticePressCollector(),
        "hikorea": HiKoreaNoticeCollector(),
        "eps": EpsNoticeCollector(),
        "moel": MoelForeignWorkerNoticeCollector(),
    }


class LinkTitleParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links: list[tuple[str, str]] = []
        self._href = ""
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        href = attrs_dict.get("href", "")
        if href:
            self._href = absolute_url(self.base_url, href)
            self._text_parts = []

    def handle_data(self, data: str) -> None:
        if self._href:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._href:
            return
        title = normalize_text(" ".join(self._text_parts))
        if title:
            self.links.append((title, self._href))
        self._href = ""
        self._text_parts = []


def fetch_html(url: str, timeout: int = 12) -> str:
    request = Request(url, headers={"User-Agent": "WorkConnectAdminBot/0.1 (+official notice collector)"})
    try:
        with urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(content_type, errors="replace")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise RuntimeError(f"official source fetch failed: {url}: {exc}") from exc


def is_allowed_official_url(url: str, allowed_domains: tuple[str, ...]) -> bool:
    lowered = (url or "").lower()
    return lowered.startswith("https://") and any(domain in lowered for domain in allowed_domains)


def is_notice_detail_url(url: str, detail_patterns: tuple[str, ...]) -> bool:
    lowered = (url or "").lower()
    return any(pattern.lower() in lowered for pattern in detail_patterns)


def infer_notice_type(default_type: str, title: str) -> str:
    lower = title.lower()
    if any(term in lower for term in ("비자", "사증", "visa", "체류자격", "e-9", "e-7", "d-2", "f-4")):
        return "VISA_POLICY"
    if any(term in lower for term in ("체류", "외국인등록", "stay", "residence")):
        return "STAY_STATUS"
    if any(term in lower for term in ("고용허가", "외국인고용", "eps", "employment")):
        return "EMPLOYMENT_POLICY"
    if any(term in lower for term in ("보도자료", "press")):
        return "PRESS_RELEASE"
    return default_type
