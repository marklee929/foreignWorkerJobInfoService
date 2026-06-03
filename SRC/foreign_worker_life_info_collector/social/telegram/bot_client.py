"""Telegram bot client."""

from __future__ import annotations

import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

TELEGRAM_BOT_TOKEN_ENV = "TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID_ENV = "TELEGRAM_CHAT_ID"


class TelegramBotClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout

    def send_message(self, text: str) -> dict:
        token = os.getenv(TELEGRAM_BOT_TOKEN_ENV, "").strip()
        chat_id = os.getenv(TELEGRAM_CHAT_ID_ENV, "").strip() or os.getenv("TELEGRAM_OWNER_CHAT_ID", "").strip()
        if not token or not chat_id:
            return {
                "status": "FAILED",
                "error_message": "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required for real notification.",
            }

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        body = urlencode({"chat_id": chat_id, "text": text}).encode("utf-8")
        request = Request(url, data=body, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                json.loads(response.read().decode("utf-8", errors="replace"))
        except Exception as exc:
            return {"status": "FAILED", "error_message": str(exc)}
        return {"status": "NOTIFIED", "error_message": ""}
