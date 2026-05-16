from __future__ import annotations

import re
from typing import Tuple

SIDO_PATTERN = r"서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주"
ADDRESS_RE = re.compile(
    rf"({SIDO_PATTERN})(?:특별시|광역시|특별자치시|특별자치도|도)?\s+([가-힣A-Za-z0-9]+(?:시|군|구))[^\n,;]*"
)


def parse_address(text: str) -> str:
    match = ADDRESS_RE.search(text or "")
    return match.group(0).strip() if match else ""


def split_region(address: str) -> Tuple[str, str]:
    if not address:
        return "", ""
    parts = address.split()
    sido = parts[0] if parts else ""
    sigungu = parts[1] if len(parts) > 1 and (parts[1].endswith("시") or parts[1].endswith("군") or parts[1].endswith("구")) else ""
    return sido, sigungu
