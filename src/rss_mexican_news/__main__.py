"""Command-line entrypoint: fetch, merge, and write the aggregate feed."""

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

from .config import load_sources
from .feed import build_atom
from .models import NewsItem


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the Mexican news aggregate feed.")
    parser.add_argument("--config", default="sources.toml")
    parser.add_argument("--output", default="feed.xml")
    parser.add_argument("--max-per-source", type=int, default=10)
    args = parser.parse_args(argv)

    sources = load_sources(args.config)
    items: list[NewsItem] = []
    for source in sources:
        try:
            items.extend(source.fetch()[: args.max_per_source])
        except Exception as exc:
            # A failing source must not sink the whole feed; log and continue.
            print(f"warning: {source.name}: {exc}", file=sys.stderr)

    items.sort(key=_sort_key, reverse=True)
    Path(args.output).write_bytes(build_atom(items))
    print(f"wrote {len(items)} items to {args.output}")
    return 0


def _sort_key(item: NewsItem) -> datetime:
    return item.published_at or datetime.min.replace(tzinfo=UTC)


if __name__ == "__main__":
    raise SystemExit(main())
