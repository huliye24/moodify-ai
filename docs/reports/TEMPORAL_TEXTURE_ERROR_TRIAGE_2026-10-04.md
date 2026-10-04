# Temporal Texture Error Triage — 2026-10-04

> **Task:** CI_HOTFIX_002 — Temporal Texture Error Triage (Phase A)
> **Branch:** `ci/temporal-texture-triage` (from `origin/main`)
> **Audited main:** `1dd5b2e14cdc67e673c26a2aa62e556c12066b20`
> **DOCS_ONLY = YES** — no baseline regenerated, no CI changed, no product code changed.
> **Depends on:** `CI_HOTFIX_001_TEMPORAL_TEXTURE_BASELINE_AUDIT.md`

---

## 1. Summary

**109 error-level findings**, reproduced on current main. They reduce to **7 groups** and
**5 human decisions**.

```text
109 findings
  → 7 root groups
  → 5 decisions
```

Two of the seven groups are **measured, not proposed**: the tooling artifacts
(2 findings, proven by controlled experiment) and the derived cluster
(21 findings that collapse to 9 oversized functions).

**The tool is factually correct.** Every FUNCTION-LENGTH claim was verified
independently against the AST — `release_cli.py:main` really is **285 lines**.
These are not invented findings.

**Agent Foundation introduces zero of them.**

---

## 2. Current Main

```text
origin/main  = 1dd5b2e14cdc67e673c26a2aa62e556c12066b20

files_scanned        660
findings total      1443   (error 109 · warning 771 · info 563)
baseline (08-20)    1422   (error  92 · warning 835 · info 495)
guard              {"new": 213, "new_errors": 21, "new_warnings": 97, "resolved": 192} → exit 1
```

109 matches the previously reported count — no drift to explain.

**Of the 109: 88 are already in the baseline, 21 are new relative to it.** Only the 21
currently fail the build, but all 109 are in scope for triage because a baseline
refresh would ratify all of them.

---

## 3. Required Triage Table

| Group | Rule | Count | Sev | Primary Paths | Classification | Root Cause | Recommended Action | Human? | Baseline eligible |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| **G1** | TT-EMPTY-EXCEPTION | 39 | error | `calibration/server.py`, `audio_io.py`, `ab_compare.py`, `calibration/online.py`, +25 more | **E — NEEDS_HUMAN_DECISION** | 39 sites of bare `except …: pass`; uniform, verified | Decide the codebase policy once (D1) | **YES** | NO |
| **G2** | TT-COMPLEXITY | 19 | error | `diagnosis/engine.py`, `stems/store.py`, `data_plane/*`, `scripts/*` | **E — NEEDS_HUMAN_DECISION** | Complexity proxy ≥20 in functions that are neither long nor nested | Decide with D2 | **YES** | NO |
| **G3** | TT-FUNCTION-LENGTH | 10 | error | `auditory/evidence/resolver.py`, `auditory/metrics.py`, `physics/*` | **E — NEEDS_HUMAN_DECISION** | Functions >120 lines not caught by G6 | Decide with D2 | **YES** | NO |
| **G4** | TT-PARAMETERS | 14 | error | `auditory/reports.py`, `auditory/manifests.py`, `data_plane/pipeline.py` | **B — ACCEPTED_DEBT** (proposed) | Assembler/builder signatures with ≥9 params | Carry; revisit when each module is next substantially touched | ratify | **YES** |
| **G5** | TT-NESTING | 4 | error | `diagnosis/defect_classifier.py:335`, `physics/experiments_2.py:300`, `tests/baseline/check_regression.py:40`, `moodify-music-package/tests/test_architecture.py:34` | **A — REAL_FIX** | Nesting depth ≥6; bounded, mechanical | `FIX_NOW` | no | NO |
| **G6** | TT-COMPLEXITY + TT-FUNCTION-LENGTH (+1 exception, +1 params, +1 nesting) | 21 | error | 9 functions (see §4) | **E — NEEDS_HUMAN_DECISION** (inherit root) | Nine oversized functions, each flagged by several rules | Decide with D2 — one decision covers all 21 | **YES** | NO |
| **G7** | TT-EMPTY-EXCEPTION | 2 | error | `scripts/generate_calibration_versions.py:91`, `physics/reliable_runner.py:152` | **C — TOOLING_ARTIFACT** | Same finding re-keyed after a line shift — **proven** | Must not enter any baseline | no | NO |

**Partition check:** 39 + 19 + 10 + 14 + 4 + 21 + 2 = **109** ✓ every finding assigned exactly once.

> **Provenance of the classification:** G7 and G6 are **measured**. G5 is concrete and
> verifiable. G1/G2/G3 were verified as factually correct but their *disposition* is a
> policy choice, hence E. G4 is a **proposal** requiring ratification — see §10.

---

## 4. Derived Cluster (G6)

Nine functions, each flagged by multiple rules. Decomposing one function removes
**all** of its findings — these are 9 root causes, not 21 decisions.

| Function | Path | Rules |
| --- | --- | --- |
| `prepare_comparison` | `moodify/ab_compare.py` | complexity · function-length · empty-exception |
| `run_golden_pipeline` | `moodify/reconstruction/pipeline.py` | complexity · function-length · parameters |
| `main` | `moodify/release_cli.py` | complexity · function-length · nesting |
| `render_report_markdown` | `moodify/auditory/report_render.py` | complexity · function-length |
| `render_report_html` | `moodify/auditory/report_render.py` | complexity · function-length |
| `assemble_judgment_evidence` | `moodify/auditory/evidence/resolver.py` | complexity · function-length |
| `build_report_frame` | `moodify/ui/report_window.py` | complexity · function-length |
| `experiment_G` | `moodify/physics/experiments_2.py` | complexity · function-length |
| `_sweep_table` | `moodify/auditory/sensitivity.py` | function-length (+ others) |

---

## 5. Are the findings real? (independent verification)

§4 forbids classifying something as REAL_FIX merely because the tool says `error`.
The tool's claims were therefore re-measured from the AST:

| Function | Tool severity | Measured lines |
| --- | --- | ---: |
| `release_cli.py:main` | error | **285** |
| `sensitivity.py:_sweep_table` | error | **193** |
| `report_render.py:render_report_html` | error | **193** |
| `resolver.py:assemble_judgment_evidence` | error | **167** |
| `report_render.py:render_report_markdown` | error | **154** |
| `ab_compare.py:prepare_comparison` | error | **153** |
| `report_window.py:build_report_frame` | error | **147** |

**15 functions exceed 120 lines in `core/src`.**

The 42 empty-exception findings were verified against source too: **all 42 are genuine
`except …: pass`** (41 bare, 1 with a trailing comment). Sampled sites are real:

```python
# moodify/audio_io.py:15      swallows ALL soundfile failures to fall through to librosa
except Exception:
    pass

# moodify/calibration/server.py:80   silently skips malformed JSONL lines
except Exception:
    pass
```

**Verdict: the tool is correct. Nothing here is a phantom.**

---

## 6. Fingerprint Stability (§12, §13)

### Fingerprint fields, per rule

`fingerprint = sha256(rule \0 path \0 symbol \0 message_key)[:20]` — the signature
excludes the line number, but five of ten rules put it back into `message_key`:

| Rule | `message_key` | Line in key? | Stable under an inserted line? | Stable under a file move? |
| --- | --- | :---: | :---: | :---: |
| `PY-SYNTAX` | `"syntax-error"` | no | ✅ | ❌ path changes |
| `TT-FUNCTION-LENGTH` | `"function-length"` | no | ✅ | ❌ |
| `TT-COMPLEXITY` | `"complexity"` | no | ✅ **(probed)** | ❌ |
| `TT-NESTING` | `"nesting"` | no | ✅ | ❌ |
| `TT-PARAMETERS` | `"parameters"` | no | ✅ | ❌ |
| `TT-BROAD-EXCEPTION` | `f"broad-exception:{handler.lineno}"` | **yes** | ❌ | ❌ |
| `TT-EMPTY-EXCEPTION` | `f"empty-exception:{handler.lineno}"` | **yes** | ❌ | ❌ |
| `TT-LINE-LENGTH` | `f"line-length:{number}"` | **yes** | ❌ **(probed)** | ❌ |
| `TT-DEBT-MARKER` | `f"debt:{marker}:{number}"` | **yes** | ❌ | ❌ |
| `TT-EMPTY-CATCH` (js) | `f"empty-catch:{number}"` | **yes** | ❌ | ❌ |

### Controlled stability probe (§13)

One harmless comment line was inserted **above** an existing finding in each of two
files; the audit was re-run; both files were reverted before anything was committed.

| Rule probed | Before | After | Outcome |
| --- | --- | --- | --- |
| `TT-LINE-LENGTH` (`workbench.js:39`) | `415b86bd2ba4df922b63` | **gone**, re-keyed `610ad6a298847a2861f8` at line 40 | **resolved + new** |
| `TT-COMPLEXITY` (`sound_protocol.py:35`) | `4ec955d286113d493e20` | **unchanged**, line 35 → 36 | **same** |

**This is the decisive contrast:** the identical edit (adding one comment) is harmless
to a stable-keyed rule and silently re-keys a line-keyed rule. The defect is the
**key**, not line movement itself.

Consequence in the current run: **2 of the 109** are provably this artifact (G7).
The defect inflates `new`/`resolved` noise across the ~1150 line-keyed findings —
which is why `resolved = 192` accompanies `new = 213`.

### Historical check

The two artifact findings are in files that **predate** the baseline
(`generate_calibration_versions.py` 2026-05-28, `reliable_runner.py` 2026-05-29) —
their identity changed while their meaning did not. The other 19 new errors are in
files **newer** than the baseline (`ab_compare.py` 2026-10-03, `report_render.py`
2026-10-02, `ui/*` 2026-10-02, `sound_protocol.py` 2026-09-23, …), so those are real
findings in never-baselined code — **not** artifacts.

---

## 7. Agent Foundation Impact (§15)

Measured directly — the audit was run on each branch head and compared to main:

| Tree | errors | total |
| --- | ---: | ---: |
| `main` (`1dd5b2e1`) | **109** | 1443 |
| `codex/ecosystem-001-capability-map` | **109** | 1431 |
| `codex/ecosystem-002-capability-registry` | **109** | 1434 |
| `codex/ecosystem-003-provider-router` | **109** | 1438 |
| `codex/project-model-001` | **109** | 1443 |

```text
AGENT_FOUNDATION_NEW_ERRORS = 0
```

**Every branch produces exactly 109 errors — identical to main.** (Totals differ
slightly because these branches are based on `01edc902`, before HOTFIX 000 and the
desktop release merged into main; that difference is inherited content, not added
findings.) HOTFIX 000 is already in main and contributes none of the 109.

---

## 8. Baseline Eligibility (§11)

| Group | Classification | Baseline eligible |
| --- | --- | :---: |
| G4 — TT-PARAMETERS (14) | ACCEPTED_DEBT | **YES** |
| G1, G2, G3, G6 (89) | NEEDS_HUMAN_DECISION | NO (until decided) |
| G5 (4) | REAL_FIX | NO |
| G7 (2) | TOOLING_ARTIFACT | NO |

**Only G4 may enter a future baseline as it stands.** Everything else is blocked on a
decision, is scheduled for fixing, or must never be baselined.

---

## 9. What is NOT eligible and why

- **G7 (2)** — artifacts. Baselining them would encode a tooling bug as accepted debt
  and it would reappear in a different form after the next edit.
- **G5 (4)** — bounded and mechanical; accepting it would be carrying debt that costs
  less to clear than to record.
- **G1/G2/G3/G6 (89)** — the *facts* are verified; only the *disposition* is open.
  Classifying them ACCEPTED_DEBT now would be the tool deciding what debt is
  acceptable, which is exactly what §23 forbids.

---

## 10. HUMAN DECISIONS REQUIRED

> **D1 — Bare `except …: pass`: allowed, or fixed?**
> **Impact:** 39 findings (G1), all verified `except …: pass`.
> **Risk of leaving:** 39 places where failure is discarded silently. This is in
> direct tension with the project's own position that a machine must not suppress
> failure evidence — the same principle HOTFIX 000 enforced for missing runtimes.
> **Risk of fixing:** mechanical, but needs a policy (log? narrow the exception type?
> both?) or it becomes 39 ad-hoc edits.
> **Recommendation:** `FIX_NOW` — decide one rule (minimum: log or narrow the caught
> type), then apply it mechanically. Priority subset: the core decode/analysis paths
> (`audio_io.py`, `auditory/*`) where a swallowed error can produce a wrong number.

> **D2 — Oversized / complex functions: decompose now, or carry with an owner?**
> **Impact:** 50 findings across G2 + G3 + G6, reducing to ~29 root functions.
> **Risk of leaving:** the worst are 285/193/193/167 lines. `release_cli.py:main` and
> `reconstruction/pipeline.py:run_golden_pipeline` are load-bearing.
> **Risk of fixing:** real refactor across measurement, reconstruction and CLI paths —
> must not change behaviour, and these paths have oracle-backed tests to satisfy.
> **Recommendation:** `DEFER_WITH_OWNER` for the 10 non-derived length findings, and
> `FIX_NOW` for the four worst derived ones (285/193/193/167) as a bounded first step.

> **D3 — ≥9-parameter signatures: accept or restructure?**
> **Impact:** 14 findings (G4).
> **Risk of leaving:** low — mostly internal assembler signatures.
> **Risk of fixing:** touches every call site for a readability gain.
> **Recommendation:** `ACCEPT_TEMPORARILY`, review point = next substantial change to
> each module. This is the one group proposed as baseline-eligible.

> **D4 — Repair the guard and regenerate the baseline?**
> **Impact:** unblocks the ~1150 line-keyed findings from churning, and makes the gate
> meaningful again.
> **Risk of doing nothing:** the check stays red on main and on every PR forever.
> **Recommendation:** `FIX_NOW` — but only after D1–D3 fix the classification, and
> as **one** change: fix `message_key` **and** regenerate from a recorded clean
> commit (see CI_HOTFIX_001 §11 for the exact commands).

> **D5 — Should the guard also run on `push: branches: [main]`?**
> **Impact:** makes main's state visible so `red` on a PR can mean "this PR regressed".
> **Risk:** main goes red on every push until D4 completes.
> **Recommendation:** `DEFER_WITH_OWNER` — land it *after* D4, not before.

**Five decisions, 109 findings.**

---

## 11. Recommendation vocabulary

| Group | Verdict |
| --- | --- |
| G1 — empty exceptions | `FIX_NOW` |
| G2 — complexity (non-derived) | `DEFER_WITH_OWNER` |
| G3 — function length (non-derived) | `DEFER_WITH_OWNER` |
| G4 — parameters | `ACCEPT_TEMPORARILY` |
| G5 — nesting | `FIX_NOW` |
| G6 — derived oversized functions | `FIX_NOW` for the four worst, `DEFER_WITH_OWNER` for the rest |
| G7 — tooling artifacts | `FIX_NOW` (as part of D4's guard repair) |

No `REMOVE_LEGACY` is recommended: none of the 109 sits on a path scheduled for
removal, and classifying one as legacy to avoid fixing it would be exactly the
shortcut §1 forbids.

---

## 12. Files Changed

```text
A  docs/reports/TEMPORAL_TEXTURE_ERROR_TRIAGE_2026-10-04.md
```

Nothing else. Probe edits to `sound_protocol.py` and `workbench.js` were reverted
before any commit; `git status` confirmed clean afterwards.

---

## 13. Side Effects

```text
BASELINE_CHANGED      = NO
CI_CHANGED            = NO
PRODUCT_CODE_CHANGED  = NO
DOCS_ONLY             = YES
```

Scratch artifacts under `artifacts/` were removed. No PR was merged. Phase B
(fingerprint redesign, baseline regeneration, trigger change) was **not** started.

---

## 14. Core Principle

> **Do not ask a baseline to decide what debt is acceptable. Humans decide that; the
> baseline records the decision.**

109 findings became 7 groups and 5 decisions. **Two of the groups were measured
rather than argued** — which is the only reason the remaining three can be presented
as genuine choices instead of a pile of rows.
