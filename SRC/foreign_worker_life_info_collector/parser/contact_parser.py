from __future__ import annotations

import re

PHONE_RE = re.compile(r"(?:\+82[-\s]?)?(?:0\d{1,2}[-\s]?\d{3,4}[-\s]?\d{4}|1[568]\d{2}[-\s]?\d{4})")


def parse_phone(text: str) -> str:
    match = PHONE_RE.search(text or "")
    if not match:
        return ""
    phone = re.sub(r"\s+", "-", match.group(0).strip())
    return re.sub(r"-{2,}", "-", phone)
