"""Facebook publishing orchestration bot."""

from ...social.facebook.page_client import FacebookPageClient


class FacebookPublishBot:
    def __init__(self, client: FacebookPageClient | None = None):
        self.client = client or FacebookPageClient()
