import os
import sys
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch

import sources.kaggle as kaggle


class MockResponse:
    def __init__(self, payload=None, error=None):
        self._payload = payload if payload is not None else {"competitions": []}
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


FUTURE = (date.today() + timedelta(days=30)).isoformat()
PAST = (date.today() - timedelta(days=30)).isoformat()


def comp(name, title, brief="", deadline=FUTURE, cats=None):
    return {
        "competitionName": name,
        "title": title,
        "briefDescription": brief,
        "deadline": deadline + "T23:59:00.000Z",
        "categories": [{"name": c} for c in (cats or [])],
    }


SAMPLE = {"competitions": [
    comp("gemma-agent", "Google Gemma 4 Developer Agent",
         brief="autonomous coding agents", cats=["artificial intelligence"]),
    comp("football-2027", "NFL Data Bowl", deadline=FUTURE, cats=["sports"]),
    comp("old-comp", "Old AI Comp", brief="machine learning", deadline=PAST),
]}


def _mock_post(payload):
    def fake_post(url, **kw):
        return MockResponse(payload)
    return fake_post


def test_fetch_maps_ai_future_comps(monkeypatch):
    monkeypatch.setattr(kaggle.requests, 'post', _mock_post(SAMPLE))
    result = kaggle.fetch_hackathons()
    assert len(result) == 1
    h = result[0]
    assert h["id"] == "gemma-agent"
    assert h["url"] == "https://www.kaggle.com/competitions/gemma-agent"
    assert h["location"] == "Online"
    assert h["deadline"] == FUTURE


def test_fetch_skips_past_deadlines(monkeypatch):
    monkeypatch.setattr(kaggle.requests, 'post', _mock_post(SAMPLE))
    result = kaggle.fetch_hackathons()
    assert all(h["id"] != "old-comp" for h in result)


def test_fetch_skips_non_ai(monkeypatch):
    monkeypatch.setattr(kaggle.requests, 'post', _mock_post(SAMPLE))
    result = kaggle.fetch_hackathons()
    assert all(h["id"] != "football-2027" for h in result)


def test_ai_keyword_in_category_counts(monkeypatch):
    payload = {"competitions": [comp("ml-cat", "Some Title", cats=["machine learning"])]}
    monkeypatch.setattr(kaggle.requests, 'post', _mock_post(payload))
    result = kaggle.fetch_hackathons()
    assert len(result) == 1


def test_http_error_raises_sourceerror(monkeypatch):
    monkeypatch.setattr(kaggle.requests, 'post',
                        lambda *a, **k: MockResponse(error=kaggle.requests.HTTPError("500")))
    try:
        kaggle.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except kaggle.SourceError:
        pass


def test_timeout_raises_sourceerror(monkeypatch):
    monkeypatch.setattr(kaggle.requests, 'post',
                        lambda *a, **k: MockResponse(error=kaggle.requests.Timeout("t")))
    try:
        kaggle.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except kaggle.SourceError:
        pass
