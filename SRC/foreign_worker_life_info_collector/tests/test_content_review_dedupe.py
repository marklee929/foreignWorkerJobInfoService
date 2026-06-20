from __future__ import annotations

import unittest

from foreign_worker_life_info_collector.content.service import (
    build_telegram_review_metadata,
    normalize_review_url,
    score_bucket,
)


def candidate(**overrides):
    base = {
        "id": 101,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "status": "READY_TO_REVIEW",
        "final_publish_score": 67.0,
        "title": "Housing contract checklist for foreign residents",
        "summary_en": "Check deposit, contract period and repair responsibility.",
        "why_it_matters_en": "This helps foreign residents avoid rental disputes.",
        "body_en": "A practical guide to checking housing contracts in Korea.",
        "review_reason": "Needs operator review.",
        "link_url": "https://Example.com/guide/housing?utm_source=newsletter&b=2",
        "source_url": "https://example.com/guide/housing",
        "source_name": "Source A",
        "raw_payload": {"duplicate_count": 1},
    }
    base.update(overrides)
    return base


class ContentReviewDedupeTest(unittest.TestCase):
    def test_score_bucket_boundaries(self) -> None:
        self.assertEqual(score_bucket(0), "0-39")
        self.assertEqual(score_bucket(39.9), "0-39")
        self.assertEqual(score_bucket(40), "40-59")
        self.assertEqual(score_bucket(60), "60-79")
        self.assertEqual(score_bucket(80), "80-100")

    def test_same_candidate_same_state_has_same_review_key(self) -> None:
        first = build_telegram_review_metadata(candidate(), "message one")
        second = build_telegram_review_metadata(candidate(), "message two with same candidate content")

        self.assertEqual(first["telegram_review_key"], second["telegram_review_key"])
        self.assertEqual(first["semantic_review_key"], second["semantic_review_key"])

    def test_status_change_changes_review_key(self) -> None:
        first = build_telegram_review_metadata(candidate(status="READY_TO_REVIEW"), "message")
        second = build_telegram_review_metadata(candidate(status="READY_TO_PUBLISH"), "message")

        self.assertNotEqual(first["telegram_review_key"], second["telegram_review_key"])
        self.assertNotEqual(first["semantic_review_key"], second["semantic_review_key"])

    def test_score_bucket_change_changes_review_key(self) -> None:
        first = build_telegram_review_metadata(candidate(final_publish_score=59), "message")
        second = build_telegram_review_metadata(candidate(final_publish_score=60), "message")

        self.assertEqual(first["score_bucket"], "40-59")
        self.assertEqual(second["score_bucket"], "60-79")
        self.assertNotEqual(first["telegram_review_key"], second["telegram_review_key"])

    def test_same_url_different_candidate_and_source_keeps_same_semantic_key(self) -> None:
        first = build_telegram_review_metadata(candidate(id=101, source_name="Source A"), "message")
        second = build_telegram_review_metadata(candidate(id=202, source_name="Source B"), "message")

        self.assertNotEqual(first["telegram_review_key"], second["telegram_review_key"])
        self.assertEqual(first["semantic_review_key"], second["semantic_review_key"])

    def test_content_change_changes_semantic_key(self) -> None:
        first = build_telegram_review_metadata(candidate(), "message")
        second = build_telegram_review_metadata(
            candidate(body_en="Updated housing guide with changed deposit warning."),
            "message",
        )

        self.assertNotEqual(first["semantic_review_key"], second["semantic_review_key"])

    def test_normalize_review_url_removes_tracking_and_fragment(self) -> None:
        self.assertEqual(
            normalize_review_url("https://Example.COM/path//item/?utm_source=x&b=2&fbclid=abc#section"),
            "https://example.com/path/item?b=2",
        )


if __name__ == "__main__":
    unittest.main()
