import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockResponse:
    def __init__(self, payload=None, error=None):
        self._payload = payload if payload is not None else {"hackathons": []}
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


SAMPLE = {
    "hackathons": [{
        "id": 1,
        "title": "AI Hack",
        "url": "http://x",
        "displayed_location": {"location": "Online"},
        "submission_period_dates": "Oct 1-31",
        "prize_amount": "$5000",
        "themes": [{"name": "AI"}],
        "open_state": "open",
    }],
    "meta": {"total_count": 1},
}


def test_fetch_hackathons_returns_list(monkeypatch):
    import sources.devpost as devpost
    monkeypatch.setattr(devpost.requests, 'get', lambda *a, **k: MockResponse(SAMPLE))
    result = devpost.fetch_hackathons()
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == "1"
    assert result[0]["title"] == "AI Hack"
    assert result[0]["location"] == "Online"
    assert result[0]["description"] == "AI"


def test_fetch_hackathons_merges_open_and_upcoming(monkeypatch):
    import sources.devpost as devpost

    def fake_get(url, params=None, **kw):
        status = (params or {}).get("status")
        if status == "open":
            payload = {"hackathons": [{"id": 1, "title": "Open One", "url": "u1",
                                       "displayed_location": {"location": "Online"},
                                       "themes": []}], "meta": {}}
        else:
            payload = {"hackathons": [{"id": 2, "title": "Upcoming One", "url": "u2",
                                       "displayed_location": {"location": "Vigo"},
                                       "themes": []}], "meta": {}}
        return MockResponse(payload)

    monkeypatch.setattr(devpost.requests, 'get', fake_get)
    result = devpost.fetch_hackathons()
    assert len(result) == 2
    assert {r["id"] for r in result} == {"1", "2"}


def test_fetch_hackathons_dedupes_by_id(monkeypatch):
    import sources.devpost as devpost
    # same hackathon returned for both statuses -> one entry
    monkeypatch.setattr(devpost.requests, 'get', lambda *a, **k: MockResponse(SAMPLE))
    result = devpost.fetch_hackathons()
    assert len(result) == 1


def test_fetch_hackathons_stops_on_empty_page(monkeypatch):
    import sources.devpost as devpost
    calls = []

    def fake_get(url, params=None, **kw):
        calls.append((params or {}).get("page", 1))
        # page 1 has data, page 2 empty -> must stop, not loop forever
        if (params or {}).get("page", 1) == 1:
            return MockResponse(SAMPLE)
        return MockResponse({"hackathons": [], "meta": {}})

    monkeypatch.setattr(devpost.requests, 'get', fake_get)
    devpost.fetch_hackathons()
    assert max(calls) == 2


def test_fetch_hackathons_api_error_raises(monkeypatch):
    import sources.devpost as devpost
    monkeypatch.setattr(devpost.requests, 'get',
                        lambda *a, **k: MockResponse(error=devpost.requests.HTTPError("500")))
    try:
        devpost.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except devpost.SourceError:
        pass


def test_fetch_hackathons_bad_json_raises(monkeypatch):
    import sources.devpost as devpost
    monkeypatch.setattr(devpost.requests, 'get',
                        lambda *a, **k: MockResponse(error=devpost.requests.Timeout("t")))
    try:
        devpost.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except devpost.SourceError:
        pass
