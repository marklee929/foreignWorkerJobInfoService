"""News content models for social publishing."""

from dataclasses import dataclass


@dataclass
class NewsItem:
    title: str
    url: str
    source: str = ""
