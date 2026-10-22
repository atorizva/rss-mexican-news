from datetime import UTC, datetime

from rss_mexican_news.feed import build_atom
from rss_mexican_news.models import NewsItem


def test_build_atom():
    items = [NewsItem(title="Headline", link="https://example.com/1", source="S")]
    xml = build_atom(items, updated=datetime(2026, 10, 21, 13, 0, tzinfo=UTC))
    text = xml.decode()
    assert text.startswith("<?xml")
    assert "<title>Headline</title>" in text
    assert 'href="https://example.com/1"' in text
    assert "2026-10-21T13:00:00Z" in text
    assert "<name>S</name>" in text


def test_build_atom_empty():
    xml = build_atom([], updated=datetime(2026, 10, 21, 13, 0, tzinfo=UTC))
    assert "<entry>" not in xml.decode()
