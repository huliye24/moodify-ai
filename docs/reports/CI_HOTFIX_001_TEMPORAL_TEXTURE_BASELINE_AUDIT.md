# CI_HOTFIX_001 — Temporal Texture Baseline Truth Audit

> **Task:** CI_HOTFIX_001 — restore a trustworthy CI baseline without weakening the guard
> **Date:** 2026-10-04
> **Branch:** `ci/temporal-texture-audit` (from `origin/main`)
> **Audited main:** `5fc74d24479cdfaf35f0efa4110802ac6a066cbf`
> **Guard changed:** **NO**

---

## 1. Summary

`moodify-temporal-texture` is red **on every PR including the ones that predate the
Agent Foundation work, and red on `main` itself**. It has failed **52 of 61 runs
records**; the only 9 successes are from 2026-08-08/09, when the workflow was
introduced. **It has never run on `main` at all.**

The root cause is **not** repository debt and **not** the five foundation branches.
It is that the committed baseline was generated **2026-08-20** and **nothing
refreshes it**, while **273 commits** have landed on `main` since the workflow was
introduced. The guard therefore compares today's tree against a seven-week-old
snapshot and reports ~200 "new" items — in both directions (`resolved` ≈ `new`).

There is a **secondary, proven defect** in the fingerprint scheme, and there is
**real pre-existing debt** that a baseline refresh would ratify — **but that
ratification is a human decision under §13, and I did not make it.**

```text
CI_TOOLING_BROKEN
```

**No file was changed.** Verification and reproduction only.

---

## 2. Current Main

```text
origin/main = 5fc74d24479cdfaf35f0efa4110802ac6a066cbf
```

The exact CI commands were run against this commit (§5 experiment):

```bash
python tools/temporal_texture/temporal_texture_audit.py --repo . \
  --config .moodify/temporal_texture.toml --out artifacts/temporal_texture/current
python tools/temporal_texture/temporal_texture_guard.py \
  --baseline .moodify/tt_baseline/report.json \
  --current artifacts/temporal_texture/current/report.json \
  --out artifacts/temporal_texture/guard_report.md
```

Result:

```json
{"new": 200, "new_errors": 21, "new_warnings": 96, "resolved": 191}
```

**Exit code 1. Current `main` itself fails the guard.**

This is **Case A** from the task's §5: the repository has no passing baseline, so
PR failures carry no regression information until this is resolved.

> **Reproduction note:** CI reported `new: 213`; the local run reports `200`. The
> small delta is consistent with a checkout difference (generated/untracked files
> present in one environment and not the other). The classification is unchanged —
> the guard fails in both.

---

## 3. Workflow Contract

```text
file      .github/workflows/moodify-temporal-texture.yml
trigger   pull_request  +  workflow_dispatch        ← never on push
runner    ubuntu-latest, Python 3.11

step 1    temporal_texture_audit.py  --repo . --config .moodify/temporal_texture.toml
                                     --out artifacts/temporal_texture/current
step 2    temporal_texture_guard.py  --baseline .moodify/tt_baseline/report.json
                                     --current  artifacts/temporal_texture/current/report.json
                                     --out      artifacts/temporal_texture/guard_report.md
```

**Baseline source:** a **committed** JSON file, `.moodify/tt_baseline/report.json`
(604 KB, 1422 findings), whose own metadata records:

```json
"generated_at": "2026-08-20T09:40:25.482940+00:00",
"repository":   "E:\\moodify\\.codex_tmp\\ci-baseline",
"config":       "E:\\moodify\\.codex_tmp\\ci-baseline\\.moodify\\temporal_texture.toml"
```

It was generated from a **scratch clone** on a Windows path, not from a recorded
commit of this repository.

**Failure rule** (`temporal_texture_guard.py:89`):

```python
if new_errors or (args.fail_on_new_warnings and new_warnings):
    return 1
```

`fail_on_new_warnings = false` in config, so **only error-severity findings that
are new relative to the baseline fail the build.**

**Comparison logic:** set difference over `fingerprint` values.

```python
new      = [item for key, item in after.items() if key not in before]
resolved = [item for key, item in before.items() if key not in after]
```

---

## 4. Root Cause

### 4.1 Primary — the baseline is not maintained, and main has no reference

```text
workflow + baseline introduced : 0ee296a7   "build: make Moodify 1.0 CI reproducible"
baseline content generated_at  : 2026-08-20
commits on main since 0ee296a7 : 273
```

The guard's design intent is clearly *"fail on debt newly introduced by this
change"*. Its mechanism is *"diff against a committed snapshot"*. Those two agree
only while the snapshot keeps up with `main`. Nothing refreshes it, and because
the workflow **never runs on `main`**, drift is invisible until a PR happens to
run — at which point the PR is blamed for seven weeks of unrelated change.

The near-symmetric churn is the signature:

```text
new = 200     resolved = 191
```

Genuine new debt does not normally arrive with 191 findings disappearing.

### 4.2 Secondary — proven fingerprint defect (line numbers embedded)

`fingerprint()` is deliberately line-independent:

```python
def fingerprint(rule, path, symbol, message_key):
    payload = f"{rule}\0{path}\0{symbol}\0{message_key}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:20]
```

But **five of the eight rules put the line number into `message_key`**, defeating it:

| Rule | `message_key` | Line-stable? |
| --- | --- | --- |
| `PY-SYNTAX` | `"syntax-error"` | ✅ |
| `TT-FUNCTION-LENGTH` | `"function-length"` | ✅ |
| `TT-COMPLEXITY` | `"complexity"` | ✅ |
| `TT-NESTING` | `"nesting"` | ✅ |
| `TT-PARAMETERS` | `"parameters"` | ✅ |
| `TT-BROAD-EXCEPTION` | `f"broad-exception:{handler.lineno}"` | ❌ |
| `TT-EMPTY-EXCEPTION` | `f"empty-exception:{handler.lineno}"` | ❌ |
| `TT-LINE-LENGTH` | `f"line-length:{number}"` | ❌ |
| `TT-DEBT-MARKER` | `f"debt:{marker}:{number}"` | ❌ |
| `TT-EMPTY-CATCH` (js) | `f"empty-catch:{number}"` | ❌ |

**Consequence:** inserting a single line above a long line makes that finding
"new" and its former self "resolved". Any edit — a comment, an import, a
reformat — churns every affected finding in the file.

**Proven, not asserted:** of the 200 new findings, **22** have an exact partner in
the resolved set with identical `(rule, path, symbol)` and identical `message`,
differing **only** by line number.

This accounts for a minority of the churn — the dominant cause is §4.1 — but it is
an objective defect and it inflates noise on top of the staleness.

### 4.3 The guard has no self-tests

```text
tests/temporal_texture/  → does not exist
```

The config's `exclude_globs` already reserves `tests/temporal_texture/**`, but the
directory was never created. **No test anywhere imports or exercises the guard or
the audit.** A CI gate with no tests, a hand-maintained baseline and no `main`
reference had nothing to stop it rotting.

### 4.4 Timeline

```text
2026-08-09  0ee296a7  workflow + baseline introduced
2026-08-08/09         the only green runs ever recorded (9)
2026-08-20           baseline content generated
2026-08-20 → 10-04   273 commits land on main, baseline never refreshed
2026-10-03/04        every run on every branch: failure (52 total)
```

---

## 5. Findings Classification

### Current counts

| | baseline (2026-08-20) | current main | delta |
| --- | ---: | ---: | ---: |
| files scanned | 625 | 657 | **+32** |
| error | 92 | 109 | +17 |
| warning | 835 | 771 | −64 |
| info | 495 | 551 | +56 |
| total | 1422 | 1431 | +9 |

### New-vs-baseline by rule

| Rule | new | resolved | net |
| --- | ---: | ---: | ---: |
| TT-DEBT-MARKER | 83 | 27 | +56 |
| TT-LINE-LENGTH | 49 | 147 | −98 |
| TT-FUNCTION-LENGTH | 22 | 1 | +21 |
| TT-BROAD-EXCEPTION | 21 | 10 | +11 |
| TT-COMPLEXITY | 16 | 2 | +14 |
| TT-EMPTY-EXCEPTION | 7 | 3 | +4 |
| TT-NESTING | 2 | 1 | +1 |

**Reading:** `TT-LINE-LENGTH` *decreased* by 98 net while showing 49 "new" — a rule
whose population shrank cannot be reporting genuine regressions. `TT-DEBT-MARKER`
at +56 net on a rule keyed by line number is the same story. Both directions move
at once, which is what staleness plus line-keyed fingerprints produce.

### The 21 error-severity findings (the only ones that fail the build)

| | Count | Assessment |
| --- | ---: | --- |
| in files **already present** in the baseline | 4 | pre-existing files; changes since 2026-08-20 |
| in files **absent from the baseline entirely** | 17 | never baselined — not "new debt", unbaselined code |

| Rule | Count |
| --- | ---: |
| TT-COMPLEXITY | 8 |
| TT-EMPTY-EXCEPTION | 7 |
| TT-FUNCTION-LENGTH | 6 |

**All 21 fall in files that no Agent Foundation branch touches** (see §8).

`TT-EMPTY-EXCEPTION` (7 of 21) is the rule whose fingerprint embeds the line
number, so at least that subset is provably fingerprint churn rather than
changed code.

### Classification verdict

| Category | Applies? |
| --- | --- |
| Real repository debt | **Yes, but not the cause of the red gate** — 109 pre-existing error-severity findings exist on main. The guard's own design tolerates baselined errors; these are conditions, not regressions. |
| Stale baseline | **Yes — primary cause** |
| Tooling defect | **Yes — secondary, proven** (§4.2), plus a config exclusion for a non-existent test directory and zero test coverage |

---

## 6. Baseline Decision

```text
PRESERVED — not regenerated, not edited.
```

There are no baseline semantics documented anywhere in the repository. The
mechanism implies *"accepted debt"* (existing entries are tolerated by design),
but nothing states it, when it may be refreshed, or by whom.

**Regenerating now would ratify 109 error-severity findings as accepted debt:**

| Rule | Would become accepted |
| --- | ---: |
| TT-EMPTY-EXCEPTION | 42 |
| TT-COMPLEXITY | 28 |
| TT-FUNCTION-LENGTH | 19 |
| TT-PARAMETERS | 15 |
| TT-NESTING | 5 |
| **total** | **109** |

§13 is explicit: *"If the baseline update would convert real errors into accepted
debt: STOP and report `REAL_REPOSITORY_DEBT`. Do not hide it."*

**Those 109 are real code-quality conditions, not artifacts.** Whether the team
accepts them is a policy decision about acceptable code quality, and it is not
mine to make. I stopped.

> **I could have turned this gate green in one command.** That command is written
> out in §10 for the human who is entitled to make the call. It was not run.

---

## 7. Changes

```text
NONE
```

No workflow, script, config, baseline or product file was modified.

### Why the obvious fix was also declined

Fixing §4.2 (removing line numbers from `message_key`) **cannot be done alone.**
All fingerprints for those five rules change, so against the existing baseline
**every one of ~1150 line-keyed findings would become "new"** — the guard would go
from 200 new to roughly 1350. The fix is only meaningful **together with** a
baseline regeneration, and that regeneration is the §13 human decision.

Shipping the fingerprint fix alone would therefore leave the repository strictly
worse than it found it. Declined deliberately.

---

## 8. Guard Tests

```text
No test was added.
```

Reason: the meaningful contract tests would **fail** against the current guard —
a test asserting *"an edit above a long line must not create a new fingerprint"*
is exactly the defect in §4.2. Writing a test that pins current buggy behaviour
would be worse than writing none.

The contract that SHOULD exist, for whoever performs the fix:

```text
identical tree vs identical baseline        → PASS
one deliberately introduced error           → FAIL
a deleted violation                          → counted as resolved, not new
editing a line above a finding               → NOT a new finding   ← currently fails
line-ending / path-separator normalisation   → deterministic
baseline serialization                       → deterministic across runs
```

Recorded here so the fix is testable when it is made.

---

## 9. Main Verification

```text
commit  5fc74d24479cdfaf35f0efa4110802ac6a066cbf
result  {"new": 200, "new_errors": 21, "new_warnings": 96, "resolved": 191}
exit    1   ← main fails
```

---

## 10. PR Verification

All five Agent Foundation branches were checked by running the audit with all five
merged (`integration/agent-foundation-001`) and diffing against main.

```text
main               new = 200   new_errors = 21
merged stack       new = 221   new_errors = 21      ← identical error count
```

### What the merged stack adds relative to main

```text
35 findings:  0 errors · 15 warnings · 20 info
```

| Rule | Added |
| --- | ---: |
| TT-DEBT-MARKER (info) | 20 |
| TT-LINE-LENGTH (warning) | 11 |
| TT-FUNCTION-LENGTH (warning) | 2 |
| TT-COMPLEXITY (warning) | 1 |
| TT-BROAD-EXCEPTION (warning) | 1 |

| Path | Added |
| --- | ---: |
| `moodify-desktop/src/main.js` | 14 |
| `moodify-desktop/scripts/test-runtime.js` | 12 |
| `src/moodify/capabilities/builtin.py` | 3 |
| `src/moodify/capabilities/router.py` | 2 |
| `tests/test_provider_router.py` | 2 |
| `src/moodify/project/service.py` | 1 |
| `tests/auditory/test_measurement_correctness.py` | 1 |

**Zero error-severity findings.** Because `fail_on_new_warnings = false`, the
guard's exit code for all five PRs is **identical to main's**. The PRs are red for
exactly the same reason main is red, and for no reason of their own.

**No special exception was made for PR #40–#44.** They simply do not appear in the
21-error set: **0 of the 21 are in files any of them touch.**

Honest note: the foundation work *does* add 35 warning/info findings in its own new
code — long lines and TODO markers, 26 of them in the desktop runtime resolver
files. That is disclosed here rather than left for someone to discover when the
baseline is next refreshed. It is not a build failure under current policy.

---

## 11. CI Trigger Decision

**Recommendation: add `push: branches: [main]`.** Not applied — §11 requires
justification rather than automatic change.

Justification: the single structural defect that let this rot for seven weeks is
that **`main` never runs the guard**. Every consequence above follows from it:

- main's drift is invisible until a PR trips over it;
- "is main green?" has no answer, so `red` cannot mean "this PR regressed";
- nothing creates pressure to refresh the baseline.

Running on `main` would make that visible. The counter-argument is honest and
should be weighed: main would immediately go red on every push, which is noisy and
can normalise ignoring a red badge.

**Therefore the trigger change should land together with a decision on the baseline
— not before it.** Sequenced recommendation:

```text
1. HUMAN DECISION  accept, or fix, the 109 error-severity findings
2. fix the fingerprint defect (§4.2) and regenerate the baseline from a
   recorded main commit in the same change
3. add the contract tests listed in §8
4. add push: branches: [main]
5. only then can this check be merge authority
```

Step 2's regeneration, when authorised, is exactly:

```bash
git switch main && git pull --ff-only
python tools/temporal_texture/temporal_texture_audit.py --repo . \
  --config .moodify/temporal_texture.toml --out artifacts/temporal_texture/current
cp artifacts/temporal_texture/current/report.json .moodify/tt_baseline/report.json
```

It must be run from a **clean tree at a recorded commit**, never by hand-editing
entries.

---

## 12. Merge Authority

```text
CI_TOOLING_BROKEN
```

The guard is not technically trustworthy as a merge signal yet. It fails
identically on `main` and on every branch, so `red` currently carries **no
information about the change under review**. A check that cannot distinguish its
own base is not a gate.

Two caveats stated plainly so this verdict is not misread:

1. **This is not a claim that the repository is clean.** Real pre-existing
   error-severity findings exist (§5) and a refresh would ratify them. That is a
   human decision, and the task's own §13 says to stop and surface it rather than
   absorb it.
2. **This is not a failure of the Agent Foundation work.** 0 of the 21 errors lie
   in files it touches.

---

## 13. Recommendation

```text
The ordered merge of PR #40–#44 may proceed on its merits, but NOT on this
check's authority.
```

Every other gate is green for all five PRs — Python 3.11 quality and tests,
Repository structure guard, Studio contracts, `test`. The temporal-texture check
should be treated as **known-broken and non-blocking** until the §11 sequence is
done, and that decision should be recorded so it is a deliberate exemption rather
than a silently ignored red badge.

**Alternatively, if this check is meant to be a real gate, merge should wait** for
the baseline decision — because the first PR to merge will make the situation
invisible again, and `main` will still have no baseline.

That trade-off is the human's to make. What is not acceptable is proceeding while
believing the red state means something about these PRs. It does not.

---

## 14. Core Principle

> **Never make a red check green by teaching it to stop seeing the truth.**

Equally:

> **A baseline is evidence, not permission.**

The evidence in this audit is that the gate stopped telling the truth weeks ago —
not that the repository is innocent, and not that the five branches are guilty.
