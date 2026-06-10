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
        publish_result: dict | None = None,
    ) -> str:
        if error_message or status in {"FAILED", "FAILED_RETRYABLE", "FAILED_PERMISSION", "AUTO_RETRY_BLOCKED"}:
            return self.build_failure_message(candidate, status, error_message, publish_result or {})

        return "\n".join(
            [
                "News auto publish completed",
                "",
                f"Title: {normalize_plain_text(candidate.title)}",
                f"Category: {normalize_plain_text(candidate.category or '-')}",
                f"Score: {candidate.evaluation_score:.2f}",
                f"Risk: {candidate.risk_level or 'LOW'}",
                "",
                f"Summary:\n{normalize_plain_text(candidate.short_summary or candidate.summary)}",
                "",
                f"Source:\n{candidate.source_url}",
                "",
                f"Facebook Post:\n{facebook_post_url or facebook_post_id}",
            ]
        )

    def build_failure_message(
        self,
        candidate: NewsCandidate,
        status: str,
        error_message: str = "",
        publish_result: dict | None = None,
    ) -> str:
        result = publish_result or {}
        context = result.get("error_context") or {}
        meta_error = context.get("meta_error") or result.get("meta_error") or {}
        token_status = context.get("token_status") or result.get("token_status") or {}
        error_category = result.get("error_category") or context.get("error_category") or "-"
        lines = [
            "Facebook Publish Failed",
            "",
            f"Content ID: {candidate.id or '-'}",
            f"Title: {normalize_plain_text(candidate.title)}",
            f"Internal Status: {status}",
            f"Error Category: {normalize_plain_text(str(error_category))}",
            "",
            "Meta Error:",
        ]
        if meta_error:
            lines.extend(
                [
                    f"- type: {normalize_plain_text(str(meta_error.get('type') or '-'))}",
                    f"- code: {meta_error.get('code') if meta_error.get('code') not in (None, '') else '-'}",
                    f"- subcode: {meta_error.get('error_subcode') if meta_error.get('error_subcode') not in (None, '') else '-'}",
                    f"- message: {normalize_plain_text(str(meta_error.get('message') or '-'))}",
                    f"- fbtrace_id: {normalize_plain_text(str(meta_error.get('fbtrace_id') or '-'))}",
                ]
            )
        else:
            lines.append("- not available")
            lines.extend(["", "Internal Reason:", f"- {normalize_plain_text(error_message or candidate.fail_reason or 'Unknown error')}"])

        lines.extend(
            [
                "",
                "Token Status:",
                f"- type: {normalize_plain_text(str(token_status.get('token_type') or 'UNKNOWN'))}",
                f"- valid: {token_status.get('is_valid', 'unknown')}",
                f"- page match: {token_status.get('page_id_match', 'unknown')}",
                f"- scopes: {token_status.get('required_scopes_present', 'unknown')}",
                f"- expires_at: {token_status.get('expires_at') or '-'}",
                f"- fingerprint: {normalize_plain_text(str(token_status.get('token_fingerprint') or '-'))}",
                "",
                "Link:",
                f"- {normalize_plain_text(str(result.get('facebook_link_url') or context.get('link_url') or candidate.source_url or '-'))}",
                "",
                "Next Action:",
                "- Check Error Category and Meta Error code before changing posting frequency.",
                "- Recheck Page Access Token in Meta Debugger only when token category indicates it.",
            ]
        )
        return "\n".join(lines)

    def notify_failure(self, candidate: NewsCandidate, error_message: str, dry_run: bool = False) -> dict:
        return self.notify_publish_result(candidate, status="FAILED", error_message=error_message, dry_run=dry_run)

    def notify_operational_alert(self, title: str, message: str, dry_run: bool = False) -> dict:
        text = "\n".join([f"Alert: {normalize_plain_text(title)}", "", normalize_plain_text(message)])
        return self._send(text, dry_run=dry_run)

    def notify_cooldown(self, cooldown: dict, dry_run: bool = False) -> dict:
        message = "\n".join(
            [
                "News Publishing Cooldown",
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
                "No Publish Candidate Found",
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
                "No Safe Candidate",
                "",
                f"Window Articles: {selection.get('today_article_count', 0)}",
                f"Window Average Score: {selection.get('today_avg_score', 0)}",
                f"Threshold: {selection.get('threshold_used') or 40}",
            ]
        )
        return self._send(message, dry_run=dry_run)

    def notify_facebook_error(
        self,
        candidate: NewsCandidate,
        reason: str,
        status: str,
        dry_run: bool = False,
        publish_result: dict | None = None,
    ) -> dict:
        message = self.build_failure_message(candidate, status, reason, publish_result or {})
        return self._send(message, dry_run=dry_run)

    def notify_publish_result(
        self,
        candidate: NewsCandidate,
        status: str,
        facebook_post_id: str = "",
        facebook_post_url: str = "",
        error_message: str = "",
        dry_run: bool = False,
        publish_result: dict | None = None,
    ) -> dict:
        message = self.build_message(candidate, status, facebook_post_id, facebook_post_url, error_message, publish_result)
        return self._send(message, dry_run=dry_run)

    def _send(self, message: str, dry_run: bool = False) -> dict:
        if dry_run:
            return {"status": "DRY_RUN", "message": message, "error_message": ""}

        if not os.getenv(TELEGRAM_BOT_TOKEN_ENV, "").strip() or not (os.getenv(TELEGRAM_CHAT_ID_ENV, "").strip() or os.getenv("TELEGRAM_OWNER_CHAT_ID", "").strip()):
            return {
                "status": "FAILED",
                "message": message,
                "error_message": "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID or TELEGRAM_OWNER_CHAT_ID are required.",
            }

        try:
            result = self.notifier.notify(message)
        except Exception as exc:
            return {"status": "FAILED", "message": message, "error_message": str(exc)}
        return {"status": result.get("status", "NOTIFIED"), "message": message, "error_message": result.get("error_message", "")}
