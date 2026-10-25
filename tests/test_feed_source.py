from rss_mexican_news.feed_source import parse_feed

RSS = b"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Test</title>
    <item>
      <title>First</title>
      <link>https://example.com/1</link>
      <description><![CDATA[<p>Hello</p>]]></description>
      <pubDate>Mon, 20 Oct 2026 12:00:00 GMT</pubDate>
    </item>
    <item>
      <title>No link</title>
      <description>x</description>
    </item>
  </channel>
</rss>
"""

ATOM = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>T</title>
  <entry>
    <title>A</title>
    <link href="https://example.com/a"/>
    <updated>2026-10-20T12:00:00Z</updated>
    <summary>sum</summary>
  </entry>
</feed>
"""


def test_parse_rss():
    items = parse_feed(RSS, source="Test")
    assert len(items) == 1
    item = items[0]
    assert item.title == "First"
    assert item.link == "https://example.com/1"
    assert item.source == "Test"
    assert item.summary == "Hello"
    assert item.published_at is not None


def test_parse_atom():
    items = parse_feed(ATOM, source="T")
    assert len(items) == 1
    assert items[0].title == "A"
    assert items[0].link == "https://example.com/a"
    assert items[0].summary == "sum"


def test_parse_feed_double_encoded_cdata():
    # Some feeds (e.g. Excélsior) escape CDATA markers, so feedparser returns
    # the literal "<![CDATA[...]]>" wrapper in the title. Strip it.
    raw = b"""<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item>
        <title>&lt;![CDATA[Headline with special chars &amp; more]]&gt;</title>
        <link>https://example.com/c</link>
      </item>
    </channel></rss>
    """
    items = parse_feed(raw, source="X")
    assert len(items) == 1
    assert items[0].title == "Headline with special chars & more"


def test_parse_feed_double_encoded_description():
    # Excélsior double-encodes the CDATA wrapper on <description>, which makes
    # feedparser drop the summary entirely. Strip the markers so the summary survives.
    raw = b"""<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item>
        <title>Headline</title>
        <link>https://example.com/d</link>
        <description>&lt;![CDATA[The summary text.]]&gt;</description>
      </item>
    </channel></rss>
    """
    items = parse_feed(raw, source="X")
    assert len(items) == 1
    assert items[0].summary == "The summary text."
