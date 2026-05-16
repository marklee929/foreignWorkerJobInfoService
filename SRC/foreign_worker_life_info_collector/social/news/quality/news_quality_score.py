"""News quality scoring placeholder."""


def score_news_item(item) -> float:
    return 1.0 if getattr(item, "title", "") and getattr(item, "url", "") else 0.0
