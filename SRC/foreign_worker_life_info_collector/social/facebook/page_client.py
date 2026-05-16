"""Facebook Page client."""

from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class FacebookPageClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def publish(self, message: str, page_id: str, access_token: str) -> dict:
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        body = urlencode({"message": message, "access_token": access_token}).encode("utf-8")
        request = Request(url, data=body, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception as exc:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "error_code": "FACEBOOK_PUBLISH_ERROR",
                "error_message": str(exc),
            }
        return {
            "status": "PUBLISHED",
            "facebook_post_id": str(payload.get("id", "")),
            "error_code": "",
            "error_message": "",
        }
