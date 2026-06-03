from __future__ import annotations

import json
import os
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from .repository import OccupationRepository


JOB_DEFAULT_API_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"
OCCUPATION_DEFAULT_API_URL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L01.do"

JOB_CODE_KEYS = ("jobCd", "jobCode", "jobsCd", "job_code", "code")
JOB_NAME_KEYS = ("jobNm", "jobName", "jobsNm", "job_name", "name")
OCCUPATION_CODE_KEYS = ("occupationCd", "occupationCode", "jobCd", "code")
OCCUPATION_NAME_KEYS = ("occupationNm", "occupationName", "jobNm", "name")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def first_value(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    lowered = {str(key).lower(): value for key, value in row.items()}
    for key in keys:
        value = row.get(key)
        if value is None:
            value = lowered.get(key.lower())
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def parse_response(raw: str) -> list[dict[str, Any]]:
    raw = raw.strip()
    if not raw:
        return []
    if raw.startswith("{") or raw.startswith("["):
        return parse_json_response(json.loads(raw))
    return parse_xml_response(raw)


def parse_json_response(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("items", "item", "data", "list", "result", "body"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = parse_json_response(value)
            if nested:
                return nested
    return [payload] if payload else []


def parse_xml_response(raw: str) -> list[dict[str, Any]]:
    root = ET.fromstring(raw)
    rows: list[dict[str, Any]] = []
    for node in root.iter():
        children = list(node)
        if not children:
            continue
        row = {strip_namespace(child.tag): (child.text or "").strip() for child in children if child.text is not None}
        if len(row) >= 2:
            rows.append(row)
    leaf_rows = [row for row in rows if any(key.lower().endswith(("cd", "code", "nm", "name")) for key in row)]
    return leaf_rows or rows[:1]


def strip_namespace(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


class BaseEmployment24DictionaryCollector:
    collector_type = ""
    key_env = ""
    url_env = ""
    default_url = ""

    def __init__(self, repository: OccupationRepository, api_url: str | None = None) -> None:
        self.repository = repository
        self.api_url = api_url or os.environ.get(self.url_env, "").strip() or self.default_url

    def auth_key(self) -> str:
        return os.environ.get(self.key_env, "").strip()

    def request_params(self, page: int, size: int) -> dict[str, Any]:
        return {
            "authKey": self.auth_key(),
            "callTp": "L",
            "returnType": os.environ.get("EMPLOYEE_24_OPEN_API_RETURN_TYPE", "XML"),
            "display": size,
            "startPage": page,
        }

    def safe_params(self, page: int, size: int) -> dict[str, Any]:
        params = self.request_params(page, size)
        params.pop("authKey", None)
        return params

    def request_url_without_key(self, page: int, size: int) -> str:
        return f"{self.api_url}?{urlencode(self.safe_params(page, size))}"

    def fetch_page(self, page: int, size: int) -> tuple[str, list[dict[str, Any]]]:
        params = self.request_params(page, size)
        if not params["authKey"]:
            raise RuntimeError(f"{self.key_env} is not configured.")
        if not self.api_url:
            raise RuntimeError(f"{self.url_env} is not configured.")
        url = f"{self.api_url}?{urlencode(params)}"
        try:
            with urlopen(url, timeout=30) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"{self.collector_type} API connection failed") from exc
        return raw, parse_response(raw)

    def run(self, page_from: int = 1, page_to: int = 1, size: int = 100, delay_seconds: float = 0.5) -> dict[str, Any]:
        request_params = {"page_from": page_from, "page_to": page_to, "size": size, "request": self.safe_params(page_from, size)}
        log_id = self.repository.start_log(self.collector_type, request_params)
        requested_count = inserted_count = updated_count = skipped_count = failed_count = 0
        error_messages: list[str] = []
        for page in range(page_from, page_to + 1):
            try:
                raw, rows = self.fetch_page(page, size)
                self.repository.save_raw_response(self.collector_type, self.request_url_without_key(page, size), raw, parsed=True)
                requested_count += len(rows)
                for raw_item in rows:
                    result = self.upsert(raw_item)
                    if result == "inserted":
                        inserted_count += 1
                    elif result == "updated":
                        updated_count += 1
                    else:
                        skipped_count += 1
            except Exception as exc:
                failed_count += 1
                message = str(exc)[:500]
                error_messages.append(f"page {page}: {message}")
                self.repository.save_raw_response(self.collector_type, self.request_url_without_key(page, size), "", parsed=False, error_message=message)
            if page < page_to:
                time.sleep(max(0.2, min(delay_seconds, 1.0)))
        status = "FAILED" if failed_count and requested_count == 0 else "PARTIAL_FAILED" if failed_count else "SUCCESS"
        self.repository.finish_log(
            log_id,
            {
                "status": status,
                "requested_count": requested_count,
                "inserted_count": inserted_count,
                "updated_count": updated_count,
                "skipped_count": skipped_count,
                "failed_count": failed_count,
                "error_message": " / ".join(error_messages)[:1000] if error_messages else None,
            },
        )
        return {
            "runId": log_id,
            "collectorType": self.collector_type,
            "status": status,
            "requestedCount": requested_count,
            "insertedCount": inserted_count,
            "updatedCount": updated_count,
            "skippedCount": skipped_count,
            "failedCount": failed_count,
            "errorMessage": " / ".join(error_messages)[:1000] if error_messages else None,
            "finishedAt": utc_now_iso(),
        }

    def upsert(self, raw_item: dict[str, Any]) -> str:
        raise NotImplementedError


class JobInfoCollector(BaseEmployment24DictionaryCollector):
    collector_type = "JOB"
    key_env = "EMPLOYEE_24_OPEN_API_JOB_KEY"
    url_env = "EMPLOYEE_24_OPEN_API_JOB_URL"
    default_url = JOB_DEFAULT_API_URL

    def upsert(self, raw_item: dict[str, Any]) -> str:
        item = {
            "source": "employment24",
            "job_code": first_value(raw_item, JOB_CODE_KEYS),
            "job_name_ko": first_value(raw_item, JOB_NAME_KEYS),
            "job_name_en": first_value(raw_item, ("jobNameEn", "jobEngNm", "nameEn")),
            "job_category_code": first_value(raw_item, ("jobClcd", "categoryCd", "jobCategoryCode")),
            "job_category_name": first_value(raw_item, ("jobClNm", "categoryNm", "jobCategoryName")),
            "description_ko": first_value(raw_item, ("jobDesc", "description", "descriptionKo", "contents")),
            "description_en": first_value(raw_item, ("descriptionEn", "jobDescEn")),
            "required_skills": first_value(raw_item, ("skill", "skills", "requiredSkills")),
            "related_keywords": first_value(raw_item, ("keyword", "keywords", "relatedKeywords")),
            "raw_response": raw_item,
            "active_yn": "Y",
        }
        return self.repository.upsert_job(item)


class OccupationInfoCollector(BaseEmployment24DictionaryCollector):
    collector_type = "OCCUPATION"
    key_env = "EMPLOYEE_24_OPEN_API_OCCUPATION_KEY"
    url_env = "EMPLOYEE_24_OPEN_API_OCCUPATION_URL"
    default_url = OCCUPATION_DEFAULT_API_URL

    def upsert(self, raw_item: dict[str, Any]) -> str:
        item = {
            "source": "employment24",
            "occupation_code": first_value(raw_item, OCCUPATION_CODE_KEYS),
            "occupation_name_ko": first_value(raw_item, OCCUPATION_NAME_KEYS),
            "occupation_name_en": first_value(raw_item, ("occupationNameEn", "jobEngNm", "nameEn")),
            "occupation_category_code": first_value(raw_item, ("occupationClcd", "categoryCd", "occupationCategoryCode")),
            "occupation_category_name": first_value(raw_item, ("occupationClNm", "categoryNm", "occupationCategoryName")),
            "work_description_ko": first_value(raw_item, ("workDesc", "jobDesc", "description", "contents")),
            "work_description_en": first_value(raw_item, ("workDescriptionEn", "descriptionEn")),
            "required_education": first_value(raw_item, ("education", "requiredEducation", "school")),
            "required_certificates": first_value(raw_item, ("certificate", "certificates", "requiredCertificates")),
            "related_jobs": first_value(raw_item, ("relatedJobs", "jobList", "relatedJob")),
            "outlook": first_value(raw_item, ("outlook", "prospect", "future")),
            "raw_response": raw_item,
            "active_yn": "Y",
        }
        return self.repository.upsert_occupation(item)

