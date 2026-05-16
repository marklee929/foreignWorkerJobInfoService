"""Telegram notification orchestration bot."""

from ...social.telegram.notifier import TelegramNotifier


class TelegramNotifyBot:
    def __init__(self, notifier: TelegramNotifier | None = None):
        self.notifier = notifier or TelegramNotifier()
