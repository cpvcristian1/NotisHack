import json
import re

import requests
from bs4 import BeautifulSoup

URL = "https://lablab.ai/ai-hackathons"


class SourceError(Exception):
    pass


def fetch_hackathons() -> list:
    try:
        resp = requests.get(URL, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        # lablab embeds a JSON-LD BreadcrumbList with every hackathon name+url
        soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for tag in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(tag.string or "")
            except (json.JSONDecodeError, TypeError):
                continue
            node = data if isinstance(data, dict) else {}
            if node.get("@type") == "ItemList":
                items = node.get("itemListElement", [])
                break
            for child in node.get("@graph", []):
                if isinstance(child, dict) and child.get("@type") == "ItemList":
                    items = child.get("itemListElement", [])
                    break
        results = []
        for item in items:
            url = item.get("url", "")
            name = item.get("name", "")
            if not url or not name or "/ai-hackathons/" not in url:
                continue
            slug = url.rstrip("/").split("/")[-1]
            if slug == "ai-hackathons" or slug.startswith("page-"):
                continue
            results.append({
                "id": slug,
                "title": name,
                "url": url,
                "deadline": "",
                "prize": "",
                "location": "Online",
                "description": name,
            })
        if not results:
            raise SourceError("lablab.ai returned no hackathon items (JSON-LD missing)")
        # dedupe by slug, first occurrence wins
        seen = {}
        for r in results:
            seen.setdefault(r["id"], r)
        return list(seen.values())
    except requests.RequestException as e:
        raise SourceError(f"lablab.ai request error: {e}")
