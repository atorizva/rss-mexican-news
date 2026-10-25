# rss-mexican-news

An RSS aggregator that pulls the latest headlines from Mexican news outlets and
publishes them as a single merged Atom feed.

## Usage

```sh
uv sync
uv run rss-mexican-news   # builds feed.xml from sources.toml
```

Add sources to `sources.toml` (see the file for the `feed`/`scrape` format), then
run the command again. The feed updates daily at 00:00 Mexico City via GitHub
Actions (`.github/workflows/update-feed.yml`) and is served at
`https://atorizva.github.io/rss-mexican-news/feed.xml`.

## Develop

```sh
uv run ruff check
uv run pyrefly check
uv run pytest
```
