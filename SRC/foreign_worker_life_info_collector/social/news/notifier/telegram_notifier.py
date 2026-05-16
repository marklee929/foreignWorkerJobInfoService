"""Telegram result notification for automated news pipeline."""

from __future__ import annotations

import os

from ...telegram.notifier import TelegramNotifier as SharedTelegramNotifier
from ..models import NewsCandidate

TELEGRAM_BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID_ENV = "TELEGRAM_CHAT_ID"


class NewsTelegramNotifier:
    def __init__(self, notifier: SharedTelegramNotifier | None = None):
        self.notifier = notifier or SharedTelegramNotifier()

    def build_message(self, candidate: NewsCandidate, status: str, facebook_post_id: str = "", error_message: str = "") -> str:
        return "\n".join(
            part
            for part in (
                "[WorkConnect News Published]",
                f"Status: {status}",
                f"Title: {candidate.title}",
                f"Source: {candidate.source_url}",
                f"Facebook Post ID: {facebook_post_id}" if facebook_post_id else "",
                f"Duplicate score: {candidate.duplicate_risk_score:.2f}",
                f"Summary: {candidate.short_summary or candidate.summary}",
                f"Error: {error_message}" if error_message else "",
            )
            if part
        )

    def notify_publish_result(
        self,
        candidate: NewsCandidate,
        status: str,
        facebook_post_id: str = "",
        error_message: str = "",
        dry_run: bool = True,
    ) -> dict:
        message = self.build_message(candidate, status, facebook_post_id, error_message)
        if dry_run:
            return {"status": "DRY_RUN", "message": message, "error_message": ""}

        if not os.getenv(TELEGRAM_BOT_TOKEN_ENV, "").strip() or not os.getenv(TELEGRAM_CHAT_ID_ENV, "").strip():
            return {
                "status": "FAILED",
                "message": message,
                "error_message": "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required for real notification.",
            }

        try:
            result = self.notifier.notify(message)
        except Exception as exc:
            return {"status": "FAILED", "message": message, "error_message": str(exc)}
        return {"status": result.get("status", "NOTIFIED"), "message": message, "error_message": result.get("error_message", "")}
