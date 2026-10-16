import os
import sys

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SAMPLE_LISTING = {
    "id": "b1", "title": "AI Challenge", "url": "http://y",
    "deadline": "2026-12-01", "prize": "$1000",
    "location": "Remote", "description": "AI agents",
}


class MockResponse:
    """Records the kwargs the source sent; raises if error is set."""

    def __init__(self, listings, error=None):
        self._listings = listings
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    def json(self):
        return {"listings": self._listings}


def test_fetch_hackathons_returns_list(monkeypatch):
    import sources.brabble as brabble
    monkeypatch.setattr(brabble.config, "BRABBLE_API_KEY", "")
    monkeypatch.setattr(brabble.requests, 'get',
                        lambda *a, **k: MockResponse([SAMPLE_LISTING]))
    result = brabble.fetch_hackathons()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "b1"


def test_fetch_hackathons_api_error_raises(monkeypatch):
    import sources.brabble as brabble
    monkeypatch.setattr(brabble.config, "BRABBLE_API_KEY", "")
    monkeypatch.setattr(brabble.requests, 'get',
                        lambda *a, **k: MockResponse([], error=requests.HTTPError("404")))
    try:
        brabble.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except brabble.SourceError:
        pass


def test_fetch_hackathons_sends_api_key(monkeypatch):
    import sources.brabble as brabble
    monkeypatch.setattr(brabble.config, "BRABBLE_API_KEY", "test_key_abc")
    sent = {}

    def fake_get(url, **kwargs):
        sent["url"] = url
        sent["headers"] = kwargs.get("headers")
        return MockResponse([SAMPLE_LISTING])

    monkeypatch.setattr(brabble.requests, 'get', fake_get)
    result = brabble.fetch_hackathons()
    assert result[0]["id"] == "b1"
    assert sent["headers"] == {"Authorization": "Bearer test_key_abc"}


def test_fetch_hackathons_no_key_sends_no_auth_header(monkeypatch):
    import sources.brabble as brabble
    monkeypatch.setattr(brabble.config, "BRABBLE_API_KEY", "")
    sent = {}

    def fake_get(url, **kwargs):
        sent["headers"] = kwargs.get("headers")
        return MockResponse([SAMPLE_LISTING])

    monkeypatch.setattr(brabble.requests, 'get', fake_get)
    brabble.fetch_hackathons()
    assert "Authorization" not in (sent["headers"] or {})
