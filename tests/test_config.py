import importlib
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_config_loads_env_vars(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token_123")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test_chat_456")
    import config
    importlib.reload(config)
    assert config.TELEGRAM_BOT_TOKEN == "test_token_123"
    assert config.TELEGRAM_CHAT_ID == "test_chat_456"


def test_config_defaults():
    import config
    importlib.reload(config)
    assert config.NOTIFIED_FILE == "notified.json"
    assert config.CHECK_INTERVAL_HOURS == 24
