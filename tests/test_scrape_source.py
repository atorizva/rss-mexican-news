from rss_mexican_news.scrape_source import ScrapeSelectors, parse_html

HTML = b"""
<html><body>
<article class="news">
  <h2><a href="/story/1">Story One</a></h2>
  <p>Summary one</p>
  <time datetime="2026-10-20T07:00:00-06:00">20 oct</time>
</article>
<article class="news">
  <h2><a href="/story/2">Story Two</a></h2>
</article>
</body></html>
"""

SELECTORS = ScrapeSelectors(
    item="article.news",
    title="h2",
    link="h2 a",
    summary="p",
    published="time",
)


def test_parse_html():
    items = parse_html(
        HTML,
        source="T",
        homepage="https://example.com",
        selectors=SELECTORS,
    )
    assert [i.title for i in items] == ["Story One", "Story Two"]
    assert items[0].link == "https://example.com/story/1"
    assert items[0].summary == "Summary one"
    assert items[0].published_at is not None
    # The second item has no summary or date; both fall back cleanly.
    assert items[1].summary == ""
    assert items[1].published_at is None
