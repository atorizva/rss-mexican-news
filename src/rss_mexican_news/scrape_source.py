"""HTML-scraping sources, parsed with BeautifulSoup."""

import re
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
        published_el = node.select_one(selectors.published) if selectors.published else node
        published = _parse_datetime(published_el) if published_el is not None else None
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
    if not href:
        href = _attr(node, "href")  # the card itself may be the anchor (e.g. Proceso)
    return urljoin(homepage, href) if href else ""


def _attr(el: Tag, key: str) -> str:
    value = el.get(key)
    return value if isinstance(value, str) else ""


def _parse_datetime(el: Tag) -> datetime | None:
    raw = _attr(el, "datetime") or _attr(el, "data-date") or el.get_text(" ", strip=True)
    if not raw:
        return None
    text = raw.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        # shortcut: ISO-8601 and Spanish "D de <mes> de AAAA"; other formats yield no date
        return _parse_spanish_date(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


_SPANISH_MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}
_SPANISH_DATE = re.compile(
    r"(\d{1,2})\s+de\s+(" + "|".join(_SPANISH_MONTHS) + r")\s+de\s+(\d{4})",
    re.IGNORECASE,
)


def _parse_spanish_date(text: str) -> datetime | None:
    """Parse a date like ``20 de octubre de 2026`` found anywhere in ``text``."""
    match = _SPANISH_DATE.search(text)
    if match is None:
        return None
    try:
        return datetime(
            int(match.group(3)),
            _SPANISH_MONTHS[match.group(2).lower()],
            int(match.group(1)),
            tzinfo=UTC,
        )
    except ValueError:
        return None
