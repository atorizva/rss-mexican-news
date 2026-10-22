"""HTTP fetching with a friendly user-agent."""

import urllib.request

USER_AGENT = "rss-mexican-news/0.1 (+https://github.com/atorizva/rss-mexican-news)"


def fetch(url: str, *, timeout: float = 30.0) -> bytes:
    """Return the raw bytes of ``url``, raising on HTTP errors."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()
