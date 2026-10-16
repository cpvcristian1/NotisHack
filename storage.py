import json
import os

import config


def load_notified() -> set[str]:
    """Return the set of already-notified hackathon IDs.

    A missing, unreadable, or corrupt file is treated as empty so the
    deduplication state can be rebuilt from scratch.
    """
    if not os.path.exists(config.NOTIFIED_FILE):
        return set()
    try:
        with open(config.NOTIFIED_FILE, 'r') as f:
            return set(json.load(f))
    except (json.JSONDecodeError, TypeError, OSError):
        return set()


def save_notified(ids: set[str]) -> None:
    with open(config.NOTIFIED_FILE, 'w') as f:
        json.dump(list(ids), f)


def is_notified(hackathon_id: str) -> bool:
    return hackathon_id in load_notified()


def mark_notified(hackathon_id: str) -> None:
    ids = load_notified()
    ids.add(hackathon_id)
    save_notified(ids)
