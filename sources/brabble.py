import config
import requests

API_URL = "https://brabble.ai/api/listings"


class SourceError(Exception):
    pass


def fetch_hackathons() -> list:
    try:
        headers = {"Authorization": f"Bearer {config.BRABBLE_API_KEY}"} if config.BRABBLE_API_KEY else {}
        resp = requests.get(API_URL, params={"hub": "hackathons"}, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        listings = data.get("listings", [])
        return [{
            "id": str(h["id"]),
            "title": h["title"],
            "url": h["url"],
            "deadline": h.get("deadline", ""),
            "prize": h.get("prize", ""),
            "location": h.get("location", ""),
            "description": h.get("description", "")
        } for h in listings]
    except (requests.RequestException, KeyError, ValueError) as e:
        raise SourceError(f"brabble API error: {e}")
