"""Load source definitions from sources.toml."""

import tomllib
from pathlib import Path

from .feed_source import FeedSource
from .models import NewsSource
from .scrape_source import ScrapeSelectors, ScrapeSource


def load_sources(path: str | Path) -> list[NewsSource]:
    """Read ``sources.toml`` and build one source object per entry."""
    with open(path, "rb") as handle:
        data = tomllib.load(handle)
    sources: list[NewsSource] = []
    for raw in data.get("sources", []):
        name = raw.get("name", "")
        url = raw.get("url", "")
        if not name or not url:
            raise ValueError(f"source entry missing 'name' or 'url': {raw!r}")
        kind = raw.get("type")
        homepage = raw.get("homepage", "")
        if kind == "feed":
            sources.append(FeedSource(name=name, homepage=homepage, url=url))
        elif kind == "scrape":
            selectors = ScrapeSelectors(
                item=raw.get("item", ""),
                title=raw.get("title", ""),
                link=raw.get("link", ""),
                summary=raw.get("summary", ""),
                published=raw.get("published", ""),
            )
            if not selectors.item or not selectors.title:
                raise ValueError(f"scrape source {name!r} needs 'item' and 'title' selectors")
            sources.append(ScrapeSource(name=name, homepage=homepage, url=url, selectors=selectors))
        else:
            raise ValueError(f"unknown source type {kind!r} for {name!r}")
    return sources
