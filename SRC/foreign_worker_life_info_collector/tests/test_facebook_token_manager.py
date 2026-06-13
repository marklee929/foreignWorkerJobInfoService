from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from foreign_worker_life_info_collector.social.facebook.token_manager import (
    FACEBOOK_APP_ID_ENV,
    FACEBOOK_APP_SECRET_ENV,
    FACEBOOK_PAGE_ACCESS_TOKEN_ENV,
    FACEBOOK_PAGE_ID_ENV,
    FACEBOOK_USER_ACCESS_TOKEN_ENV,
    FacebookTokenManager,
)


class FakeFacebookTokenManager(FacebookTokenManager):
    def exchange_long_lived_user_token(self, user_token: str) -> dict:
        return {"access_token": f"long-{user_token}", "expires_in": 3600}

    def fetch_page_token(self, *, user_token: str, page_id: str) -> dict:
        return {"id": page_id, "name": "WorkConnect Korea", "access_token": f"page-{user_token}"}

    def debug_token(self, input_token: str) -> dict:
        return {
            "token_type": "PAGE",
            "is_valid": True,
            "profile_id": os.environ.get(FACEBOOK_PAGE_ID_ENV, ""),
            "scopes": ["pages_manage_posts", "pages_read_engagement"],
            "expires_at": 0,
            "app_id": "app",
            "checked_at": 1,
        }


class FacebookTokenManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.old_env = {key: os.environ.get(key) for key in [
            FACEBOOK_APP_ID_ENV,
            FACEBOOK_APP_SECRET_ENV,
            FACEBOOK_PAGE_ACCESS_TOKEN_ENV,
            FACEBOOK_PAGE_ID_ENV,
            FACEBOOK_USER_ACCESS_TOKEN_ENV,
        ]}
        for key in self.old_env:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self.old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_refresh_writes_config_and_selects_page_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "facebook_config.json"
            os.environ[FACEBOOK_APP_ID_ENV] = "app-id"
            os.environ[FACEBOOK_APP_SECRET_ENV] = "app-secret"
            os.environ[FACEBOOK_PAGE_ID_ENV] = "810804142117301"
            os.environ[FACEBOOK_USER_ACCESS_TOKEN_ENV] = "short-user"

            selection = FakeFacebookTokenManager(config_path=config_path).get_page_token(force_refresh=True)

            self.assertEqual(selection.source, "refreshed_facebook_config.json")
            self.assertEqual(selection.access_token, "page-long-short-user")
            self.assertTrue(config_path.exists())
            summary = FakeFacebookTokenManager(config_path=config_path).safe_config_summary()
            self.assertEqual(summary["page_id"], "810804142117301")
            self.assertEqual(summary["page_name"], "WorkConnect Korea")
            self.assertTrue(summary["page_token_fingerprint"])

    def test_refresh_failure_falls_back_to_env_page_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "facebook_config.json"
            os.environ[FACEBOOK_PAGE_ID_ENV] = "810804142117301"
            os.environ[FACEBOOK_PAGE_ACCESS_TOKEN_ENV] = "env-page-token"

            selection = FacebookTokenManager(config_path=config_path).get_page_token()

            self.assertEqual(selection.source, "env_fallback")
            self.assertEqual(selection.access_token, "env-page-token")
            self.assertTrue((selection.token_status or {}).get("refresh_error"))


if __name__ == "__main__":
    unittest.main()
