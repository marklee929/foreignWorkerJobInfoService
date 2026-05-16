"""News content models for social publishing."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NewsItem:
    title: str
    url: str
    source: str = ""
    summary: str = ""
    content: str = ""
    language: str = "ko"
    category: str = ""


@dataclass
class NewsCandidate:
    title: str
    source_url: str
    source_type: str
    summary: str = ""
    content: str = ""
    language: str = "ko"
    category: str = ""
    hash_key: str = ""
    similarity_key: str = ""
    status: str = "CANDIDATE"
    collected_at: str = ""
    published_at: str | None = None
    duplicate_group_id: int | None = None
    id: int | None = None

    @classmethod
    def from_item(cls, item: NewsItem) -> "NewsCandidate":
        return cls(
            title=item.title,
            source_url=item.url,
            source_type=item.source or "manual",
            summary=item.summary,
            content=item.content,
            language=item.language,
            category=item.category,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "title": self.title,
            "summary": self.summary,
            "language": self.language,
            "category": self.category,
            "hash_key": self.hash_key,
            "similarity_key": self.similarity_key,
            "duplicate_group_id": self.duplicate_group_id,
            "status": self.status,
            "collected_at": self.collected_at,
            "published_at": self.published_at,
        }
