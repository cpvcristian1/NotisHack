import time

import requests

import config

API_BASE = "https://api.telegram.org/bot{token}/sendMessage"
MAX_LEN = 4000  # Telegram hard limit is 4096


def format_message(hackathons: list[dict]) -> str:
    """Render hackathons as a Telegram (Markdown) message body."""
    if not hackathons:
        return "🤖 Sin novedades de hackathones de IA hoy."
    lines = [f"🤖 Nuevos hackathones de IA ({len(hackathons)} encontrados):\n"]
    for i, h in enumerate(hackathons, 1):
        lines.append(f"{i}. [{h['title']}]({h['url']})")
        lines.append(f"   📍 Modalidad: {h.get('location', 'N/A')}")
        if h.get('prize'):
            lines.append(f"   🏆 Premio: {h['prize']}")
        if h.get('deadline'):
            lines.append(f"   ⏰ Deadline: {h['deadline']}")
        lines.append(f"   🔗 Inscripción: {h['url']}\n")
    return "\n".join(lines)


def _chunk(text: str, limit: int = MAX_LEN) -> list[str]:
    """Split text into pieces of at most `limit` chars, on line boundaries."""
    if len(text) <= limit:
        return [text]
    chunks, cur = [], ""
    for line in text.split("\n"):
        candidate = f"{cur}\n{line}" if cur else line
        if len(candidate) > limit and cur:
            chunks.append(cur)
            cur = line
        else:
            cur = candidate
    if cur:
        chunks.append(cur)
    return chunks


def _send(text: str) -> bool:
    url = API_BASE.format(token=config.TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": False,
    }
    last_body = ""
    for attempt in ("send", "retry"):
        resp = None
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            return True
        except requests.RequestException as e:
            last_body = (resp.text[:200] if resp is not None else "")
            print(f"Warning: Telegram {attempt} failed: {e} — body: {last_body}")
            if attempt == "send":
                time.sleep(5)
    return False


def send_summary(hackathons: list[dict]) -> bool:
    """Send the summary to Telegram. Returns True on success, False on failure.

    Nothing to send counts as success. Long messages are split into chunks;
    all chunks must succeed for the result to be True.
    """
    if not hackathons:
        return True
    ok = True
    for chunk in _chunk(format_message(hackathons)):
        if not _send(chunk):
            ok = False
    return ok
