# CI Reproducibility

- Ubuntu CI installs and verifies FFmpeg/ffprobe.
- Dependencies, including PyYAML, are declared in `pyproject.toml`.
- OpenAI is optional and lazy-imported.
- Required WAV fixtures are deterministic and generated in tests.
- No API key, proprietary media, MuseScore or SoX is required by core CI.
- Commands: `python -m ruff check src/moodify`; `python -m pytest tests/ -q`.
