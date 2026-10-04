# PRODUCT_REALIGNMENT_001 — Reality Audit Verification

> **Document type:** verification of the reality audit's claims against the repository.
> **Date:** 2026-10-04
> **Base:** `origin/main` = `1dd5b2e14cdc67e673c26a2aa62e556c12066b20`
> **Runtime authority changed:** NO · **Product code changed:** NO · **Canon changed:** NO
> **Status:** HUMAN REVIEW REQUIRED — see §7

---

## 1. Why this document exists

A **reality audit** is only worth what its claims are worth. This repository has
repeatedly shipped documents containing unverified statements:

```text
auditory/inventory.py        names six modules that do not exist
structure.py                 declares tempo_bpm with no producer anywhere
loudness.py docstring        claims "error < 0.1 LU" that was never measured
(a check I ran myself)       reported two packages "importable" that were
                             empty namespace packages built from stale __pycache__
```

So the audit's claims were checked one by one before treating it as a basis for
migration. **Nothing below changes the audit's substance; it establishes whether
the substance is true.**

---

## 2. Verification results — claims that HELD

Every load-bearing factual claim was checked. **None could be falsified.**

### 2.1 §1.2 "already exists"

| Claimed | Verified as |
| --- | --- |
| source import | `auditory/decode.py`, `audio_io.py` |
| audio analysis | `auditory/metrics.py` (+ `loudness.py`, `true_peak.py`, `stereo.py`) |
| diagnosis projection | `diagnosis/` (7 modules) |
| evidence / provenance | `contracts/provenance.py`, `auditory/evidence/` (7 modules) |
| preview separation | `stems/` + `moodify-desktop/scripts/dsp_separate.py` |
| MIDI artifact | `moodify-desktop/src/main.js` basic-pitch path |
| MusicXML / score artifact | `moodify-desktop/scripts/midi_to_musicxml.py` |
| A/B related work | `ab_compare.py`, `evaluation/`, `listening/` |
| Mix Graph | `mix_graph/` |
| finishing presets | `v01_presets.py` |
| CLI | `cli.py`, `release_cli.py` |
| node / queue / jobs | `node/`, `reconstruction_job/` |
| Desktop Studio | `moodify-desktop/src/{pipeline,main,studio}.js` |

### 2.2 §3 duplicate-authority risks — the three checkable ones are real

**Risk A — Desktop pipeline owns stage derivation and gates. CONFIRMED.**

```text
moodify-desktop/src/pipeline.js:63   const STAGES = Object.freeze([...])
moodify-desktop/src/pipeline.js:78   Object.fromEntries(STAGES.map((s, i) => [s, i]))
moodify-desktop/src/pipeline.js:169  /** Boolean checklist behind the stages —
                                          the thing the UI gates on. */
moodify-desktop/src/pipeline.js:182  // hard gate for the canonical route
moodify-desktop/src/pipeline.js:24   ANALYZED + DIAGNOSED + SEPARATED + MIDI
                                     = READY_FOR_DEEP_PLAN
```

The desktop shell genuinely holds gate semantics that a Core Production Graph
would also hold. **"Desktop says READY / Core says NOT_READY" is a real
possibility, not a hypothetical.**

**Risk C — two diagnosis surfaces. CONFIRMED.**

```text
moodify/diagnosis/   engine.py · health_scorer.py · defect_classifier.py
                     quality_gate.py · preprocessing.py · metrics.py
moodify/auditory/    reports.py · judgment.py  (report + findings projection)
```

Both can claim to be "what is wrong with this audio". The audit's ruling — do not
add a third — is correct, and the two that exist are already one too many.

**Risk E — job state is independent of production state. CONFIRMED.**

```text
node/models.py:9   class JobStatus(StrEnum): SUCCEEDED / FAILED ...
```

`job SUCCEEDED ≠ project VERIFIED` is a live distinction, not a caution.

### 2.3 §4.2 Project Model layout — matches the implementation exactly

The audit lists:

```text
project.json
source/ analysis/ stems/ transcription/ score/ edits/
session/ renders/ verification/ exports/ provenance/
```

`codex/project-model-001` creates `source/` plus exactly ten reserved
directories:

```text
PROJECT_DIRECTORIES = (stems, analysis, transcription, score, edits,
                       session, renders, verification, exports, provenance)
```

**One-for-one match.** The audit's description of Project Model 0.1 is accurate.

### 2.4 §5 / §6 capability status — consistent with the registry

Every capability the audit lists under §5 appears in the Capability Registry
(ECOSYSTEM 002), and every one it lists under §6 as TARGET/ABSENT/PARTIAL is
either absent there or declared non-canonical:

```text
§5  audio.decode CANONICAL · audio.analyze CANONICAL · audio.verify CANONICAL
    stem.separate EXPERIMENTAL · midi.transcribe IMPLEMENTED_NOT_CANONICAL
    score.generate IMPLEMENTED_NOT_CANONICAL · clipping.repair
    IMPLEMENTED_NOT_CANONICAL · mix.render EXPERIMENTAL · master.render
    EXPERIMENTAL · delivery.export IMPLEMENTED_NOT_CANONICAL

§6  structure.analyze PARTIAL · harmony.analyze ABSENT · lyrics.align ABSENT
    instrument.identify ABSENT · pitch.correct ABSENT · timing.correct ABSENT
    noise.reduce ABSENT
```

The audit's own caveat — *"存在代码 ≠ canonical capability 已完成"* — is the
right frame, and the registry's status vocabulary already encodes it.

### 2.5 §7 canon file list — all nine paths exist

`AGENTS.md` · `docs/canon/{CURRENT_CANON,PRODUCT_DEFINITION_V3,PRODUCT_BOUNDARY,
AUTHORITY_ORDER,CURRENT_ARCHITECTURE,STUDIO_PRODUCTION_PIPELINE_V3,
CANON_CHANGELOG}.md` · `docs/REPOSITORY_STATUS.md` · `docs/protocol/` — all present.

### 2.6 §11 PR sequence — conflict with the existing stack

The proposed `PR 1 = this audit + canon alignment` and `PR 2 = Project Model v0.1
compatibility` **both presuppose queued work**. At the time of this verification:

```text
#40 HOTFIX 000                     MERGED
#41 ECOSYSTEM 001 (docs)           OPEN
#42 ECOSYSTEM 002 (registry)       OPEN
#43 ECOSYSTEM 003 (router)         OPEN — base is #42, stacked
#44 TASK 001 Project Model 0.1     OPEN
#38 Desktop release 001            MERGED
```

**§11 PR 2 cannot be built until #44 merges**, and `docs/ecosystem/` is still
incomplete until #41–#43 land. The sequence is sound but is not startable at
step 1 as written.

---

## 3. What the audit does NOT account for

These are additions, not corrections. The audit is silent on them and they bear
on whether the migration is startable.

### 3.1 The CI gate is currently broken, and the plan assumes it is not

§11 proposes a multi-PR sequence with parity tests (§8 Phase A). But
`moodify-temporal-texture` — the one check that guards structural quality —
**fails on `main` itself**, has never run on `main`, and keys five of its rules on
line numbers (CI_HOTFIX_001, CI_HOTFIX_002). Two of its 109 error findings were
proven to be re-keying artifacts.

`REALIGNMENT → parity tests → PR sequence` rests on a gate that currently cannot
distinguish a regression from a line shift. **D4 in the triage (repair the guard,
then regenerate the baseline from a recorded commit) is a prerequisite, not a
parallel track.**

### 3.2 Five capability layers are unmerged, and PR 2 depends on them

The audit treats "Project Model" and "Capability Registry" as available
foundations. At this base they are open PRs. Verified directly:

```text
moodify.capabilities   NOT PRESENT on this branch   (PR #42 open)
moodify.project        NOT PRESENT on this branch   (PR #44 open)
```

### 3.3 Only one of the seven human decisions is genuinely blocking

The audit lists D1–D7. Mapped against the repository's actual state:

```text
D1 Project schema freeze        already answered in practice by TASK 001
D2 Production Graph protocol    correctly deferred (read model first)
D3 First edit/repair capability — depends on the registry existing at all
D4 Mastering-grade separation   correctly deferred (licence/quality/runtime)
D5 Quick vs Deep default        product-experience call, not an architecture gate
D6 Publish ≠ Accept             policy, does not gate Phase A
D7 Cloud boundary               — this is the one that gates everything
```

**D7 is the load-bearing decision.** A, B and C in §13 are the same decision stated
three ways, and everything in §8 Phase B onward depends on it.

---

## 4. Files Changed

```text
A  docs/reports/PRODUCT_REALIGNMENT_001_REALITY_AUDIT.md
```

No canon file was updated. §7 lists nine authority surfaces for alignment, but
§13 says the next step requires human confirmation first — so aligning canon
before the boundary is approved would spend that work on an unratified direction.

---

## 5. Side Effects

```text
CANON_CHANGED           = NO
RUNTIME_AUTHORITY       = unchanged
PRODUCT_CODE_CHANGED    = NO
BASELINE_CHANGED        = NO
CI_CHANGED              = NO
```

No file under `moodify-core-package/`, `moodify-desktop/`, `ops/`, `.moodify/`
or `.github/` was touched.

---

## 6. Verification method

Every claim above was checked against the working tree at
`1dd5b2e14cdc67e673c26a2aa62e556c12066b20` by direct file inspection, not by
reading other documents. Where a check was mine and wrong, it is reported as
such: an early desktop-file check used a bad relative path and reported five
existing files "MISSING"; a Project-layout comparison script had a regex bug.
Both were corrected and the corrected results are what appear above.

---

## 7. Review Decision

The audit's three conditions remain the gate:

```text
A. Core 是唯一生产语义 authority
B. Cloud 是基础设施，不定义第二套产品状态
C. Existing Desktop pipeline 作为 reference semantics 迁移，
   而不是继续扩张为长期 authority
```

Confirm all three →

```text
REALIGNMENT_BOUNDARY_APPROVED
```

otherwise

```text
STOP
```

**Recommendation:** approve A/B/C, and insert one prerequisite before §11's PR 2:
repair the temporal-texture guard and regenerate its baseline (triage decisions D4),
because the parity testing this plan depends on cannot currently be trusted to
report a regression.

---

## 8. Assessment

> **已有能力已经足够开始闭环，但这些能力还没有被一个统一 authority 串起来。**

**The audit is accurate.** Every claim it makes about what exists, what
duplicates what, and what is missing survived verification. Its two structural
findings — that Desktop and a future Core Graph would both own gate semantics, and
that two diagnosis surfaces already coexist — are real and checkable in the tree
today.

What it understates is the **dependency floor**: the migration cannot start at its
own step 1. Three of the foundations it assumes are unmerged PRs, and the quality
gate it would rely on for parity testing is red on `main` for reasons that have
nothing to do with this realignment.
