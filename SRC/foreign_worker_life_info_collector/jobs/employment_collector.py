from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .repository import JobCollectorRepository


DEFAULT_API_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"
FIELD_MAP = {
    "wantedAuthNo": "wantedAuthNo",
    "company": "company",
    "busino": "busino",
    "indTpNm": "indTpNm",
    "title": "title",
    "salTpNm": "salTpNm",
    "sal": "sal",
    "minSal": "minSal",
    "maxSal": "maxSal",
    "region": "region",
    "holidayTpNm": "holidayTpNm",
    "minEdubg": "minEdubg",
    "maxEdubg": "maxEdubg",
    "career": "career",
    "regDt": "regDt",
    "closeDt": "closeDt",
    "infoSvc": "infoSvc",
    "wantedInfoUrl": "wantedInfoUrl",
    "wantedMobileInfoUrl": "wantedMobileInfoUrl",
    "zipCd": "zipCd",
    "strtnmCd": "strtnmCd",
    "basicAddr": "basicAddr",
    "detailAddr": "detailAddr",
    "empTpCd": "empTpCd",
    "jobsCd": "jobsCd",
    "smodifyDtm": "smodifyDtm",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def text_of(parent: ET.Element, tag: str) -> str:
    node = parent.find(f".//{tag}")
    return (node.text or "").strip() if node is not None and node.text else ""


def find_posting_nodes(root: ET.Element) -> list[ET.Element]:
    nodes = []
    for node in root.iter():
        if node is not root and node.find("wantedAuthNo") is not None:
            nodes.append(node)
    return nodes


class EmploymentJobCollector:
    def __init__(self, repository: JobCollectorRepository, api_url: str | None = None) -> None:
        self.repository = repository
        self.api_url = api_url or os.environ.get("EMPLOYEE_24_OPEN_API_EMPLOYMENT_URL") or os.environ.get("WORK24_EMPLOYMENT_API_URL") or DEFAULT_API_URL

    def auth_key(self) -> str:
        return os.environ.get("EMPLOYEE_24_OPEN_API_EMPLOYMENT_KEY", "").strip()

    def request_params(self, display: int, start_page: int, sort_order_by: str) -> dict[str, Any]:
        return {
            "authKey": self.auth_key(),
            "callTp": "L",
            "returnType": "XML",
            "display": display,
            "startPage": start_page,
            "sortOrderBy": sort_order_by,
        }

    def safe_request_params(self, display: int, start_page: int, sort_order_by: str) -> dict[str, Any]:
        return {
            "callTp": "L",
            "returnType": "XML",
            "display": display,
            "startPage": start_page,
            "sortOrderBy": sort_order_by,
        }

    def fetch_page(self, display: int, start_page: int, sort_order_by: str) -> tuple[str, list[dict[str, Any]]]:
        params = self.request_params(display, start_page, sort_order_by)
        if not params["authKey"]:
            raise RuntimeError("EMPLOYEE_24_OPEN_API_EMPLOYMENT_KEY가 설정되어 있지 않습니다.")
        url = f"{self.api_url}?{urlencode(params)}"
        try:
            with urlopen(url, timeout=30) as response:
                raw_xml = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError("채용정보 API 연결 실패") from exc

        root = ET.fromstring(raw_xml)
        error_node = root.find(".//error")
        if error_node is not None and (error_node.text or "").strip():
            raise RuntimeError((error_node.text or "").strip()[:300])
        postings = []
        for node in find_posting_nodes(root):
            wanted_auth_no = text_of(node, "wantedAuthNo")
            if not wanted_auth_no:
                continue
            item = {target: text_of(node, source) for source, target in FIELD_MAP.items()}
            item["rawXml"] = ET.tostring(node, encoding="unicode")
            item["collectedAt"] = utc_now_iso()
            postings.append(item)
        return raw_xml, postings

    def run(
        self,
        display: int = 100,
        start_page_from: int = 1,
        start_page_to: int = 10,
        sort_order_by: str = "DESC",
        delay_seconds: float = 0.7,
    ) -> dict[str, Any]:
        started_at = utc_now_iso()
        safe_params = self.safe_request_params(display, start_page_from, sort_order_by)
        run_id = self.repository.start_run(started_at, start_page_from, start_page_to, display, sort_order_by, safe_params)
        total_received = 0
        inserted_count = 0
        updated_count = 0
        skipped_count = 0
        failed_pages: list[dict[str, Any]] = []
        error_message = ""

        for page in range(start_page_from, start_page_to + 1):
            try:
                _, postings = self.fetch_page(display=display, start_page=page, sort_order_by=sort_order_by)
                total_received += len(postings)
                for posting in postings:
                    result = self.repository.upsert_posting(posting)
                    if result == "inserted":
                        inserted_count += 1
                    elif result == "updated":
                        updated_count += 1
                    else:
                        skipped_count += 1
            except Exception as exc:
                message = str(exc)[:300]
                failed_pages.append({"page": page, "message": message})
                error_message = message
            if page < start_page_to:
                time.sleep(max(0.5, min(delay_seconds, 1.0)))

        status = "FAILED" if failed_pages and total_received == 0 else "PARTIAL_FAILED" if failed_pages else "COMPLETED"
        ended_at = utc_now_iso()
        self.repository.finish_run(
            run_id,
            {
                "ended_at": ended_at,
                "total_received": total_received,
                "inserted_count": inserted_count,
                "updated_count": updated_count,
                "skipped_count": skipped_count,
                "failed_count": len(failed_pages),
                "failed_pages": failed_pages,
                "status": status,
                "error_message": error_message or None,
            },
        )
        return {
            "runId": run_id,
            "startedAt": started_at,
            "endedAt": ended_at,
            "pageFrom": start_page_from,
            "pageTo": start_page_to,
            "display": display,
            "sortOrderBy": sort_order_by,
            "totalReceived": total_received,
            "insertedCount": inserted_count,
            "updatedCount": updated_count,
            "skippedCount": skipped_count,
            "failedCount": len(failed_pages),
            "failedPages": failed_pages,
            "status": status,
            "errorMessage": error_message or None,
            "zeroResultRequestParams": safe_params if total_received == 0 else None,
        }
