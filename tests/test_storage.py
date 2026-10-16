import os
import sys
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_load_notified_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr('config.NOTIFIED_FILE', str(tmp_path / "notified.json"))
    import storage
    assert storage.load_notified() == set()


def test_save_and_load_notified(tmp_path, monkeypatch):
    monkeypatch.setattr('config.NOTIFIED_FILE', str(tmp_path / "notified.json"))
    import storage
    storage.save_notified({"abc123", "def456"})
    assert storage.load_notified() == {"abc123", "def456"}


def test_is_notified(tmp_path, monkeypatch):
    monkeypatch.setattr('config.NOTIFIED_FILE', str(tmp_path / "notified.json"))
    import storage
    storage.save_notified({"abc123"})
    assert storage.is_notified("abc123") is True
    assert storage.is_notified("xyz789") is False


def test_mark_notified(tmp_path, monkeypatch):
    monkeypatch.setattr('config.NOTIFIED_FILE', str(tmp_path / "notified.json"))
    import storage
    storage.mark_notified("new123")
    assert storage.is_notified("new123") is True


def test_corrupted_json_treated_as_empty(tmp_path, monkeypatch):
    f = tmp_path / "notified.json"
    f.write_text("not valid json{{{")
    monkeypatch.setattr('config.NOTIFIED_FILE', str(f))
    import storage
    assert storage.load_notified() == set()


def test_wrong_shape_json_treated_as_empty(tmp_path, monkeypatch):
    f = tmp_path / "notified.json"
    f.write_text("null")
    monkeypatch.setattr('config.NOTIFIED_FILE', str(f))
    import storage
    assert storage.load_notified() == set()
