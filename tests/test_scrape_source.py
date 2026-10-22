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


def test_parse_html_item_is_anchor():
    # Some sites (e.g. Proceso) wrap the whole card in an <a> instead of linking the title.
    html = b"""
    <html><body>
    <a href="/nacional/2026/10/21/ejemplo.html" class="news-article"
       data-date="2026-10-22T01:59:38.801Z">
      <h3 class="news-article__title">Ejemplo</h3>
    </a>
    </body></html>
    """
    selectors = ScrapeSelectors(item="a.news-article", title=".news-article__title")
    items = parse_html(html, source="P", homepage="https://www.proceso.com.mx", selectors=selectors)
    assert [i.title for i in items] == ["Ejemplo"]
    assert items[0].link == "https://www.proceso.com.mx/nacional/2026/10/21/ejemplo.html"
    assert items[0].published_at is not None


def test_parse_html_spanish_date():
    # Some sites (e.g. Animal Político) print "20 de octubre de 2026" as plain text.
    html = b"""
    <html><body>
    <ul id="ssr-list">
      <li>
        <a href="https://grupoanimal.mx/noticias/ejemplo">Ejemplo</a>
        <span>Animal Politico - 20 de octubre de 2026</span>
      </li>
    </ul>
    </body></html>
    """
    selectors = ScrapeSelectors(item="#ssr-list li", title="a", published="span")
    items = parse_html(html, source="AP", homepage="https://grupoanimal.mx", selectors=selectors)
    assert [i.title for i in items] == ["Ejemplo"]
    assert items[0].published_at is not None
    assert items[0].published_at.year == 2026
    assert items[0].published_at.month == 10
    assert items[0].published_at.day == 20
