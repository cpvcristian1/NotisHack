# NotisHack

[![Tests](https://github.com/cpvcristian1/NotisHack/actions/workflows/tests.yml/badge.svg)](https://github.com/cpvcristian1/NotisHack/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A small Python bot that checks several hackathon and competition sources every
day and sends a Telegram summary with the ones that match a set of filters.

## How it works

`main.py` is the whole pipeline: fetch, filter, deduplicate, notify.

**Sources** — each module exposes `fetch_hackathons()` and returns a list of
normalized dicts (`id`, `title`, `url`, `deadline`, `prize`, `location`,
`description`).

| Source | Module | How it is read |
|---|---|---|
| Devpost | `sources/devpost.py` | Public JSON API, `open` and `upcoming` statuses, capped at 10 pages per status. |
| lablab.ai | `sources/lablab.py` | HTML page, parsed for the embedded JSON-LD `ItemList`. |
| Kaggle | `sources/kaggle.py` | Public competition service API, only active competitions with a future deadline. |
| brabble.ai | `sources/brabble.py` | REST API; only used when `BRABBLE_API_KEY` is set. |

A source that raises is logged as a warning and skipped, so one broken site
never stops the run.

**Filtering** — `filters.py` applies three rules, and a source item must pass
all of them:

- It mentions an AI topic (LLM, agent, machine learning, NLP, and similar).
- It is remote/online/virtual, or located in Vigo, Spain or Galicia.
- It does not forbid AI-assisted code. Wording that explicitly prohibits AI
  tools rejects the item; wording that allows them keeps it. Anything
  unspecified is kept.

**Deduplication** — `storage.py` keeps the IDs already sent in
`notified.json`. An item is dropped if its ID is present, and after a
successful Telegram send every sent ID is appended. A missing or corrupt file
is treated as empty, so the state rebuilds itself instead of crashing.

**Notification** — `notify.py` renders a Markdown message with title, link,
format, prize and deadline. Messages over 4000 characters are split on line
boundaries, since Telegram rejects anything above 4096. A failed request is
retried once after 5 seconds. IDs are only marked as notified when the whole
send succeeds.

## Project structure

| Path | Purpose |
|---|---|
| `main.py` | Entry point; runs the fetch, filter, dedupe and notify pipeline. |
| `config.py` | Environment variables and constants. |
| `filters.py` | AI topic, location and AI-coding-policy rules. |
| `notify.py` | Telegram message formatting, chunking and delivery. |
| `storage.py` | Read/write of the notified ID set. |
| `sources/` | One module per hackathon source. |
| `tests/` | Pytest suite for every module. |
| `notified.json` | Persisted deduplication state. |
| `.github/workflows/daily.yml` | Scheduled GitHub Actions run. |
| `Procfile`, `railway.toml` | Worker definitions for Railway-style hosting. |
| `requirements.txt` | Runtime and test dependencies. |

## Configuration

All configuration comes from environment variables, read in `config.py`.

| Variable | Required | Purpose |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token used to call the Telegram send API. Example: `123456:ABC...`. |
| `TELEGRAM_CHAT_ID` | Yes | Target chat or channel ID. Example: `-1001234567890`. |
| `BRABBLE_API_KEY` | No | Enables the brabble.ai source and is sent as a bearer token. Without it that source is skipped. Example: `example-key`. |

Never commit real values. The workflow reads them from repository secrets.

## Usage

```bash
pip install -r requirements.txt
python main.py
```

The run is one-shot: it exits after the summary is sent. There is no daemon
mode, so schedule it externally.

## Testing

```bash
pytest
```

The suite covers each source's parsing and error handling, the filter rules,
message formatting and chunking, the deduplication store, and the full
pipeline in `main.py`. Network calls are mocked with `monkeypatch`.

## Automation

`.github/workflows/daily.yml` runs the bot on GitHub Actions:

1. Triggers on the `0 9 * * *` cron (09:00 UTC daily) or manually through
   `workflow_dispatch`.
2. Checks out the repo and installs Python 3.12.
3. Runs `pip install -r requirements.txt`.
4. Runs `python main.py` with `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` and
   `BRABBLE_API_KEY` taken from repository secrets.
5. Commits the updated `notified.json` back to the branch with `GITHUB_TOKEN`
   (`contents: write`), using the message
   `chore: update notified state [skip ci]`. The commit is skipped when the
   file did not change.

The same entry point can be deployed as a worker: `Procfile` declares
`worker: python main.py`, and `railway.toml` sets the Nixpacks builder with
`python main.py` as the start command.

## License

Released under the MIT License. See [LICENSE](LICENSE).
