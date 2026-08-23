# Cross-Package Test Suite

This directory contains repository-level smoke tests that exercise the core
package as an installed dependency. It complements, rather than replaces,
the detailed suite in `moodify-core-package/tests/`.

## Scope

- `test_audio.py` verifies loading and basic acoustic analysis with a generated
  WAV fixture.
- `test_mrs.py` verifies the experimental MRS input/output contract.
- `test_api.py` verifies that the experimental API facade registers and keeps
  unimplemented processing explicit.
- `fixtures/` documents fixture rules. No private or licensed audio belongs in
  this directory.

Run the full engineering suite from `moodify-core-package`:

```bash
python -m pytest -q tests ../tests
```

The API and MRS modules are experimental. A passing smoke test verifies their
contract, not perceptual quality, cloud availability, or production readiness.
