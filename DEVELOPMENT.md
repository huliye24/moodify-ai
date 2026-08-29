# Moodify Development Guide

## Prerequisites

- Python 3.10 or later; CI uses Python 3.11.
- `pip` and a virtual environment tool.
- FFmpeg is optional for tests that explicitly require FFmpeg/FFprobe; those
  tests skip when the tool is unavailable.

## Setup

```bash
git clone https://github.com/huliye24/moodify-ai.git
cd moodify-ai/moodify-core-package
python -m venv .venv
# PowerShell: .\.venv\Scripts\Activate.ps1
# POSIX: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run Tests and Checks

```bash
cd moodify-core-package
python -m ruff check src tests ../tests
python -m pytest -q tests ../tests
```

Run focused checks during development:

```bash
python -m pytest -q tests/mrs tests/api
python -m ruff check src/moodify/mrs src/moodify/api tests/mrs tests/api
```

## Local API Debugging

The repository FastAPI application can be started locally:

```bash
cd moodify-core-package
python -m uvicorn moodify.api.main:app --reload
```

The experimental integration facade is available under
`/api/v1/intelligence`. It accepts local, size-bounded uploads only; starting
the application does not prove cloud deployment, production capacity, or MRS
validation.

## Debugging Principles

- Reproduce issues with generated or authorized fixtures.
- Keep temporary output outside version control.
- Inspect structured errors and evidence artifacts before changing rules.
- Treat an uncertain auditory judgment as a reason to escalate, not to invent a
  confident result.
