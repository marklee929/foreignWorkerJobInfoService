from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from foreign_worker_life_info_collector.utils.content_card_renderer import build_content_card_preview


def main() -> None:
    candidate = {
        "id": 900001,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "category": "healthcare",
        "title": "How to Check Health Insurance Payments in Korea",
        "summary_en": "Confirm your payment status. Keep monthly receipts. Ask NHIS before a deadline passes.",
        "why_it_matters_en": "Health insurance status can affect clinic visits, visa renewals, and unpaid bills.",
        "body_en": "Foreign residents should check payment records and ask official support channels when details are unclear.",
        "source_name": "NHIS",
        "original_collected_at": "2026-06-16T12:00:00+09:00",
        "final_publish_score": 88,
        "raw_payload": {"content_format": "CHECKLIST_CARD"},
    }
    result = build_content_card_preview(candidate)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
