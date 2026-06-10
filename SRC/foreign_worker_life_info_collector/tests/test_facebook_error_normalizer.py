from __future__ import annotations

import json
import unittest

from foreign_worker_life_info_collector.social.facebook.error_normalizer import (
    FACEBOOK_LINK_INVALID,
    FACEBOOK_POLICY_BLOCK,
    FACEBOOK_RATE_LIMIT,
    INTERNAL_ENV_MISSING,
    TOKEN_EXPIRED,
    TOKEN_EXPIRING_SOON,
    TOKEN_INVALID,
    TOKEN_PERMISSION_MISSING,
    build_error_context,
    classify_meta_error,
    token_status_snapshot,
)
from foreign_worker_life_info_collector.social.news.models import NewsCandidate
from foreign_worker_life_info_collector.social.news.notifier.telegram_notifier import NewsTelegramNotifier


class FacebookErrorNormalizerTest(unittest.TestCase):
    def test_meta_code_190_expired(self) -> None:
        self.assertEqual(
            classify_meta_error({"code": 190, "message": "Session has expired", "type": "OAuthException"}),
            TOKEN_EXPIRED,
        )

    def test_meta_code_190_invalid(self) -> None:
        self.assertEqual(
            classify_meta_error({"code": 190, "message": "Error validating access token", "type": "OAuthException"}),
            TOKEN_INVALID,
        )

    def test_meta_code_200_permission(self) -> None:
        self.assertEqual(classify_meta_error({"code": 200, "message": "Permissions error"}), TOKEN_PERMISSION_MISSING)

    def test_meta_code_613_rate_limit(self) -> None:
        self.assertEqual(classify_meta_error({"code": 613, "message": "Calls to this api have exceeded"}), FACEBOOK_RATE_LIMIT)

    def test_meta_code_368_policy_block(self) -> None:
        self.assertEqual(classify_meta_error({"code": 368, "message": "Temporarily blocked"}), FACEBOOK_POLICY_BLOCK)

    def test_meta_code_100_link_invalid(self) -> None:
        self.assertEqual(classify_meta_error({"code": 100, "message": "Invalid link URL"}), FACEBOOK_LINK_INVALID)

    def test_internal_missing_env(self) -> None:
        context = build_error_context(error_code="MISSING_FACEBOOK_ENV", error_message="missing")
        self.assertEqual(context["error_category"], INTERNAL_ENV_MISSING)
        self.assertFalse(context["retryable_yn"])

    def test_expiring_soon_valid_token_is_snapshot_not_failure(self) -> None:
        snapshot = token_status_snapshot(
            token="secret-token",
            token_debug={"token_type": "PAGE", "is_valid": True, "profile_id": "123", "scopes": ["pages_manage_posts"], "expires_at": 9999999999},
            page_id="123",
            required_scopes={"pages_manage_posts"},
        )
        self.assertTrue(snapshot["page_id_match"])
        self.assertTrue(snapshot["required_scopes_present"])
        self.assertNotEqual(snapshot["token_fingerprint"], "secret-token")
        self.assertEqual(TOKEN_EXPIRING_SOON, "TOKEN_EXPIRING_SOON")

    def test_telegram_failure_message_includes_meta_and_token_status(self) -> None:
        body = json.dumps(
            {
                "error": {
                    "message": "Error validating access token",
                    "type": "OAuthException",
                    "code": 190,
                    "error_subcode": 463,
                    "fbtrace_id": "ABC123",
                }
            }
        )
        context = build_error_context(
            error_code="190",
            response_code="400",
            response_body=body,
            link_url="https://example.com/news",
            token_status={"token_type": "PAGE", "is_valid": False, "page_id_match": True, "required_scopes_present": True, "token_fingerprint": "abcd1234"},
        )
        candidate = NewsCandidate(title="Korea visa update", source_url="https://example.com/news", source_type="test", id=123)
        message = NewsTelegramNotifier().build_failure_message(
            candidate,
            "FAILED_PERMISSION",
            "fallback",
            {"error_category": context["error_category"], "error_context": context},
        )
        self.assertIn("Error Category: TOKEN_INVALID", message)
        self.assertIn("fbtrace_id: ABC123", message)
        self.assertIn("fingerprint: abcd1234", message)


if __name__ == "__main__":
    unittest.main()
