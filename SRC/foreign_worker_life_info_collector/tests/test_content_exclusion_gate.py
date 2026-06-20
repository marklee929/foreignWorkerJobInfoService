from __future__ import annotations

import unittest

from foreign_worker_life_info_collector.content.service import (
    ContentService,
    apply_content_quality_gate,
    content_quality_gate,
)


class FakeRepository:
    pass


def candidate(**overrides):
    base = {
        "id": 1,
        "source_domain": "LIVING_INFO",
        "content_type": "LIVING_GUIDE",
        "priority_group": "SECONDARY",
        "category": "settlement_life",
        "title": "Foreign worker rights notice in Korea",
        "summary_en": "Foreign workers in Korea can check labor rights and support steps.",
        "why_it_matters_en": "This helps workers decide what to check before applying.",
        "body_en": "The notice explains worker rights, support centers, eligibility, and application steps.",
        "link_url": "https://example.go.kr/notice/foreign-worker-rights",
        "source_url": "https://example.go.kr/notice/foreign-worker-rights",
        "source_name": "MOEL",
        "final_publish_score": 72,
        "quality_score": 72,
        "review_reason": "",
        "status": "READY_TO_REVIEW",
        "raw_payload": {},
    }
    base.update(overrides)
    return base


class ContentExclusionGateTest(unittest.TestCase):
    def test_japan_policy_with_missing_link_is_blocked(self) -> None:
        decision = content_quality_gate(
            candidate(
                title="Japan's Foreigner Policy Skirts Key Issues",
                summary_en="Japan immigration policy debate.",
                body_en="Japan-only immigration policy story.",
                link_url="",
                source_url="",
                final_publish_score=0,
            )
        )

        self.assertEqual(decision.code, "BLOCKED_SOURCE_INVALID")
        self.assertFalse(decision.review_eligible)
        self.assertFalse(decision.publish_eligible)

    def test_bali_travel_story_is_blocked(self) -> None:
        decision = content_quality_gate(
            candidate(
                title="Travel Confidence Tested as Bali Authorities Counter South Korea Warning",
                category="travel",
                summary_en="Bali tourism officials respond to a travel warning.",
                body_en="A destination safety and tourism market story.",
                link_url="https://travel.example.com/bali-warning",
                source_url="https://travel.example.com/bali-warning",
                final_publish_score=65,
            )
        )

        self.assertEqual(decision.code, "BLOCKED_GENERIC_TRAVEL")

    def test_generic_crypto_guide_is_blocked(self) -> None:
        decision = content_quality_gate(
            candidate(
                title="Crypto in South Korea: The Ultimate Guide",
                category="finance",
                summary_en="A general cryptocurrency exchange guide.",
                body_en="Bitcoin, Ethereum and token trading overview for investors.",
                link_url="https://example.com/crypto-korea-guide",
                source_url="https://example.com/crypto-korea-guide",
                final_publish_score=38,
            )
        )

        self.assertEqual(decision.code, "BLOCKED_GENERIC_CRYPTO")

    def test_korean_local_election_article_is_blocked(self) -> None:
        decision = content_quality_gate(
            candidate(
                title="More foreigners than ever can vote in Korea's local elections",
                category="settlement_life",
                summary_en="A local election and governance story.",
                body_en="The article discusses local election politics and campaign issues.",
                link_url="https://example.com/korea-local-election",
                source_url="https://example.com/korea-local-election",
                final_publish_score=55,
            )
        )

        self.assertEqual(decision.code, "BLOCKED_DOMESTIC_POLITICS")

    def test_minimum_wage_committee_meeting_is_watch_topic(self) -> None:
        decision = content_quality_gate(
            candidate(
                title="Minimum Wage Committee meeting held in Korea",
                category="employment",
                summary_en="The committee held a meeting and discussed the agenda.",
                body_en="The item reports a meeting schedule only, with no wage rate or worker action.",
                link_url="https://example.go.kr/minimum-wage-meeting",
                source_url="https://example.go.kr/minimum-wage-meeting",
                final_publish_score=68,
            )
        )

        self.assertEqual(decision.code, "WATCH_TOPIC_ONLY")
        self.assertEqual(decision.watch_topic, "MINIMUM_WAGE_2026")

    def test_foreign_worker_rights_notice_is_review_eligible(self) -> None:
        decision = content_quality_gate(candidate())

        self.assertEqual(decision.code, "REVIEW_ELIGIBLE")
        self.assertTrue(decision.review_eligible)
        self.assertTrue(decision.publish_eligible)
        self.assertTrue(ContentService(repository=FakeRepository()).requires_telegram_review(candidate()))

    def test_hikorea_official_lookup_is_review_eligible_even_with_lower_score(self) -> None:
        item = candidate(
            source_domain="IMMIGRATION_INFO",
            content_type="IMMIGRATION_NOTICE",
            priority_group="OFFICIAL_NOTICE",
            category="immigration",
            title="HiKorea medical institution lookup manual",
            summary_en="Official lookup manual for medical institutions and immigration agency offices.",
            body_en="Use the official HiKorea lookup to check institution address, location, and contact.",
            link_url="https://www.hikorea.go.kr/info/medical-lookup",
            source_url="https://www.hikorea.go.kr/info/medical-lookup",
            source_name="HiKorea",
            final_publish_score=25,
        )

        decision = content_quality_gate(item)

        self.assertEqual(decision.code, "REVIEW_ELIGIBLE")
        self.assertTrue(decision.review_eligible)

    def test_zip_only_official_notice_is_evidence_only(self) -> None:
        item = candidate(
            source_domain="IMMIGRATION_INFO",
            content_type="IMMIGRATION_NOTICE",
            priority_group="OFFICIAL_NOTICE",
            category="EMPLOYMENT_POLICY",
            title="K-New Deal Academy training notice",
            summary_en="Attached file exists.",
            why_it_matters_en="",
            body_en="Attachment exists.",
            link_url="https://www.moel.go.kr/common/downloadAllZip.do?bbs_seq=19547&bbs_id=12",
            source_url="https://www.moel.go.kr/common/downloadAllZip.do?bbs_seq=19547&bbs_id=12",
            source_name="MOEL Foreign Employment Notice",
            final_publish_score=82,
            quality_score=82,
            status="READY_TO_REVIEW",
            raw_payload={
                "raw_response": {
                    "attachment_filename": "19547_20260621012124.zip",
                    "attachment_size": "120 KB",
                }
            },
        )

        decision = content_quality_gate(item)
        payload = apply_content_quality_gate(item)

        self.assertEqual(decision.code, "ATTACHMENT_REVIEW_REQUIRED")
        self.assertFalse(decision.review_eligible)
        self.assertFalse(decision.publish_eligible)
        self.assertFalse(ContentService(repository=FakeRepository()).requires_telegram_review(payload))
        self.assertEqual(payload["status"], "SCORED")
        self.assertEqual(payload["content_type"], "DOCUMENT_EXTRACTION_REQUIRED")
        self.assertEqual(payload["priority_group"], "EVIDENCE_ONLY")
        self.assertLessEqual(payload["final_publish_score"], 39.0)
        self.assertEqual(payload["raw_payload"]["attachment_review_state"], "ATTACHMENT_REVIEW_REQUIRED")
        self.assertEqual(payload["raw_payload"]["classification_status"], "CLASSIFICATION_PENDING")

    def test_attachment_only_review_message_has_no_facebook_preview(self) -> None:
        item = candidate(
            id=77,
            source_domain="IMMIGRATION_INFO",
            content_type="IMMIGRATION_NOTICE",
            priority_group="OFFICIAL_NOTICE",
            title="Small business support attachment notice",
            summary_en="Attachment exists.",
            body_en="Attachment exists.",
            link_url="https://www.moel.go.kr/common/downloadAllZip.do?bbs_seq=19548&bbs_id=12",
            source_url="https://www.moel.go.kr/common/downloadAllZip.do?bbs_seq=19548&bbs_id=12",
            source_name="MOEL",
            raw_payload={"raw_response": {"attachment_filename": "notice.zip", "attachment_size": "88 KB"}},
        )

        message = ContentService(repository=FakeRepository()).telegram_review_message(item)

        self.assertIn("[Content Review - Evidence Only]", message)
        self.assertIn("attachment_content_not_inspected", message)
        self.assertIn("bbs_seq: 19548", message)
        self.assertIn("notice.zip", message)
        self.assertNotIn("[Facebook Format Preview]", message)
        self.assertNotIn("#KoreaJobs", message)

    def test_system_text_is_blocked_and_payload_is_downgraded(self) -> None:
        payload = apply_content_quality_gate(
            candidate(
                summary_en="No article body was saved.",
                body_en="Content unavailable.",
                status="READY_TO_PUBLISH",
                final_publish_score=82,
                quality_score=82,
            )
        )

        self.assertEqual(payload["status"], "SCORED")
        self.assertEqual(payload["final_publish_score"], 0.0)
        self.assertEqual(payload["raw_payload"]["content_quality_gate_code"], "BLOCKED_SYSTEM_TEXT")


if __name__ == "__main__":
    unittest.main()
