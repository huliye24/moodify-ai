# MIP-0002 — Stem Tuning Loop (逐轨修音闭环)

```yaml
mip: 0002
title: Stem Tuning Loop — per-stem pitch/timing correction and mixing, rendered as paired tiers
author: huliye24
status: DRAFT
type: Core-Contract
created: 2026-10-04
updated: 2026-10-04 (Addendum A — FAST_STEREO_ONLY pair contract, EXPERIMENTAL reference implementation)
requires: none
supersedes: none
```

---

## Abstract

Adds a Core capability that takes a decomposed song (stems + MIDI) and produces **one complete
rendering per parameter tier**, where a tier is a full pass of (a) per-stem pitch / timing
correction referenced to MIDI and (b) per-stem mixing processing. Two tiers — `conservative`
and `aggressive` — are rendered as a pair so a human can A/B them, and each rendering carries
evidence (`before` / `after` / `deltas` / `invariants` / `peak_gate`) consistent with the
existing `finishing` evidence shape. This adds a new Core contract surface (`tuning`) and a new
artifact family under the Studio case; it does not modify the existing `finishing` or
`protocol process` contracts.

Affected: Core (new capability), CLI (`moodify tuning`), Studio (`moodify-desktop`, the caller),
the Review Network (new perceptual claims to review). Not affected: `protocol` wire formats,
existing cases, existing presets.

---

## Motivation

Today a case can be analysed, diagnosed, separated and structured, and then processed — but
**the processing targets the original stereo master, not the stems**. In `moodify-desktop`,
both `finishing:run` and `studio:process` resolve their input through `resolveCaseSource()`
(`src/main.js:650`, `:1011`), so the separated stems produced at stage ③ are never an input to
any processing chain. Their only uses in the whole shell are counting files to derive a stage
(`src/pipeline.js:108`) and being allowed as an input to audio-to-MIDI (`src/main.js:601`).

Three things therefore stay impossible:

1. **Correcting a tone in the part that is out of tune.** Pitch and timing problems are
   per-instrument facts. Applying a whole-mix chain cannot fix a flat vocal without also
   processing everything else.
2. **Using the recovered structure.** Stage ④ recovers MIDI precisely so that pitch and timing
   have a reference. Nothing consumes it.
3. **Comparing two corrections rather than "processed vs unprocessed".** The current A/B in the
   shell is defined as original-vs-product (`src/main.js:712`, `:785`), so it can only answer
   "did anything happen", never "which of these two corrections is better".

Who is affected: the Creator-side user, who currently has no way to act on a per-part problem;
and the Review Network, because a per-stem correction makes new, finer perceptual claims that
must be reviewable.

**Cost of doing nothing.** The Studio flow accumulates a decomposition (stems + MIDI) that no
stage consumes, and the pipeline's advertised last steps — "tune", "verify" — remain
unimplementable. The `VERIFIED` stage in `src/pipeline.js` already has no writer anywhere in the
repository, i.e. the flow currently claims a stage it cannot reach.

---

## Specification

### New CLI surface

```text
moodify tuning plan   --stems <dir> --midi <file> --tier conservative|aggressive
                      --out <plan.json>
moodify tuning render <plan.json> --output-dir <dir>

<dir>/<stem>__tuning.wav        per-stem tuned result
<dir>/mix.wav                   sum of the tuned stems
<dir>/mix.evidence.json         before / after / deltas / invariants / peak_gate / nodes
```

### Tier descriptor (exact fields)

```json
{
  "schema": "moodify.core.tuning-tier/0.1",
  "tier": "conservative",
  "calibration_status": "UNCALIBRATED_ENGINEERING_DEFAULT",
  "pitch_correction": { "max_cents": 0, "reference": "midi", "preserve_vibrato": true },
  "timing_correction": { "max_ms": 0, "reference": "midi", "preserve_groove": true },
  "mix": { "per_stem": { "<stem_name>": { "<operator>": { "<param>": 0 } } } }
}
```

- `tier` ∈ `{conservative, aggressive}`. Two tiers only; the set is closed in this MIP.
- `calibration_status` is **required**. It must be `UNCALIBRATED_ENGINEERING_DEFAULT` until a
  calibration artifact justifies otherwise. It travels with the artifact so no consumer can read
  an engineering default as a validated limit.
- Both tiers must declare their own values. A tier may not be derived from the other by an
  undocumented scale factor.

### Observable behavioral difference

For a case with ≥1 non-empty stem directory and ≥1 MIDI file, `tuning plan` + `tuning render`
for both tiers must produce, in the output directory, one `<stem>__tuning.wav` per input stem,
one `mix.wav`, and one `mix.evidence.json` **per tier**. Invariants that must hold and must be
recorded in the evidence:

```text
duration preserved           |Δduration| == 0
sample rate preserved        equal
channel count preserved      equal
output finite                no NaN / Inf
peak gate                    within the documented limit
```

The evidence must reference the graph it executed (`graph_digest_sha256`) and the output
(`output.sha256`), matching the existing `finishing` evidence contract so one reader handles both.

### Studio-side artifacts (caller contract, for cross-interface consistency)

```text
<case>/studio/tuning/<pair_id>/
    pair.json        { pair_id, source, midi, stems, tiers:{A:"conservative",B:"aggressive"}, created_at }
    A/  plan.json  stems/*.wav  mix.wav  evidence.json  analysis/report.json
    B/  plan.json  stems/*.wav  mix.wav  evidence.json  analysis/report.json
    recheck.json     three-way metric alignment vs the original report
```

`pair.json` must record which tier each side is; a pair whose sides differ in anything but the
tier is invalid.

### One Core

Per `AGENTS.md` ("一个 Core，多个 Interface"), this capability must be reachable from Core by any
interface. No pitch/timing/mixing logic may live in `moodify-desktop` or in any app. The shell
calls Core and copies nothing.

---

## Rationale

**Why two tiers and not human-edited parameters.** The human decision on 2026-10-04 was
"系统出两档参数" — the system proposes, the human chooses by listening. Editing parameters per
stem is a mixing-engineer task and would make the first version's UI a parameter editor, which
`docs/canon/TECHNOLOGY_PRINCIPLES.md` pushes against (`existing > … > custom`; and the product
strategy is 可商用 > 技术先进). Two fixed tiers keep the human action at the decision level.

**Why a closed set of two tiers.** An open tier set invites tier proliferation and makes
"which tier is better" unanswerable. Two is the minimum that makes A/B meaningful.

**Why per-stem processing extends `mix_graph` instead of a new engine.** A second DSP path would
violate the technical constitution. The existing `finishing` chain already provides EQ, dynamics,
loudness and stereo operators; what is missing is applying them per stem. Considered and rejected:
a separate "tuning engine" — it would be the `CLI DSP Engine vs App DSP Engine` failure mode one
level down.

**Why pitch/timing correction references MIDI and does not claim reconstruction.** MIDI is
recovered approximately (V3 §6: audio evidence > stem audio > measured features > MIDI
interpretation). Correcting "toward" the reference is defensible; claiming the original
performance was reconstructed is not.

**Alternative considered: correct the whole mix.** Cheapest, but cannot fix one flat part without
touching everything — it fails the motivating problem.

**Alternative considered: correct stems but keep a single rendering.** Cheaper, but it removes
the A/B the human asked for, and leaves no way to compare two corrections.

---

## Backwards compatibility

- New CLI subcommand group. No existing verb changes behaviour. **Not breaking** for existing
  jobs, cases, or schema consumers.
- New artifact family under `<case>/studio/tuning/`. Cases that never call `tuning` are
  unaffected; the Studio stage model simply never reaches `TUNED`.
- New evidence artifact reuses the `finishing` evidence fields, so a reader built for finishing
  evidence needs no change; it must tolerate the additional per-stem entries.
- Protocol version: **no bump**. This is a Core capability, not a wire-format change.
- Rollback: remove the subcommand and the `tuning/` subtree; no migration needed because no
  existing artifact references it.

---

## Evidence

**Not yet produced.** This MIP is `DRAFT` and cannot reach `ACCEPTED` without the table below
filled in with real measurements.

| What was measured | How | Result | Where the artifact lives |
|---|---|---|---|
| pitch deviation before/after, per stem | to be run | — | `docs/evidence/…` |
| timing deviation before/after, per stem | to be run | — | `docs/evidence/…` |
| invariant preservation (duration / SR / channels / peak) | to be run | — | `docs/evidence/…` |
| human A/B preference, conservative vs aggressive, blind | to be run | — | `docs/evidence/…` |

Required per run: `source hash · core version · tier descriptor · graph digest · before metrics ·
after metrics · A/B result · human review · agent version · timestamp`.

**Expected to be partially negative and must be reported as such.** The input stems come from
`dsp_center_hpss` (`moodify-desktop/scripts/dsp_separate.py`), which is a preview-grade separator
with vocal bleed and artefacts (V3 §5). Pitch/timing correction applied to preview-grade stems
may make some material **worse**. If so, that must be recorded, not suppressed (see `ME-002`).
It is plausible that this MIP's honest conclusion is "correcting preview stems is not
worthwhile until a master-grade separator exists" — that is a valid decision basis.

---

## Human review

Every perceptual claim here is human-scoped:

- **"Aggressive is better than conservative."** Requires blind listening review. The machine may
  compute deltas; it may not declare a winner.
- **Which tier's values are right.** The parameter values themselves are a "what sounds better"
  judgement, reserved to humans by `AGENTS.md`. Until reviewed, the tier descriptor must carry
  `UNCALIBRATED_ENGINEERING_DEFAULT`.
- **Preservation claims.** Whether a correction preserved groove or vibrato is perceptual.

Out-of-scope, insufficient-evidence, or uncertain cases must produce `HUMAN_REQUIRED` or
`INCONCLUSIVE` — not be resolved by suppressing the escalation.

---

## Reference implementation

None yet for the deep path. `status: DRAFT`. `IMPLEMENTED` requires a Core implementation passing
the test plan below, plus the shell wiring described in the Specification.

**Addendum A (FAST_STEREO_ONLY) has an EXPERIMENTAL reference implementation**: `moodify/tuning.py`
in `moodify-core-package` plus the `moodify tuning render-pair` CLI command, with tests in
`moodify-core-package/tests/test_tuning_pairs.py` and the Studio-side integration in
`moodify-desktop/scripts/test-main-ipc.js`. That implementation **does not** implement per-stem
pitch/timing correction, so it does not satisfy this MIP's main specification and must not be read
as `IMPLEMENTED`. Its tier parameter values are `UNCALIBRATED_ENGINEERING_DEFAULT`.

---

## Test plan

```bash
# 1. tiers are a closed set and each is self-describing
moodify tuning plan --stems <case>/stems --midi <case>/midi/<f>.mid \
  --tier conservative --out /tmp/cons.json
moodify tuning plan --stems <case>/stems --midi <case>/midi/<f>.mid \
  --tier aggressive --out /tmp/aggr.json
python -c "import json;d=json.load(open('/tmp/cons.json'));assert d['calibration_status']=='UNCALIBRATED_ENGINEERING_DEFAULT'"
python -c "import json;a=json.load(open('/tmp/cons.json'));b=json.load(open('/tmp/aggr.json'));assert a!=b and a['tier']!=b['tier']"

# 2. render produces one tuned stem per input stem, plus mix + evidence, per tier
moodify tuning render /tmp/cons.json --output-dir /tmp/out_cons
test -f /tmp/out_cons/mix.wav && test -f /tmp/out_cons/mix.evidence.json
ls /tmp/out_cons/*__tuning.wav | wc -l   # == number of input stems

# 3. invariants actually held (not merely asserted in prose)
python -c "import json;e=json.load(open('/tmp/out_cons/mix.evidence.json'))['verification'];assert e['invariants']['length_preserved'] is True;assert e['peak_gate']['passed'] is True"

# 4. a missing MIDI must not silently produce a rendering
moodify tuning plan --stems <case>/stems --midi /nonexistent.mid --tier conservative \
  --out /tmp/x.json ; test $? -ne 0
```

Addendum A (FAST_STEREO_ONLY) reference implementation:

```bash
# 5. one call renders one complete pair (no stems, no MIDI)
moodify tuning render-pair --mode fast-stereo-only \
  --source <case>/source.wav --output-dir /tmp/pair --pair-id tune_test_0001
test -f /tmp/pair/pair.json
test -f /tmp/pair/A/mix.wav && test -f /tmp/pair/B/mix.wav
test -f /tmp/pair/A/evidence.json && test -f /tmp/pair/B/evidence.json
test -f /tmp/pair/A/tuned/source.wav && test -f /tmp/pair/B/tuned/source.wav
python -c "import json;a=json.load(open('/tmp/pair/A/evidence.json'));b=json.load(open('/tmp/pair/B/evidence.json'));assert a['output_sha256']!=b['output_sha256'];assert a['checks']['peak_gate']['passed'] is True"

# 6. an existing pair directory is never overwritten
moodify tuning render-pair --mode fast-stereo-only \
  --source <case>/source.wav --output-dir /tmp/pair ; test $? -ne 0

# 7. an unknown mode is rejected before any rendering
moodify tuning render-pair --mode deep --source <case>/source.wav \
  --output-dir /tmp/other ; test $? -ne 0

# 8. both sides are analysed and three-way aligned (Studio: recheck.js)
moodify demo /tmp/pair/A/mix.wav --cases-root /tmp/rc_a --no-open
moodify demo /tmp/pair/B/mix.wav --cases-root /tmp/rc_b --no-open
```

Independent verification additionally requires the repository's own structure check
(`scripts/check_repo_structure.py`) to stay green and the Studio pipeline test
(`moodify-desktop/scripts/test-pipeline.js`) to pass once the shell is wired.

---

## Security and privacy considerations

No credentials, no network, no personal data. The capability reads local audio and MIDI already
present inside a case and writes local artifacts inside the same case. It does not widen any
path-access surface. The shell must continue to guard every case directory through
`resolveGuardedCase()`, and the new artifacts must live inside `<case>/studio/tuning/` so that
existing path guards cover them without modification.

---

## Unresolved questions

1. **What are the actual tier parameter values, and who signs off on them?** This MIP fixes the
   shape of a tier, not its values. The values are a perceptual judgement and need human review.
2. **Is correcting preview-grade stems worthwhile at all?** Depends on evidence that does not
   exist yet (see Evidence). A negative result is an acceptable outcome.
3. **Does the second tier need to be a variant of the first, or may the two tiers differ in
   *which operators* they enable, not only in magnitude?** Currently unfixed.
4. **Where do the tuned stems live relative to the original stems** — replace, sibling directory,
   or versioned tree? The Studio side assumes a versioned tree (`tuning/<pair>/A/stems`), but a
   Core-only consumer may expect otherwise.
5. **How does this interact with the Studio "Quick Finish (stereo only)" path**, which by
   definition has no stems? **Answered for the pair surface by Addendum A** (a second, narrower
   Core call: `tuning render-pair --mode fast-stereo-only`, which needs no stems and no MIDI).
   The deep path's interaction is still open: whether ④修音 for the deep route reuses the same
   `render-pair` entry point with a stem list, or keeps the two-call `plan` + `render` shape.
6. **Does the mixdown belong in Core, or is it the caller's job?** This MIP puts it in Core so
   that CLI and App produce the same `mix.wav`; the alternative keeps Core stateless per stem.

---

## Addendum A — `FAST_STEREO_ONLY` pair contract (Phase 2, 2026-10-04)

**Status of this addendum:** part of this MIP, still `DRAFT`. It defines a **second, narrower Core
contract** that does not need stems or MIDI, so the first real "two complete candidates → recheck →
human choice → export" loop can exist before any per-stem capability does. It is implemented as an
**EXPERIMENTAL reference implementation**; nothing here is calibrated or perceptually validated.

### A.1 Tier vocabulary (normative)

```text
side A / tier id "conservative"   display: A（保守）
side B / tier id "full"           display: B（充分）
```

`aggressive`, used in the pre-addendum draft, names the same concept under an older wording; the
pair contract uses `conservative` / `full` and **`full` must never be described as "better"**, only
as "更充分 / 变化更明显". The closed tier set for this mode is `{conservative, full}`.
No consumer may use `clean_master` / `warm_vocal` / `wide_space` as a tier id, tier label, or
product-facing choice (those retired on 2026-10-04).

### A.2 New CLI surface (normative)

```text
moodify tuning render-pair \
  --mode fast-stereo-only \
  --source <song.wav> \
  --output-dir <pair_dir> \
  [--pair-id <tune_…>]
```

- One invocation renders **one pair**. There is no "render one side" mode.
- `--mode` is a closed set: currently only `fast-stereo-only`. An unknown mode is an error.
- `--source` is the case's own stereo master. Stems and MIDI are **not** inputs; passing them is
  not part of this contract.
- `--output-dir` is the final pair directory. If it already exists (file or directory), the
  command **fails without writing** — repeating the command must produce a *new* pair, never
  overwrite an existing one, and never touch the source audio.
- stdout: exactly one JSON object. Failure: one JSON object on stderr, exit code 2.
  A failure must never be reported as a success with a partial pair.

### A.3 Tier descriptor (normative fields)

```json
{
  "schema": "moodify.core.tuning-tier/0.1",
  "tier": "conservative | full",
  "side": "A | B",
  "mode": "FAST_STEREO_ONLY",
  "calibration_status": "UNCALIBRATED_ENGINEERING_DEFAULT",
  "engine_version": "<core version>",
  "preserve": [],
  "parameters": { "nodes": [ { "id": "...", "type": "...", "parameters": { } } ] }
}
```

- Every value a tier applies must be listed in `parameters.nodes` — "a bit stronger" is not a
  parameter record. The graph actually executed must be derivable from this descriptor alone.
- `preserve` is empty here: nobody has recorded what to protect for this case, and the fast path
  may not claim it protected perceptual features it was never told about.
- `calibration_status` is `UNCALIBRATED_ENGINEERING_DEFAULT` until a calibration artifact says
  otherwise. It travels with the artifact so no consumer can read an engineering default as a
  validated limit.

### A.4 Reference-implementation tier defaults (UNCALIBRATED)

Recorded here so evidence can cite a source; these are engineering defaults awaiting human
calibration (see Unresolved #1), not perceptual findings. All values are inside the existing
`mix_graph` provider ranges.

```text
conservative (A)                       full (B)
  eq  highshelf 10 kHz  +0.5 dB          eq  highshelf 10 kHz  +1.5 dB
                                         eq  peak 250 Hz  -1.0 dB  q 0.7
  comp  thr -14 dB  ratio 1.2            comp  thr -18 dB  ratio 1.5
        attack 35 ms  release 250 ms           attack 25 ms  release 220 ms
  limiter  ceiling -1.0 dB               stereo  width 1.08
           input_gain 0.0 dB             limiter  ceiling -1.0 dB
                                                 input_gain +0.5 dB
```

### A.5 Allowed processing (normative)

Only whole-track `mix_graph` primitives: `eq`, `compressor`, `stereo`, `limiter`, rendered through
the existing `moodify.mix_graph` session (one DSP authority; no new engine). This mode **must not
claim** per-stem processing, pitch correction, timing correction, recovery of the original stems,
or protection of perceptual features that were not recorded in `preserve`.

### A.6 Atomic artifacts (normative)

```text
<case>/studio/tuning/<pair_id>/          published only after BOTH sides are complete
  pair.json
  A/  plan.json  tuned/source.wav  mix.wav  evidence.json
  B/  plan.json  tuned/source.wav  mix.wav  evidence.json
```

`pair.json` (schema `moodify.studio.tuning-pair/0.1`) carries at least: `pair_id`, `mode`,
`source`, `source_sha256`, `tiers: {A: "conservative", B: "full"}`, `calibration_status`,
`engine_version`, `created_at`.

Writing rules:

```text
1. render into a temporary sibling attempt directory inside the same tuning directory
2. A and B (mixes, tuned, plans, evidence) must ALL succeed before publication
3. publish with a single atomic rename; never leave a partial directory at <pair_id>
4. any failure → the attempt directory is removed and <pair_id> never appears
5. an existing <pair_id> is never overwritten; the source audio is never written to
```

`tuned/source.wav` is this mode's single-track "tuned" slot and `mix.wav` is the composite. For a
one-track (stereo) mode the composite step is the identity of the same rendered signal; that
identity is recorded in `plan.json`, not implied. Both files exist so stage derivation is identical
to the deep path (`V4` §3) — a fast pair is a pair, not a special case.

### A.7 Evidence (normative fields, per side)

`<side>/evidence.json` (schema `moodify.studio.tier-evidence/0.1`) carries: `tier` descriptor
(A.3), `mode`, `calibration_status`, `engine_version`, `source_sha256`, `output_sha256`,
`graph_digest_sha256`, the executed node parameters, `before` / `after` / `deltas` / `invariants` /
`peak_gate` verbatim from the mix-graph session, `duration_s` / `sample_rate` / `channels`,
`finite`, and **`review_required: true`** (the machine processed; a human still has to listen).
The mix-graph session's own evidence document is embedded **verbatim** under
`mix_graph_evidence` — never paraphrased. It names the temporary path it rendered to; because the
pair is published by renaming its attempt directory, `render_step` records that relocation
explicitly and `output` carries the final published paths, so no published field points at a
directory that no longer exists.

### A.8 Hard gates (normative)

```text
output exists and decodes
duration preserved within the stated tolerance (exact length for this implementation)
sample rate preserved · channel count preserved
no NaN / Inf
peak within the declared ceiling gate
BOTH sides complete before the pair is published
```

No new "perceptual score" may decide which side is better: the machine may measure, only a human
may prefer.

### A.9 Failure contract

```text
unknown mode / unknown tier          → error, nothing written
source missing / not decodable       → error, nothing written
one side fails to render or verify   → error, no pair published, attempt directory removed
output-dir already exists            → error, nothing written
```

The caller (Studio) maps a failure into its own visible failure state; it must not retry into an
existing pair id.

### A.10 Compatibility and rollback

- New artifacts only. `finishing`, `protocol process`, `compare` and the mix-graph schema are
  unchanged; this addendum adds one CLI command and one artifact family.
- Deleting `<case>/studio/tuning/<pair_id>` returns the case to its previous derived stage with no
  migration, because stages are derived from disk (`V4` §3).
- `moodify-desktop`'s `<case>/studio/finish_mode.json` remains the human's explicit opt-in; the
  fast route must never auto-activate (V4 §4.2). If this addendum is rejected, removing the CLI
  command and the module leaves the shell reporting the previous `TUNABLE_CORE_NOT_AVAILABLE`.

### A.11 Explicitly out of scope for this addendum

- per-stem pitch / timing correction and per-stem mixing (the main specification above);
- multi-stem compositing;
- `moodify tuning roundtrip` — **deferred**: no sourced threshold exists for a `passed` verdict, so
  no `passed: true` may be written, and ④修音 for the deep path stays locked (`V4` §4.1). Producing
  an unsourced pass would be exactly the fabricated gate this repository forbids.

---

## Copyright

All MIPs are licensed under GPL-3.0-only, matching this repository.
