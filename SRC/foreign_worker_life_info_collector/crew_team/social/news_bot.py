"""Social news orchestration bot."""

from ...social.news.pipeline import NewsPipeline


class NewsBot:
    def __init__(self, pipeline: NewsPipeline | None = None):
        self.pipeline = pipeline or NewsPipeline()

    def run(self) -> list:
        return self.pipeline.run()
