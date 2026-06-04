# Fix Log — NEM-MOODIFY-STUDIO-OS-001 / Harden-6

**Date**: 2026-06-04
**Source**: MHP-062 Failure Analysis

---

## P0 Fixes

| # | Issue | File | Fix | Verified |
|---|-------|------|-----|----------|
| 1 | CLI_ARG_MISMATCH | `moodify_runtime/config.py:41-45` | Replaced 3 broken templates with 2 correct ones (`{input}` positional + `--output-dir`) | ✅ 119 unit + 3 real audio tests pass |

**Before** (all 3 templates broken):
```python
"{python} cli.py process --input {input} --output {output_dir} --preset {preset}"          # --input doesn't exist
"{python} -m moodify.cli process --input {input} --output {output_dir} --preset {preset}"  # --input/--output don't exist
"{python} cli.py process {input} --output {output_dir} --preset {preset}"                   # --output should be --output-dir
```

**After** (both templates correct):
```python
"{python} -m moodify.cli process {input} --output-dir {output_dir} --preset {preset}"
"{python} -m moodify.cli process {input} --output-dir {output_dir} --preset {preset} --json"
```

---

## P1 Fixes

| # | Issue | File | Fix | Verified |
|---|-------|------|-----|----------|
| 2 | PATH_RESOLUTION | `moodify_runtime/config.py:41-45` | Removed cwd-relative `cli.py` templates; use only package-relative `-m moodify.cli` | ✅ |

---

## P2 Fixes (Documented, Deferred)

| # | Issue | Status | Deferred Reason |
|---|-------|--------|-----------------|
| 3 | MP3_FORMAT | ⚠️ Documented | moodify.cli process expects WAV. 30 MP3 validation samples assembled. Add WAV conversion or MP3 support in next NEM. |
| 4 | JSONL compaction | 📋 Deferred | MHP-066 adds `compact_operator_jobs()` |
| 5 | Error handling gaps | 📋 Deferred | MHP-066 adds structured error handling |

---

## Test Verification

```bash
$ python3 -m pytest moodify_runtime/tests/ -q
119 passed in 0.74s

$ python3 -m pytest moodify_runtime/tests/test_real_audio.py -v -m slow
3 passed in 6.67s

$ python3 -m pytest moodify_runtime/tests/test_full_stack_smoke.py -v
7 passed in 3.74s
```

**Total**: 129 tests, 0 failures. All fixes verified.
