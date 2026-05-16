"""Facebook publisher for automated news pipeline."""

from __future__ import annotations

import os

from ...facebook.page_client import FacebookPageClient
from ...facebook.post_builder import build_text_post
from ..models import NewsCandidate

FACEBOOK_PAGE_ID_ENV = "FACEBOOK_PAGE_ID"
FACEBOOK_PAGE_ACCESS_TOKEN_ENV = "FACEBOOK_PAGE_ACCESS_TOKEN"


class FacebookPublisher:
    def __init__(self, client: FacebookPageClient | None = None):
        self.client = client or FacebookPageClient()

    def build_message(self, candidate: NewsCandidate) -> str:
        summary = candidate.short_summary or candidate.summary
        parts = [
            candidate.title,
            summary,
            candidate.relevance_reason,
            candidate.source_url,
            "#WorkConnectKorea #ForeignWorkersKorea",
        ]
        return "\n\n".join(part.strip() for part in parts if part and part.strip())

    def publish(self, candidate: NewsCandidate, dry_run: bool = True) -> dict:
        message = self.build_message(candidate)
        if dry_run:
            return {
                "status": "DRY_RUN",
                "facebook_post_id": f"dry-run-news-{candidate.id}",
                "page_id": "dry-run",
                "message": message,
            }

        page_id = os.getenv(FACEBOOK_PAGE_ID_ENV, "").strip()
        access_token = os.getenv(FACEBOOK_PAGE_ACCESS_TOKEN_ENV, "").strip()
        if not page_id or not access_token:
            return {
                "status": "FAILED",
                "facebook_post_id": "",
                "page_id": page_id,
                "message": message,
                "error_code": "MISSING_FACEBOOK_ENV",
                "error_message": "FACEBOOK_PAGE_ID and FACEBOOK_PAGE_ACCESS_TOKEN are required for real publishing.",
            }

        result = self.client.publish(message=message, page_id=page_id, access_token=access_token)
        return {
            "status": result.get("status", "PUBLISHED"),
            "facebook_post_id": result.get("facebook_post_id", ""),
            "page_id": page_id,
            "message": message,
            "error_code": result.get("error_code", ""),
            "error_message": result.get("error_message", ""),
        }
