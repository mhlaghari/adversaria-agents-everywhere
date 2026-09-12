"""Explicit Exa searches, with source text and URLs carried into the artifact."""

from .config import CliError
from .transport import request


def search(config, query, count=5):
    key = config.key("exa")
    if not key:
        raise CliError("Exa needs a key: adversaria auth exa (or EXA_API_KEY).")
    data = request(
        "POST",
        "https://api.exa.ai/search",
        headers={"x-api-key": key},
        timeout=45,
        json={
            "query": query,
            "type": "auto",
            "numResults": count,
            "contents": {"text": {"maxCharacters": 4000}},
        },
    )
    return [
        {
            "title": r.get("title") or r.get("url", "Untitled"),
            "url": r.get("url", ""),
            "text": (r.get("text") or "\n".join(r.get("highlights") or []))[:4000],
            "published": r.get("publishedDate", ""),
        }
        for r in data.get("results", [])
    ]


def source_context(results):
    return "\n\n".join(
        f"[{i}] {r['title']}\n{r['url']}\n{r['text']}" for i, r in enumerate(results, 1)
    )
