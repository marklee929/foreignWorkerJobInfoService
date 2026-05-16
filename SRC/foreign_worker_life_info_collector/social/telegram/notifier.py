"""Telegram notification orchestration."""

from .bot_client import TelegramBotClient


class TelegramNotifier:
    def __init__(self, client: TelegramBotClient | None = None):
        self.client = client or TelegramBotClient()

    def notify(self, text: str) -> dict:
        return self.client.send_message(text)
