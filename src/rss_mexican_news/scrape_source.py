"""HTML-scraping sources, parsed with BeautifulSoup."""

from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .http import fetch
from .models import NewsItem


@dataclass(frozen=True, slots=True)
class ScrapeSelectors:
    """CSS selectors for extracting news items from a homepage."""

    item: str
    title: str
    link: str = ""
    summary: str = ""
    published: str = ""


def parse_html(
    raw: bytes,
    *,
    source: str,
    homepage: str,
    selectors: ScrapeSelectors,
) -> list[NewsItem]:
    """Extract news items from a homepage using ``selectors``."""
    soup = BeautifulSoup(raw, "html.parser")
    items: list[NewsItem] = []
    for node in soup.select(selectors.item):
        title_el = node.select_one(selectors.title)
        if title_el is None:
            continue
        title = title_el.get_text(" ", strip=True)
        link = _link(node, selectors.link, title_el, homepage)
        if not title or not link:
            continue
        summary = ""
        if selectors.summary:
            summary_el = node.select_one(selectors.summary)
            if summary_el is not None:
                summary = summary_el.get_text(" ", strip=True)
        published = None
        if selectors.published:
            published_el = node.select_one(selectors.published)
            if published_el is not None:
                published = _parse_datetime(published_el)
        items.append(
            NewsItem(
                title=title,
                link=link,
                source=source,
                summary=summary,
                published_at=published,
            )
        )
    return items


@dataclass(frozen=True, slots=True)
class ScrapeSource:
    """A source with no feed; headlines are scraped from its homepage."""

    name: str
    homepage: str
    url: str
    selectors: ScrapeSelectors

    def fetch(self) -> list[NewsItem]:
        return parse_html(
            fetch(self.url),
            source=self.name,
            homepage=self.homepage,
            selectors=self.selectors,
        )


def _link(node: Tag, link_selector: str, fallback: Tag, homepage: str) -> str:
    target = node.select_one(link_selector) if link_selector else fallback
    if target is None:
        target = fallback
    href = _attr(target, "href")
    if not href:
        anchor = target.find("a")
        href = _attr(anchor, "href") if anchor is not None else ""
    return urljoin(homepage, href) if href else ""


def _attr(el: Tag, key: str) -> str:
    value = el.get(key)
    return value if isinstance(value, str) else ""


def _parse_datetime(el: Tag) -> datetime | None:
    raw = _attr(el, "datetime") or el.get_text(" ", strip=True)
    if not raw:
        return None
    text = raw.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        # shortcut: only ISO-8601 timestamps are parsed; other formats yield no date
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
