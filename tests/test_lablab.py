import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MockResponse:
    """Stands in for a requests.Response; text holds the HTML body."""

    def __init__(self, text="", error=None):
        self._text = text
        self.error = error

    def raise_for_status(self):
        if self.error is not None:
            raise self.error

    @property
    def text(self):
        return self._text


LD_JSON = (
    '<html><head>'
    '<script type="application/ld+json">'
    '{"@type": "ItemList", "itemListElement": ['
    '{"@type": "ListItem", "position": 1, "name": "AI Hack", '
    '"url": "https://lablab.ai/ai-hackathons/ai-hack"},'
    '{"@type": "ListItem", "position": 2, "name": "Second One", '
    '"url": "https://lablab.ai/ai-hackathons/second-one"},'
    '{"@type": "ListItem", "position": 3, "name": "Bad Path", '
    '"url": "https://lablab.ai/pricing"}'
    ']}</script>'
    '</head><body></body></html>'
)

NO_LD_HTML = "<html><body><div class='hackathon'><h2>AI Hack</h2></div></body></html>"


def test_fetch_hackathons_parses_jsonld(monkeypatch):
    import sources.lablab as lablab
    monkeypatch.setattr(lablab.requests, 'get', lambda *a, **k: MockResponse(LD_JSON))
    result = lablab.fetch_hackathons()
    assert len(result) == 2
    assert result[0]["id"] == "ai-hack"
    assert result[0]["title"] == "AI Hack"
    assert result[0]["url"] == "https://lablab.ai/ai-hackathons/ai-hack"
    assert result[0]["location"] == "Online"
    assert "AI Hack" in result[0]["description"]


def test_fetch_hackathons_skips_non_hackathon_urls(monkeypatch):
    import sources.lablab as lablab
    monkeypatch.setattr(lablab.requests, 'get', lambda *a, **k: MockResponse(LD_JSON))
    result = lablab.fetch_hackathons()
    ids = [r["id"] for r in result]
    assert "pricing" not in ids


def test_fetch_hackathons_empty_raises(monkeypatch):
    import sources.lablab as lablab
    monkeypatch.setattr(lablab.requests, 'get', lambda *a, **k: MockResponse(NO_LD_HTML))
    try:
        lablab.fetch_hackathons()
        assert False, "Should have raised SourceError for empty content"
    except lablab.SourceError:
        pass


def test_fetch_hackathons_http_error_raises(monkeypatch):
    import sources.lablab as lablab
    monkeypatch.setattr(lablab.requests, 'get',
                        lambda *a, **k: MockResponse("", error=lablab.requests.HTTPError("503")))
    try:
        lablab.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except lablab.SourceError:
        pass


def test_fetch_hackathons_dedupes_by_slug(monkeypatch):
    import sources.lablab as lablab
    dup = LD_JSON.replace('"position": 2, "name": "Second One", "url": "https://lablab.ai/ai-hackathons/second-one"',
                           '"position": 2, "name": "AI Hack", "url": "https://lablab.ai/ai-hackathons/ai-hack"')
    monkeypatch.setattr(lablab.requests, 'get', lambda *a, **k: MockResponse(dup))
    result = lablab.fetch_hackathons()
    assert len(result) == 1


def test_fetch_hackathons_handles_broken_jsonld(monkeypatch):
    import sources.lablab as lablab
    html = '<html><head><script type="application/ld+json">{broken</script></head><body>x</body></html>'
    monkeypatch.setattr(lablab.requests, 'get', lambda *a, **k: MockResponse(html))
    try:
        lablab.fetch_hackathons()
        assert False, "Should have raised SourceError"
    except lablab.SourceError:
        pass
