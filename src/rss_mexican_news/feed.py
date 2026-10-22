"""Build the aggregate Atom feed."""

import xml.etree.ElementTree as ET
from datetime import UTC, datetime

from .models import NewsItem

ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", ATOM_NS)

FEED_TITLE = "Mexican News"
FEED_ID = "tag:atorizva.github.io,2026:rss-mexican-news"
FEED_URL = "https://atorizva.github.io/rss-mexican-news/feed.xml"


def build_atom(items: list[NewsItem], *, updated: datetime | None = None) -> bytes:
    """Render the merged feed as an Atom XML document."""
    updated = updated or datetime.now(UTC)
    feed = ET.Element(_q("feed"))
    _text(feed, "title", FEED_TITLE)
    _text(feed, "id", FEED_ID)
    _text(feed, "updated", _iso(updated))
    ET.SubElement(feed, _q("link"), {"href": FEED_URL, "rel": "self"})
    for item in items:
        entry = ET.SubElement(feed, _q("entry"))
        _text(entry, "title", item.title)
        ET.SubElement(entry, _q("link"), {"href": item.link})
        _text(entry, "id", item.link)
        _text(entry, "updated", _iso(item.published_at or updated))
        if item.summary:
            _text(entry, "summary", item.summary)
        author = ET.SubElement(entry, _q("author"))
        _text(author, "name", item.source)
    ET.indent(feed, space="  ")
    return ET.tostring(feed, encoding="utf-8", xml_declaration=True)


def _q(tag: str) -> str:
    return f"{{{ATOM_NS}}}{tag}"


def _text(parent: ET.Element, tag: str, value: str) -> None:
    ET.SubElement(parent, _q(tag)).text = value


def _iso(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
