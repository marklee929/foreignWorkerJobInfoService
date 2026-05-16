"""Publishing log model helpers."""

from dataclasses import dataclass


@dataclass
class PublishLog:
    channel: str
    content_id: str
    status: str
