# rss-mexican-news

An aggregator that pulls the latest headlines from a set of Mexican news outlets and publishes them as a single merged feed.

## Language

**Source**: A Mexican news outlet we draw headlines from. Each source has a name, a homepage, and one acquisition method.
_Avoid_: Site, feed (when referring to the whole outlet)

**NewsItem**: A single headline pulled from a source: a title, a link, the source it came from, an optional summary, and an optional publication time.
_Avoid_: Article, story, post, entry

**Aggregate feed**: The single merged feed this project publishes, combining the latest items from every source, newest first.
_Avoid_: The feed, output, combined feed

**Feed source**: A source that exposes a machine-readable feed (RSS or Atom) which we consume directly.
_Avoid_: RSS source

**Scrape source**: A source with no usable feed; we read its homepage HTML and extract headlines via CSS selectors instead.
_Avoid_: HTML source, crawler source

**Snapshot**: Each run regenerates the aggregate feed from the current latest items only; no history is kept.
_Avoid_: History, archive
