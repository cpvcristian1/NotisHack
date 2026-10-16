import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_run_end_to_end(monkeypatch):
    import main
    monkeypatch.setattr('sources.devpost.fetch_hackathons', lambda: [
        {"id": "1", "title": "AI Hack", "url": "http://x", "deadline": "Oct 31", "prize": "$5000", "location": "Online", "description": "AI tools allowed"}
    ])
    monkeypatch.setattr('sources.brabble.fetch_hackathons', lambda: [])
    monkeypatch.setattr('sources.lablab.fetch_hackathons', lambda: [])
    notified = []
    monkeypatch.setattr('storage.is_notified', lambda x: x in notified)
    monkeypatch.setattr('storage.mark_notified', lambda x: notified.append(x))
    sent = []
    monkeypatch.setattr('notify.send_summary', lambda h: sent.append(h) or True)
    main.run()
    assert len(sent) == 1
    assert sent[0][0]["title"] == "AI Hack"
    assert "1" in notified

def test_run_skips_already_notified(monkeypatch):
    import main
    monkeypatch.setattr('sources.devpost.fetch_hackathons', lambda: [
        {"id": "1", "title": "AI Hack", "url": "http://x", "deadline": "Oct 31", "prize": "$5000", "location": "Online", "description": "AI tools allowed"}
    ])
    monkeypatch.setattr('sources.brabble.fetch_hackathons', lambda: [])
    monkeypatch.setattr('sources.lablab.fetch_hackathons', lambda: [])
    monkeypatch.setattr('storage.is_notified', lambda x: True)
    sent = []
    monkeypatch.setattr('notify.send_summary', lambda h: sent.append(h) or True)
    main.run()
    assert len(sent) == 0

def test_run_continues_on_source_error(monkeypatch):
    import main
    def raise_error():
        raise Exception("API down")
    monkeypatch.setattr('sources.devpost.fetch_hackathons', raise_error)
    monkeypatch.setattr('config.BRABBLE_API_KEY', 'test-key')  # brabble skipped when key unset
    monkeypatch.setattr('sources.brabble.fetch_hackathons', lambda: [
        {"id": "2", "title": "AI Hack 2", "url": "http://y", "deadline": "Nov 1", "prize": "", "location": "Vigo", "description": "AI agents"}
    ])
    monkeypatch.setattr('sources.lablab.fetch_hackathons', lambda: [])
    monkeypatch.setattr('storage.is_notified', lambda x: False)
    sent = []
    monkeypatch.setattr('notify.send_summary', lambda h: sent.append(h) or True)
    main.run()
    assert len(sent) == 1

def test_run_does_not_mark_notified_when_send_fails(monkeypatch):
    import main
    monkeypatch.setattr('sources.devpost.fetch_hackathons', lambda: [
        {"id": "1", "title": "AI Hack", "url": "http://x", "deadline": "Oct 31", "prize": "$5000", "location": "Online", "description": "AI tools allowed"}
    ])
    monkeypatch.setattr('sources.brabble.fetch_hackathons', lambda: [])
    monkeypatch.setattr('sources.lablab.fetch_hackathons', lambda: [])
    notified = []
    monkeypatch.setattr('storage.is_notified', lambda x: x in notified)
    monkeypatch.setattr('storage.mark_notified', lambda x: notified.append(x))
    sent = []
    monkeypatch.setattr('notify.send_summary', lambda h: sent.append(h) or False)
    main.run()
    assert len(sent) == 1
    assert notified == []
