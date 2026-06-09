"""Telegram result notification for automated news pipeline."""

from __future__ import annotations

import os

from ....utils.text_normalizer import normalize_plain_text
from ...telegram.notifier import TelegramNotifier as SharedTelegramNotifier
from ..models import NewsCandidate

TELEGRAM_BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID_ENV = "TELEGRAM_CHAT_ID"


class NewsTelegramNotifier:
    def __init__(self, notifier: SharedTelegramNotifier | None = None):
        self.notifier = notifier or SharedTelegramNotifier()

    def build_message(
        self,
        candidate: NewsCandidate,
        status: str,
        facebook_post_id: str = "",
        facebook_post_url: str = "",
        error_message: str = "",
    ) -> str:
        if error_message or status in {"FAILED", "FAILED_RETRYABLE", "AUTO_RETRY_BLOCKED"}:
            return "\n".join(
                [
                    "⚠️ Facebook Publish Failed",
                    "",
                    f"Candidate: {candidate.id or '-'}",
                    f"Title: {normalize_plain_text(candidate.title)}",
                    f"Reason: {normalize_plain_text(error_message or candidate.fail_reason or 'Unknown error')}",
                    f"Status: {status}",
                    f"Source: {candidate.source_url}",
                ]
            )

        return "\n".join(
            [
                "✅ 뉴스 자동 게시 완료",
                "",
                f"제목: {normalize_plain_text(candidate.title)}",
                f"카테고리: {normalize_plain_text(candidate.category or '-')}",
                f"점수: {candidate.evaluation_score:.2f}",
                f"위험도: {candidate.risk_level or 'LOW'}",
                "",
                f"요약:\n{normalize_plain_text(candidate.short_summary or candidate.summary)}",
                "",
                f"원문 기사:\n{candidate.source_url}",
                "",
                f"Facebook 게시글:\n{facebook_post_url or facebook_post_id}",
            ]
        )

    def notify_failure(self, candidate: NewsCandidate, error_message: str, dry_run: bool = False) -> dict:
        return self.notify_publish_result(candidate, status="FAILED", error_message=error_message, dry_run=dry_run)

    def notify_operational_alert(self, title: str, message: str, dry_run: bool = False) -> dict:
        text = "\n".join([f"⚠️ {normalize_plain_text(title)}", "", normalize_plain_text(message)])
        return self._send(text, dry_run=dry_run)

    def notify_cooldown(self, cooldown: dict, dry_run: bool = False) -> dict:
        message = "\n".join(
            [
                "⏳ News Publishing Cooldown",
                "",
                f"Last post: {cooldown.get('last_post_at') or '-'}",
                f"Next publish: {cooldown.get('next_publish_at') or '-'}",
                f"Remaining: {cooldown.get('remaining_minutes', 0)} minutes",
            ]
        )
        return self._send(message, dry_run=dry_run)

    def notify_no_candidate(self, selection: dict, dry_run: bool = False) -> dict:
        message = "\n".join(
            [
                "⚠️ No Publish Candidate Found",
                "",
                f"Ready: {selection.get('ready_count', 0)}",
                f"Expanded: {selection.get('expanded_candidate_count', 0)}",
                f"Window Articles: {selection.get('today_article_count', 0)}",
            ]
        )
        return self._send(message, dry_run=dry_run)

    def notify_no_safe_candidate(self, selection: dict, dry_run: bool = False) -> dict:
        message = "\n".join(
            [
                "⚠️ No Safe Candidate",
                "",
                f"Window Articles: {selection.get('today_article_count', 0)}",
                f"Window Average Score: {selection.get('today_avg_score', 0)}",
                f"Threshold: {selection.get('threshold_used') or 40}",
            ]
        )
        return self._send(message, dry_run=dry_run)

    def notify_facebook_error(self, candidate: NewsCandidate, reason: str, status: str, dry_run: bool = False) -> dict:
        message = "\n".join(
            [
                "⚠️ Facebook Publish Failed",
                "",
                f"Candidate: {candidate.id or '-'}",
                f"Title: {normalize_plain_text(candidate.title)}",
                f"Reason: {normalize_plain_text(reason or candidate.fail_reason or 'Unknown error')}",
                f"Status: {status}",
            ]
        )
        return self._send(message, dry_run=dry_run)

    def notify_publish_result(
        self,
        candidate: NewsCandidate,
        status: str,
        facebook_post_id: str = "",
        facebook_post_url: str = "",
        error_message: str = "",
        dry_run: bool = False,
    ) -> dict:
        message = self.build_message(candidate, status, facebook_post_id, facebook_post_url, error_message)
        return self._send(message, dry_run=dry_run)

    def _send(self, message: str, dry_run: bool = False) -> dict:
        if dry_run:
            return {"status": "DRY_RUN", "message": message, "error_message": ""}

        if not os.getenv(TELEGRAM_BOT_TOKEN_ENV, "").strip() or not (os.getenv(TELEGRAM_CHAT_ID_ENV, "").strip() or os.getenv("TELEGRAM_OWNER_CHAT_ID", "").strip()):
            return {
                "status": "FAILED",
                "message": message,
                "error_message": "TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID 또는 TELEGRAM_OWNER_CHAT_ID가 필요합니다.",
            }

        try:
            result = self.notifier.notify(message)
        except Exception as exc:
            return {"status": "FAILED", "message": message, "error_message": str(exc)}
        return {"status": result.get("status", "NOTIFIED"), "message": message, "error_message": result.get("error_message", "")}
