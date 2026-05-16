from __future__ import annotations

from datetime import datetime, timezone


def is_stale(collected_at: str, max_age_days: int = 90) -> bool:
    try:
        collected = datetime.fromisoformat(collected_at.replace("Z", "+00:00"))
    except ValueError:
        return True
    return (datetime.now(timezone.utc) - collected).days > max_age_days
