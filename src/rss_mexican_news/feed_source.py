"""Feed-based sources, parsed with feedparser."""

import calendar
import time
from dataclasses import dataclass
from datetime import UTC, datetime

import feedparser
from bs4 import BeautifulSoup

from .http import fetch
from .models import NewsItem


def parse_feed(raw: bytes, *, source: str) -> list[NewsItem]:
    """Parse an RSS or Atom document into news items."""
    parsed = feedparser.parse(raw)
    items: list[NewsItem] = []
    for entry in parsed.entries:
        title = (entry.get("title") or "").strip()
        link = entry.get("link") or ""
        if not title or not link:
            continue
        summary = entry.get("summary") or entry.get("description") or ""
        items.append(
            NewsItem(
                title=title,
                link=link,
                source=source,
                summary=_plain_text(summary),
                published_at=_parsed_time(
                    entry.get("published_parsed") or entry.get("updated_parsed")
                ),
            )
        )
    return items


@dataclass(frozen=True, slots=True)
class FeedSource:
    """A source backed by an RSS or Atom feed."""

    name: str
    homepage: str
    url: str

    def fetch(self) -> list[NewsItem]:
        return parse_feed(fetch(self.url), source=self.name)


def _plain_text(html: str) -> str:
    return BeautifulSoup(html, "html.parser").get_text(" ", strip=True)


def _parsed_time(value: time.struct_time | None) -> datetime | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(calendar.timegm(value), tz=UTC)
    except OverflowError, ValueError:
        return None
