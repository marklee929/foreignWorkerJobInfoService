from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from foreign_worker_life_info_collector.utils.content_card_renderer import (
    OUTPUT_SIZE,
    build_content_card_preview,
    select_template_type,
)


def candidate(**overrides):
    base = {
        "id": 3001,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "category": "housing",
        "title": "Housing Deposit Guide in Korea",
        "summary_en": "Confirm the owner name. Keep bank transfer receipts. Ask for written repair terms.",
        "why_it_matters_en": "Housing deposits can be large, and clear records reduce dispute risk.",
        "body_en": "Foreign residents should check the contract, deposit, and payment records before signing.",
        "source_name": "Local support center",
        "original_collected_at": "2026-06-16T12:00:00+09:00",
        "final_publish_score": 84,
        "raw_payload": {},
    }
    base.update(overrides)
    return base


class ContentCardGeneratorTest(unittest.TestCase):
    def test_generates_living_card_png(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_content_card_preview(candidate(), Path(tmp))

            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "CARD_PREVIEW_GENERATED")
            self.assertEqual(result["template_type"], "LIVING_IN_KOREA")
            image_path = Path(result["image_path"])
            self.assertTrue(image_path.exists())
            with Image.open(image_path) as image:
                self.assertEqual(image.size, OUTPUT_SIZE)

    def test_immigration_candidate_uses_visa_template(self) -> None:
        self.assertEqual(
            select_template_type(
                candidate(
                    source_domain="IMMIGRATION_INFO",
                    content_type="IMMIGRATION_NOTICE",
                    category="visa_policy",
                    title="Visa Extension Document Checklist",
                )
            ),
            "VISA_IMMIGRATION",
        )

    def test_korean_public_text_fails_language_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_content_card_preview(candidate(title="체류자격 안내매뉴얼"), Path(tmp))

            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "CARD_TEXT_INVALID_LANGUAGE")
            self.assertTrue(result["card_required"])

    def test_overflow_fails_without_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_content_card_preview(
                candidate(card_bullets=["This bullet contains far more than eighty characters and should fail before any automatic truncation can hide useful context."]),
                Path(tmp),
            )

        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "CARD_TEXT_OVERFLOW")

    def test_long_auto_summary_is_compacted_for_living_card(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = build_content_card_preview(
                candidate(
                    title="Seoul's young singles are redefining home through co-living",
                    summary_en=(
                        "When I lived alone, things like food deliveries made me nervous. "
                        "More foreigners are coming to Korea for work and study, so shared housing can help with safety and daily life."
                    ),
                    why_it_matters_en="Foreign residents may need practical housing options that reduce isolation and make daily life easier.",
                    body_en="Foreign residents should compare rent, deposits, location, privacy, and contract terms before choosing shared housing.",
                    source_name="Korea Times",
                    final_publish_score=91.4,
                    link_url="https://www.koreatimes.co.kr/lifestyle/trends/co-living",
                ),
                Path(tmp),
            )

            self.assertTrue(result["ok"])
            self.assertEqual(result["template_type"], "LIVING_IN_KOREA")
            self.assertTrue(all(len(item) <= 80 for item in result["payload"]["bullets"]))

    def test_news_article_with_valid_link_uses_og_not_card(self) -> None:
        result = build_content_card_preview(
            candidate(
                source_domain="SOCIAL_NEWS",
                content_type="NEWS_ARTICLE",
                link_url="https://example.com/news/article-1",
                source_url="https://example.com/news/article-1",
            )
        )

        self.assertFalse(result["ok"])
        self.assertFalse(result["card_required"])
        self.assertEqual(result["status"], "CARD_NOT_REQUIRED")
        self.assertEqual(result["reason"], "NEWS_ARTICLE_LINK_PREVIEW_USES_OG")

    def test_zero_score_candidate_is_not_card_target(self) -> None:
        result = build_content_card_preview(candidate(final_publish_score=0))

        self.assertFalse(result["ok"])
        self.assertFalse(result["card_required"])
        self.assertEqual(result["reason"], "CARD_BLOCKED_ZERO_SCORE")


if __name__ == "__main__":
    unittest.main()
