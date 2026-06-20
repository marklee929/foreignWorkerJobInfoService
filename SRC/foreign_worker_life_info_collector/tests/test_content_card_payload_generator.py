from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from foreign_worker_life_info_collector.utils.content_card_renderer import OUTPUT_SIZE
from foreign_worker_life_info_collector.utils.content_card_payload_generator import (
    CardPayloadRequest,
    generate_card_from_text,
    validate_generated_payload,
)


def request(**overrides):
    base = {
        "template_type": "CHECKLIST_HOWTO",
        "content_text": (
            "Health insurance status can affect clinic visits, visa renewals, and unpaid bills. "
            "Foreign residents should confirm payment status, keep receipts, and ask NHIS before deadlines."
        ),
        "source": "NHIS",
        "link": "https://www.nhis.or.kr",
        "date": "2026-06-16",
    }
    base.update(overrides)
    return CardPayloadRequest(**base)


class ContentCardPayloadGeneratorTest(unittest.TestCase):
    def test_checklist_sample_mode_generates_payload_and_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = generate_card_from_text(request(), output_dir=Path(tmp), sample_mode=True)

            self.assertTrue(result["ok"])
            self.assertEqual(result["validation_status"], "VALID")
            self.assertEqual(result["template_type"], "CHECKLIST_HOWTO")
            self.assertEqual(len(result["payload"]["bullets"]), 4)
            image_path = Path(result["generated_image_path"])
            payload_path = Path(result["generated_payload_path"])
            self.assertTrue(image_path.exists())
            self.assertTrue(payload_path.exists())
            self.assertTrue(image_path.name.startswith("CHECKLIST_HOWTO_20260616") or image_path.name.startswith("CHECKLIST_HOWTO_"))
            with Image.open(image_path) as image:
                self.assertEqual(image.size, OUTPUT_SIZE)
            saved_payload = json.loads(payload_path.read_text(encoding="utf-8"))
            self.assertEqual(saved_payload["footer_url"], "WorkConnect Korea")

    def test_korean_public_text_fails_validation(self) -> None:
        payload = {
            "template_type": "LIVING_IN_KOREA",
            "title": "체류자격 안내",
            "subtitle": "Foreign residents should check official information.",
            "bullets": ["Check your address.", "Keep receipts.", "Ask official support."],
            "source": "WorkConnect Guide",
            "date": "2026-06-16",
            "footer_url": "WorkConnect Korea",
        }

        with self.assertRaises(Exception) as raised:
            validate_generated_payload(payload, request(template_type="LIVING_IN_KOREA"), "LIVING_IN_KOREA")

        self.assertEqual(getattr(raised.exception, "code", ""), "CARD_TEXT_INVALID_LANGUAGE")

    def test_llama_unavailable_returns_clear_error(self) -> None:
        with patch.dict("os.environ", {"LOCAL_LLAMA_ENABLED": "false"}):
            result = generate_card_from_text(request(), sample_mode=False)

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "LLAMA_UNAVAILABLE")

    def test_checklist_three_bullets_fails_validation(self) -> None:
        payload = {
            "template_type": "CHECKLIST_HOWTO",
            "title": "Health Insurance Payment Checklist",
            "subtitle": "Keep payment records before clinic visits and renewals.",
            "bullets": ["Check payment status.", "Keep monthly receipts.", "Ask NHIS before deadlines."],
            "source": "NHIS",
            "date": "2026-06-16",
            "footer_url": "WorkConnect Korea",
        }

        with self.assertRaises(Exception) as raised:
            validate_generated_payload(payload, request(), "CHECKLIST_HOWTO")

        self.assertEqual(getattr(raised.exception, "code", ""), "CARD_BULLET_COUNT_INVALID")

    def test_alert_review_three_bullets_passes_validation(self) -> None:
        payload = {
            "template_type": "ALERT_REVIEW",
            "title": "Check Official Sources Before Making Visa Decisions",
            "subtitle": "Some updates may apply only to specific visa types or situations.",
            "bullets": [
                "Confirm the original notice before applying.",
                "Check whether the rule applies to your visa type.",
                "Ask an official office if the information is unclear.",
            ],
            "source": "HiKorea",
            "date": "2026-06-16",
            "footer_url": "WorkConnect Korea",
        }

        validated = validate_generated_payload(
            payload,
            request(template_type="ALERT_REVIEW", source="HiKorea", link="https://www.hikorea.go.kr"),
            "ALERT_REVIEW",
        )

        self.assertEqual(validated["template_type"], "ALERT_REVIEW")
        self.assertEqual(len(validated["bullets"]), 3)


if __name__ == "__main__":
    unittest.main()
