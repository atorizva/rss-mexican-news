"""Core domain types: the news item and the source protocol."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class NewsItem:
    """A single headline pulled from a source."""

    title: str
    link: str
    source: str
    summary: str = ""
    published_at: datetime | None = None


class NewsSource(Protocol):
    """Anything that can produce the latest news items for one source."""

    name: str

    def fetch(self) -> list[NewsItem]: ...
