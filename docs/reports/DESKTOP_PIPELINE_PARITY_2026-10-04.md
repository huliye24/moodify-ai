# Desktop Pipeline Parity — 2026-10-04

> **Task:** realignment implementation order, step 3 — freeze current pipeline behaviour
> **Branch:** `desktop/pipeline-parity-tests`
> **Base:** `origin/main` = `f5bf8255`
> **Scope:** desktop only. No Core change, no gate change, no behaviour change.

---

## 1. Result

**The tests had largely been written already. The gap was somewhere else.**

```text
test-pipeline.js       33 checks   covers all seven freeze items      ALREADY EXISTED
test-pipeline-parity.js 8 checks   the authority vs its one mirror    ← ADDED
```

Added: `moodify-desktop/scripts/test-pipeline-parity.js` (8 checks), wired into
`npm test`.

---

## 2. The seven freeze items, audited against what existed

| # | Item to freeze | Existing coverage |
| --- | --- | --- |
| 1 | stage derivation | §1 `ANALYZED` / `IMPORTED` / *"deleting artifacts moves it backwards"*; plus *"recording a stage does not become an authority"* |
| 2 | Deep / Quick two paths | §6 cases 2, 6, 11, 12 — `mode` resolves `DEEP` / `FAST_STEREO_ONLY` |
| 3 | plan requires stems **and** MIDI | §6 cases 3, 4, 5, 6 — including *stems without MIDI*, *MIDI without stems*, and **MusicXML explicitly rejected as a substitute** |
| 4 | finish requires a plan artifact | §6 cases 9, 10 |
| 5 | Quick requires explicit opt-in | case 2 (offered, not applied), case 11 (applied only on opt-in), plus the opt-in is an **attributable artifact** with a timestamp |
| 6 | diagnosis projects Core facts only | §2 — *"copies Core values verbatim, never re-derives them"*; every evidence pointer must resolve **and land on the finding it came from** |
| 7 | `issues: []` stated honestly | §2 — empty issues must not be invented, and `finding_rule_coverage.note` must carry the *"no finding ≠ audio is fine"* caveat |

**All seven were already pinned.** Writing them again would have produced a
second copy of an existing test — the exact failure mode this session kept
finding elsewhere.

---

## 3. The gap: the gate had two implementations and one was untested

`renderer/app.js:2706` says it in its own docstring:

```js
/**
 * Which stages the current case may enter. Mirrors src/pipeline.js gates().
 */
```

Verified rather than taken on trust:

| | |
| --- | --- |
| `src/pipeline.js` | `gates()` — `canPlan: deepReady`, where `deepReady = analyzed + diagnosed + separated + structured` |
| `renderer/app.js` | `stageUnlocked()` maps stage → gate field; `stageLockReason()` **restates the rule** as UI copy (`if (!f.structured) missing.push('④ 结构（MIDI）')`) |

The 33 existing checks pin the authority and never look at the mirror. **Change
the rule in `pipeline.js` and the renderer's copy drifts silently** — and the
renderer copy is the one a human reads when a stage refuses to open.

This is realignment Risk A made concrete. It matters right now because the
migration **deletes this mirror**; freezing the two together first is what makes
that deletion safe rather than hopeful.

---

## 4. What the new test does

It compares **behaviour, not text**. A string comparison would pass if both sides
drifted together.

```text
authority side   build a fully deep-ready case, remove one fact's artifact
                 at a time, record which removals flip canPlan to false
                 -> the prerequisites pipeline.js actually enforces

mirror side      extract the fact names stageLockReason() names for ⑤
                 -> the prerequisites the renderer claims
                 assert the two sets are equal
```

Also pinned:

```text
the renderer consumes gates rather than deriving them
    (no require(), no fs.* — a browser script cannot re-derive state by accident)
⑥ is not among the ⑤ prerequisites
a persisted plan is what opens ⑥, on top of deep readiness
stageUnlocked maps ⑤/⑥ onto gates.canPlan and gates.canFinish || gates.canFinishQuick
the Quick route cannot reach ⑤ in either implementation
mode labels are 深度完成 / 快速（仅立体声）
```

Two checks guard the test itself against going vacuous: it asserts the authority
really does require all four facts, so the parity comparison cannot pass with
both sides empty.

---

## 5. Proof that it bites

Passing is not proof. The mirror was deliberately broken and restored:

```text
remove ④ 结构（MIDI） from the renderer's ⑤ lock reason
  FAIL ⑤ prerequisites: renderer list == what pipeline.js actually enforces
       — renderer says ⑤ needs [analyzed,diagnosed,separated]
         but pipeline.js enforces [analyzed,diagnosed,separated,structured]
  7 passed, 1 failed        exit 1
restore
  8 passed, 0 failed        exit 0
```

The failure names the drift precisely enough to act on without reading either
file.

The test also fails loudly if `stageLockReason()` disappears rather than skipping:
if the mirror moves, that must be noticed, not silently unmonitored.

---

## 6. Gates

```text
check-contracts          exit 0
test-pipeline            33 passed, 0 failed
test-pipeline-parity      8 passed, 0 failed     ← new
test-studio              21 passed, 0 failed
test-runtime             all runtime checks passed
repo structure guard     OK (1545 tracked files, 6 checks)
```

---

## 7. Files changed

```text
M  moodify-desktop/package.json                        (wire the new test into npm test)
A  moodify-desktop/scripts/test-pipeline-parity.js     (8 checks)
A  docs/reports/DESKTOP_PIPELINE_PARITY_2026-10-04.md  (this report)
```

**No behaviour changed.** `pipeline.js` and `renderer/app.js` are untouched —
this step freezes what they currently do; it does not alter it.

---

## 8. What this unblocks, and what it does not

**Unblocks:** step 4 (the Core Project Adapter). The shell's behaviour is now
pinned by 41 checks across two files, so a migration that changes it will fail
loudly rather than quietly.

**Does not do:** the mirror is still there and still a second copy. Freezing it is
not fixing it. Deleting `stageLockReason`'s duplicated rule is the adapter step's
job — and this test is what will tell whoever does it whether the Coreside
behaviour matches.

**Still open, unchanged by this step:** the merge order (#41 → #42 → #43 → #44),
D5, and the 67 baselined error findings.
