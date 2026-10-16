import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_format_message_empty():
    import notify
    msg = notify.format_message([])
    assert "0 encontrados" in msg or "sin novedades" in msg.lower()

def test_format_message_with_items():
    import notify
    hackathons = [
        {"title": "AI Hack 1", "url": "http://x", "deadline": "Oct 31", "prize": "$5000", "location": "Online"},
        {"title": "AI Hack 2", "url": "http://y", "deadline": "Nov 15", "prize": "", "location": "Vigo"}
    ]
    msg = notify.format_message(hackathons)
    assert "AI Hack 1" in msg
    assert "AI Hack 2" in msg
    assert "http://x" in msg
    assert "Oct 31" in msg

def test_send_summary_success(monkeypatch):
    import notify
    called = {}
    def mock_post(url, json=None, timeout=None):
        called['url'] = url
        called['json'] = json
        class R:
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr(notify.requests, 'post', mock_post)
    monkeypatch.setattr('config.TELEGRAM_BOT_TOKEN', 'test_token')
    monkeypatch.setattr('config.TELEGRAM_CHAT_ID', 'test_chat')
    result = notify.send_summary([{"title": "Test", "url": "http://x", "deadline": "", "prize": "", "location": "Online"}])
    assert result is True
    assert 'test_token' in called['url']
    assert called['json']['chat_id'] == 'test_chat'

def test_send_summary_api_error(monkeypatch):
    import notify
    def mock_post(url, json=None, timeout=None):
        raise notify.requests.HTTPError("429")
    monkeypatch.setattr(notify.requests, 'post', mock_post)
    monkeypatch.setattr('config.TELEGRAM_BOT_TOKEN', 'test_token')
    monkeypatch.setattr('config.TELEGRAM_CHAT_ID', 'test_chat')
    result = notify.send_summary([{"title": "Test", "url": "http://x", "deadline": "", "prize": "", "location": "Online"}])
    assert result is False

def test_chunk_splits_long_text():
    import notify
    text = "\n".join(f"line {i} " + "x" * 50 for i in range(200))  # ~11k chars
    chunks = notify._chunk(text, limit=4000)
    assert len(chunks) >= 3
    assert all(len(c) <= 4000 for c in chunks)
    assert "\n".join(chunks) == text

def test_chunk_short_text_single_piece():
    import notify
    assert notify._chunk("short") == ["short"]

def test_send_summary_many_hackathons_splits(monkeypatch):
    import notify
    calls = []
    def mock_post(url, json=None, timeout=None):
        calls.append(json['text'])
        class R:
            def raise_for_status(self): pass
        return R()
    monkeypatch.setattr(notify.requests, 'post', mock_post)
    monkeypatch.setattr('config.TELEGRAM_BOT_TOKEN', 'test_token')
    monkeypatch.setattr('config.TELEGRAM_CHAT_ID', 'test_chat')
    hs = [
        {"title": f"Hackathon {i}", "url": f"http://x/{i}", "deadline": "Oct 31",
         "prize": "$5000", "location": "Online"}
        for i in range(150)
    ]
    assert notify.send_summary(hs) is True
    assert len(calls) > 1
    assert all(len(c) <= 4000 for c in calls)
