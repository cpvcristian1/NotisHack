import requests

API_URL = "https://devpost.com/api/hackathons"


class SourceError(Exception):
    pass


def _fetch_page(status: str, page: int) -> list:
    resp = requests.get(
        API_URL,
        params={"search": "AI", "status": status, "page": page},
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    return resp.json().get("hackathons", [])


def fetch_hackathons() -> list:
    try:
        seen = {}
        for status in ("open", "upcoming"):
            page = 1
            while True:
                batch = _fetch_page(status, page)
                if not batch:
                    break
                for h in batch:
                    seen[str(h["id"])] = h
                page += 1
                if page > 10:  # ponytail: cap pagination, 90 items per status is plenty
                    break
        return [{
            "id": str(h["id"]),
            "title": h["title"],
            "url": h["url"],
            "deadline": h.get("submission_period_dates", ""),
            "prize": h.get("prize_amount", ""),
            "location": (h.get("displayed_location") or {}).get("location", ""),
            "description": " ".join(
                t["name"] for t in h.get("themes", []) if isinstance(t, dict)
            ),
        } for h in seen.values()]
    except (requests.RequestException, KeyError, ValueError, TypeError) as e:
        raise SourceError(f"Devpost API error: {e}")
