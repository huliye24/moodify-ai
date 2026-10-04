# CI_HOTFIX_003 — Temporal Texture Guard Repair (D4 executed)

> **Task:** execute decision D4 from CI_HOTFIX_002 — repair the guard and regenerate the baseline
> **Branch:** `ci/temporal-texture-repair`
> **Base:** `origin/main` = `1dd5b2e14cdc67e673c26a2aa62e556c12066b20`
> **Commits:** `84c062d9` (repair) · `ec8aba2e` (baseline)
> **Authorised by:** owner approval of `REALIGNMENT_BOUNDARY_APPROVED` + "先做 D4"

---

## 1. Summary

**The gate is green for the first time in about seven weeks.**

```text
before   {"new": 213, "new_errors": 21, "resolved": 192}   exit 1
after    {"new":   0, "new_errors":  0, "resolved":   0}   exit 0
```

Two defects were repaired, not one. The second was found while fixing the first
and is the more serious of the two.

| | Defect | Symptom | Severity |
| --- | --- | --- | --- |
| 1 | Fingerprint keyed on **line number** (5 of 10 rules) | Any edit above a finding re-keyed it → the guard reported `resolved + new` for edits that changed nothing | **Noisy** |
| 2 | `symbol` was the **bare function name** | Repeated definitions collapsed to one fingerprint; `finding_map` is a plain dict, so all but one were **silently dropped** | **Quiet** |

The line-number defect was why the gate churned. The symbol defect is why it was
occasionally **wrong**, including for rules that were never line-keyed.

---

## 2. Defect 1 — positional identity

Five rules put the line number into the fingerprint's `message_key`
(`line-length:{n}`, `debt:{marker}:{n}`, `broad-exception:{lineno}`,
`empty-exception:{lineno}`, `empty-catch:{n}`), defeating the fingerprint
function, whose signature has no line parameter.

Measured, not inferred:

```text
insert one comment line above a TT-LINE-LENGTH finding
  415b86bd2ba4df922b63  ->  gone, re-keyed as 610ad6a298847a2861f8 at line +1
```

**Why the line number was there:** `finding_map` returns `{fingerprint: item}`, so
the key must be unique. **148 (rule, path, symbol) combinations hold more than one
finding** — a discriminator is genuinely required.

**Replacement:** a discriminator derived from the finding's **content**, with an
occurrence ordinal for identical content in one scope:

```python
digest = sha256(content)[:12]
occurrence = seen.get(digest, 0); seen[digest] = occurrence + 1
return digest if occurrence == 0 else f"{digest}:{occurrence}"
```

Content identifies a finding. Position does not. The ordinal keeps the key unique
when the same handler appears twice in one function.

**Post-fix behaviour, same experiment:**

```text
new=0  resolved=0
10 findings kept their fingerprint with the line number moved
```

---

## 3. Defect 2 — colliding symbols

`symbol = node.name` used the bare name. `evaluation/judges.py` declares a nested
`evaluate` method **four times**, once per judge class:

```text
BEFORE
  TT-PARAMETERS       judges.py:evaluate  ->  4 findings, all fingerprint 3dfa84f1da75249943ed
  TT-FUNCTION-LENGTH  judges.py:evaluate  ->  2 findings, both fingerprint c02cfe320069d0cb3e1c
```

`finding_map` collapsed each group to one entry, so **4 findings were invisible to
the guard**. These are stable-keyed rules, so this defect is independent of
Defect 1 — fixing only the line numbers would have left it in place, and a
baseline regenerated without fixing it would have enshrined the loss.

**Replacement:** scope-qualified symbols (`Alpha.run` vs `Beta.run`), via a
one-pass walk that tracks class and function nesting.

```text
AFTER
  TT-PARAMETERS       LLMJudge.evaluate              fp=6766f0e309af67
  TT-FUNCTION-LENGTH  AcousticJudge.evaluate         fp=134ff596241795
  TT-PARAMETERS       AcousticJudge.evaluate         fp=e1529d74d25cdf
  ...                                                (7 distinct findings, was 2)
```

### Collision counts, same tree, same 1443 findings

```text
ORIGINAL tool   1443 findings   1439 unique   4 INVISIBLE
FIXED    tool   1443 findings   1443 unique   0 INVISIBLE
```

**The finding population is unchanged.** Only identity changed — which is what
makes the regenerated baseline a re-keying rather than a re-measurement.

---

## 4. Baseline regeneration

```text
source commit   84c062d981e367b68180a308940b66f6576fc126
generated from  a clean tree at that commit, not hand-edited

python tools/temporal_texture/temporal_texture_audit.py --repo . \
  --config .moodify/temporal_texture.toml --out artifacts/temporal_texture/current
cp artifacts/temporal_texture/current/report.json .moodify/tt_baseline/report.json
```

**Why the diff is large and why that is expected:** every fingerprint for the five
line-keyed rules changed, and every Python finding changed because symbols are now
qualified. That is 1443 re-keyed entries against a 1443-entry population.

**What this ratifies, stated rather than left implicit in a binary diff:** 109
error-level, 771 warning and 563 info findings as the accepted state of `main`.
The guard fails only on *new* errors, so these become the accepted floor. This is
the decision escalated as D4 and approved by the owner.

**Determinism**, checked rather than asserted:

```text
findings array, two runs         byte-identical        <- the only part the guard reads
generated_at                     differs (timestamp, by design)
repository                       machine-local path    <- pre-existing; not guard-relevant
```

---

## 5. Verification — every branch, corrected guard

Run with the repaired tool and the new baseline:

| Branch | Result | Reading |
| --- | --- | --- |
| `origin/main` | `new=0 errors=0 resolved=0` **PASS** | main is the reference |
| `hotfix-000-measurement-correctness` | `0 / 0 / 0` **PASS** | already in main |
| `code-quality/empty-exception-policy-001` | `new=5, errors=0, resolved=62` **PASS** | see below |
| `ecosystem-001-capability-map` | `new=0, errors=0, resolved=12` **PASS** | docs-only |
| `ecosystem-002-capability-registry` | `new=3, errors=0` **PASS** | registry |
| `ecosystem-003-provider-router` | `new=7, errors=0` **PASS** | router |
| `project-model-001` | `new=1, errors=0` **PASS** | project model |

```text
ZERO new errors on every branch.
```

**The numbers are self-consistent**, which is the best evidence the repair works:
`code-quality` resolves **62**, not the 42 it fixed — because `except Exception: pass`
tripped **both** the empty-exception *and* the broad-exception rules, and one fix
retires both. Under the old scheme that same branch produced churn in the hundreds.

This is precisely the §15 property the triage asked for: *feature branches only
fail for actual new regressions.* Every branch now passes, including the ones
adding new code, because none of them adds an error-level finding.

---

## 6. Tests

`tests/temporal_texture/test_guard_contract.py` — **12 tests**, in a directory the
tool's own config already reserved (`exclude_globs: tests/temporal_texture/**`)
but which never existed. CI already runs it: `pytest -q tests ../tests`.

**Two were verified to FAIL against the previous implementation**, by swapping the
original tool back in:

```text
FIXED    tool   12 passed
ORIGINAL tool    2 failed  <- test_inserting_a_line_above_a_finding_does_not_rekey_it
                              test_identical_symbols_in_different_scopes_do_not_collide
RESTORED        12 passed
```

### A vacuous test, caught and corrected

The first version of the line-shift test called `scan_python` for a line-length
finding. Line length is a **textual** rule, so it returned `[]` and the test
asserted `[] == []` — **it passed against both implementations**. It looked like
coverage and was worth nothing. The test now calls `scan_textual` and asserts the
fixture is non-empty. Reported here because the failure mode was invisible in the
test's own output, and only the attempt to prove it bites exposed it.

---

## 7. Gates

```text
python -m pytest tests/temporal_texture/ -q     12 passed
python -m ruff check <changed>                  All checks passed
python scripts/check_repo_structure.py          OK (1543 tracked files, 6 checks)
```

---

## 8. What was NOT done

**D5 (add `push: branches: [main]`) is deliberately not included.** The triage
listed it as `DEFER_WITH_OWNER` and said it must land *after* D4; D4 alone was
approved. The recommendation now stands for the first time without a caveat — a
green gate on main is worth reporting on main.

Also untouched: the 67 remaining error findings in G2–G6, and the repository
structure guard's file count falling 1557 → 1543 (main's untracking of generated
core outputs, unrelated).

---

## 9. Core Principle

> **A gate that cannot tell a change from a shuffle is not a gate.**

It can now. `new=0` on main means something, and a PR that shows a new error will
be showing one.
