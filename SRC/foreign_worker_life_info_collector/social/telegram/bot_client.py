"""Telegram bot client placeholder.

Network calls are intentionally not implemented in this structural refactor.
"""


class TelegramBotClient:
    def send_message(self, text: str) -> dict:
        raise NotImplementedError("Telegram notifications are not enabled in dry-run structure.")
