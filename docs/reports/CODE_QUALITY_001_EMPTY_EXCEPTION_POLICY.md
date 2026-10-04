# CODE_QUALITY_001 — Empty Exception Policy

> **Task:** CODE_QUALITY_001 — remove silent failure swallowing (G1 only)
> **Branch:** `code-quality/empty-exception-policy-001`
> **Base:** `origin/main` = `1dd5b2e14cdc67e673c26a2aa62e556c12066b20`
> **Depends on:** CI_HOTFIX_002 (triage, decision `D1 = FIX_NOW`)
> **Baseline / CI tool changes:** NONE

---

## 1. Summary

**The `TT-EMPTY-EXCEPTION` error group is gone: 42 → 0.**

```text
                     before   after
TT-EMPTY-EXCEPTION       42       0
all error findings      109      67     (remainder = G2–G6, out of scope)
```

**One discrepancy with the triage is resolved up front.** CI_HOTFIX_002 reported
G1 = 39; the audit reports **42**. Both are right: the triage subtracted the 2
proven tooling artifacts and the 1 finding inside a derived function. But all 42
are real `except …: pass` **sites** — the artifacts were merely re-keys of real
sites — so fixing the code removes all 42, and the target is 42, not 39.

---

## 2. Base

```text
origin/main  1dd5b2e14cdc67e673c26a2aa62e556c12066b20
branch       code-quality/empty-exception-policy-001
```

Re-checked with `git fetch` at task start, not taken from the task document.

---

## 3. Policy applied

The rule (`tools/temporal_texture/temporal_texture_audit.py:191`) flags a handler
whose body is **only** `pass` and/or empty-string docstrings:

```python
if not node.body or all(
    isinstance(item, (ast.Pass, ast.Expr)) and (
        isinstance(item, ast.Pass)
        or (isinstance(item, ast.Expr) and isinstance(item.value, ast.Constant)
            and item.value.value in {None, ""}))
    for item in node.body):
    self.empty_handlers.append(node)
```

**It does not care how narrow the caught type is.** `except ImportError: pass` is
flagged exactly like `except Exception: pass`. That shapes the whole task, and the
report distinguishes the two kinds of change below.

Applied rule, per site — choose the smallest correct replacement:

| # | Situation | Treatment |
| --- | --- | --- |
| 1 | Broad catch, knowable failure set | **Narrowed** to the expected exception types |
| 2 | Broad catch, failure set genuinely unknowable | Narrowed as far as defensible; where kept broad, **logged** using the module's own existing idiom |
| 3 | Already narrow and intentional | Type kept; `pass` → `...` plus a comment stating the intent |
| 4 | Test assert-raises idiom | Replaced with `pytest.raises(...)` — the handler disappears entirely |

For (2) the file's own conventions were the guide: `workflow_engine.py` already
uses `except Exception as e: logger.warning(...)` for the same `_diagnose_audio`
call at line 396, so matching it is consistency, not invention.

`audio_io.py` was narrowed **from measurement, not assumption** — every soundfile
failure (unsupported format, missing file, corrupt file) raises
`sf.SoundfileError`, whose MRO is `LibsndfileError → SoundFileRuntimeError →
SoundFileError → RuntimeError`, so the library's own base class is the correct catch.

---

## 4. Site Classification

All 42 sites, by behaviour:

| Class | Count | Examples |
| --- | ---: | --- |
| **fallback** (A unavailable/failed → try B) | 14 | `audio_io.py` soundfile→librosa · `engine.py`/`preprocessing.py` soxr→scipy→librosa · `emotion_targets.py` preset→DeepSeek→default · `search.py` calibration→uncorrected · `stems/client.py` JSON body→raw text |
| **test idiom** (assert-raises) | 8 | `test_ch02_phase1_evidence.py` ×6 · `test_store.py` · `safety/test_projection.py` |
| **tolerant parser** (skip malformed input) | 6 | `memory/history.py` · `calibration/server.py` · `physics/reliable_runner.py` · `ab_compare.py` · `ops/e2e_runner.py` · `calibration/online.py` |
| **optional dependency** (`ImportError`) | 5 | `engine.py`/`preprocessing.py` (soxr) · `icc.py` (pingouin) · `resource_meter.py` (tracemalloc) · `ui/theme.py` (tkinter) |
| **other** (optional display / best-effort cosmetic) | 4 | `cli.py` calibration line · `workflow_engine.py:484` enrichment · `ui/app.py`/`report_window.py` theme |
| **control flow** (the exception *is* the signal) | 3 | `ui/app.py` `queue.Empty` poll · `object_key.py` trial-parse ×2 |
| **cleanup** (must not mask the primary failure) | 2 | `stems/store.py` ×2 unlink |

**By kind of change:**

```text
20  narrowed          (semantic change: real fix)
 8  test-idiom        (handler removed entirely)
14  intent marker     (type was already correct; `pass` → `...` + comment)
──
42
```

**The 14 intent-marker sites are reported as such.** They are not semantic fixes —
the exception boundary was already correct, and the rule flags them only because
the body was empty. Marking them is what §3.D's own example (`except ImportError:
...`) prescribes, and it documents intent where `pass` left it implicit. They are
disclosed rather than counted as fixes.

---

## 5. Files Changed

27 modified, 1 added.

```text
src/moodify/                       ab_compare.py · audio_io.py · cli.py · icc.py
                                   calibration/{online,server}.py
                                   data_plane/object_key.py
                                   diagnosis/{engine,health_scorer,preprocessing}.py
                                   knowledge/emotion_targets.py
                                   memory/history.py · optimizer/search.py
                                   orchestration/workflow_engine.py
                                   physics/reliable_runner.py
                                   reconstruction_job/resource_meter.py
                                   safety/test_projection.py
                                   stems/{client,store}.py
                                   ui/{app,report_window,theme}.py
tests/                             auditory/test_ch02_phase1_evidence.py
                                   baseline/run_baseline.py
                                   reconstruction_job/test_store.py
                                   test_exception_boundaries.py          (new)
scripts/                           generate_calibration_versions.py
ops/                               e2e_runner.py
```

No file under `.moodify/`, `.github/` or `tools/temporal_texture/` was touched.

---

## 6. Behaviour Changes

Unexpected failures that were previously invisible now surface. The sites where
this is a **correctness** change, not just a style change:

- **`safety/test_projection.py` swallows its own assertion.** The block was
  `try: … assert log2 == []  except Exception: pass` — so a failing assertion was
  caught and discarded, and the check could never fail. `AssertionError` is now
  outside the catch set. *This is the clearest defect the task repaired.*
- **`audio_io.py`** no longer treats every possible error as "soundfile can't read
  this". A programming error now propagates instead of being silently re-attributed
  to librosa.
- **`memory/history.py`, `calibration/server.py`, `calibration/online.py`** no
  longer swallow arbitrary runtime errors while skipping bad data.
- **`optimizer/search.py`, `workflow_engine.py`, `emotion_targets.py`** now catch
  the failure modes they actually expect, so an unexpected one is not reported as
  "calibration unavailable".

Expected behaviour is preserved everywhere: fallback order, skip-and-continue,
cleanup tolerance and the `queue.Empty` poll all still work — proven in §7.

**One consequence of my own change, disclosed:** the explanatory comments added to
`resolve_emotion_from_nl` (`emotion_targets.py`) pushed that function from ~58 to
**62 lines**, crossing the 60-line `TT-FUNCTION-LENGTH` **warning** threshold. It
does not affect the build (`fail_on_new_warnings = false`). I did not trim the
comments: shortening documentation to sit under an arbitrary line count is
optimising for the metric rather than the code.

---

## 7. Tests

New: `moodify-core-package/tests/test_exception_boundaries.py` (5 tests).

Each encodes the two properties §13 asks for — the intended fallback still
happens, **and** an unexpected failure no longer disappears. The second is a
regression guard: `test_history_does_not_swallow_unexpected_errors` was verified
to propagate, i.e. **it fails against the pre-fix `except Exception: pass`**.

`test_m4a_falls_through_to_librosa_instead_of_aborting` asserts on *which layer*
raised, not on whether decoding succeeds, so it proves §11's fallback is intact
without depending on an audio backend being installed.

```bash
$ python -m pytest tests/test_exception_boundaries.py -q
4 passed, 1 skipped        (skip: no M4A backend in this environment)

$ python -m pytest -q
1209 passed, 6 skipped, 0 failed in 875.77s (0:14:35)
```

**Arithmetic:** 1184 (main@`5fc74d24`) + 20 (HOTFIX 000) + 5 (this task) = **1209** ✓
The 6 skips are unchanged pre-existing environment-conditional skips.

```bash
$ python -m ruff check src/moodify tests/test_exception_boundaries.py
(clean)
```

`ops/e2e_runner.py` carries a pre-existing `F401 unused import: mimetypes` at
line 92 — present in `HEAD`, unrelated to this task's diff (lines 63-66). Left
alone per §15 ("do not mass-fix unrelated lint").

### §16 Agent Foundation compatibility

Verified on this base:

```text
moodify                      real
moodify.auditory.metrics     real
moodify.auditory.loudness    real      oracle: ours -9.712 vs pyloudnorm -9.754 (+0.043 LU)
moodify.capabilities         NOT PRESENT on this branch   (PR #42 open)
moodify.project              NOT PRESENT on this branch   (PR #44 open)
```

No cross-layer dependency was created. The two absent layers are simply not
merged yet, so there is nothing here that could break them.

> **Correction of an early check of my own.** A first pass reported both layers
> "importable". That was wrong: this working tree held stale untracked
> `capabilities/` and `project/` directories containing **only `__pycache__`**, so
> Python resolved them as empty *namespace packages* (`__file__ is None`) and the
> import succeeded while importing nothing. The stale directories were removed.
> Worth noting generally: a successful import did not mean the layer was present.

---

## 8. Temporal Texture

Baseline **unchanged**; the tool was **not** modified. Counts from the unchanged
baseline:

```text
                        before   after
error findings             109      67
  TT-EMPTY-EXCEPTION        42       0
  TT-COMPLEXITY             28      28
  TT-FUNCTION-LENGTH        19      19
  TT-PARAMETERS             15      15
  TT-NESTING                 5       5

guard  new / new_errors / resolved
      213 /         21 /      192   →   238 / 14 / 277
```

`new_errors` fell 21 → 14 (exactly the 7 empty-exception findings that were new).

**`new` rose while `new_errors` fell** — and this is the G7 defect demonstrating
itself at scale. My edits add comment lines, and five of the tool's rules key the
fingerprint on the **line number**:

```text
disappeared: TT-EMPTY-EXCEPTION 42 · TT-BROAD-EXCEPTION 40 · TT-DEBT-MARKER 13 · TT-LINE-LENGTH 4
appeared   : TT-BROAD-EXCEPTION 21 · TT-DEBT-MARKER 13 · TT-LINE-LENGTH  4 · TT-FUNCTION-LENGTH 1
38 of the appeared findings share (rule, path, symbol) with a disappeared one
```

`TT-DEBT-MARKER` 13→13 and `TT-LINE-LENGTH` 4→4 are pure re-keying: nothing about
those findings changed except which line they sit on. **The gate is now red for a
different, smaller reason than before, and still not because of real new debt.**

---

## 9. Side Effects

```text
BASELINE_CHANGED      = NO
CI_TOOL_CHANGED       = NO
PRODUCT_BEHAVIOUR     = preserved except where an unexpected failure now surfaces (see §6)
DOCS_ONLY             = NO — this task legitimately changes code; it changes no
                        baseline, no CI rule and no schema
```

Scratch artifacts under `artifacts/` removed. The two stale `__pycache__`-only
directories were deleted (§7).

---

## 10. Deferred

Out of scope by §20, and **not** started:

```text
G2 TT-COMPLEXITY       28    (D2 decision pending)
G3 TT-FUNCTION-LENGTH  19
G4 TT-PARAMETERS       15    (proposed ACCEPTED_DEBT)
G5 TT-NESTING           4    (REAL_FIX, not started)
G6 derived functions   21
G7 tooling artifacts    2
baseline regeneration · fingerprint redesign · workflow trigger change
```

---

## 11. Core Principle

> **A failure may be recoverable, but it must never be invisible by accident.**

The group is now empty. Two of the 42 sites were hiding something that mattered —
one of them an assertion that could not fail — and the rest were made explicit
about a decision they had been making silently.
