from datetime import date

import requests

API_URL = "https://www.kaggle.com/api/i/competitions.CompetitionService/ListCompetitions"

AI_KEYWORDS = (
    "ai", "agent", "machine learning", "ml", "deep learning",
    "neural", "llm", "gemma", "language", "vision", "nlp",
)


class SourceError(Exception):
    pass


def _is_ai(c: dict) -> bool:
    text = " ".join([
        c.get("title", ""),
        c.get("briefDescription", ""),
        " ".join(cat.get("name", "") for cat in c.get("categories", [])),
    ]).lower()
    return any(k in text for k in AI_KEYWORDS)


def fetch_hackathons() -> list:
    try:
        resp = requests.post(
            API_URL,
            json={
                "competitionFilter": {
                    "organizationHostSegment": "GENERAL",
                    "sort": "RECENTLY_CREATED",
                    "activeOnly": True,
                },
                "pageSize": 200,
            },
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
        comps = resp.json().get("competitions", [])
        now = date.today().isoformat()
        return [{
            "id": c["competitionName"],
            "title": c["title"],
            "url": f"https://www.kaggle.com/competitions/{c['competitionName']}",
            "deadline": c.get("deadline", "")[:10],
            "prize": "",
            "location": "Online",
            "description": c.get("briefDescription", ""),
        } for c in comps
            if c.get("deadline", "")[:10] > now and _is_ai(c)]
    except (requests.RequestException, KeyError, ValueError, TypeError) as e:
        raise SourceError(f"Kaggle API error: {e}")
