# MFY-CR-P06 — Baseline

Executed 2026-08-17 on `codex/moodify-classic-reconstruction-001`
(P01..P05 baselines; P04 absent and absorbed into this package as the
objective layer — per user decision, P04 executed separately afterwards).

## New implementation

```text
moodify-core-package/src/moodify/reconstruction/
  __init__.py      — public API
  objective.py     — RECONSTRUCTION_OBJECTIVE_POLICY_V1: deterministic A/B/C plans
                     from Era Diagnostic findings (P04-absorbed)
  pipeline.py      — run_golden_pipeline: source freeze -> diagnostic -> plans
                     -> render -> hard gates -> identity guard -> ranking -> blind kit
  blind.py         — X1-X4 blind kit: level matching, hidden mapping, finalize
  record.py        — GoldenReconstructionRecord (evidence record, no second authority)

moodify-core-package/tests/reconstruction/test_golden_pipeline.py (12 tests)
```

## Golden run

```text
SOURCE  = CAD10-05_VIEILLIR ("Vieillir et devenir nouveau avec toi", cadeau10
          album, OWNED by Moodify) — 182.16 s, 48 kHz, 24-bit, stereo WAV
sha256  = aa1542c00866efa8e438cfcaf6b40b2325abe2285e5896e8751151459700e9e5
run dir = moodify-core-package/golden_run_out/ (audio stays local, not committed)
```

## Key chain findings (recorded, not silently tuned)

1. The shared DSP chain's **always-on Compressor** (ratio 2, threshold -24)
   flattens dynamic recordings (LRA 12.7 -> 8.0 on this source) — the identity
   guard correctly REJECTed those candidates. The objective therefore bypasses
   compression (ratio 1.0) as an explicit, documented decision.
2. The chain's **default 20 % wet reverb** adds ~+4.2 LU of loudness. The
   objective disables it (P11=0) — no space objective exists in P06; reverb
   change would risk IG-03/era-texture damage.
3. Loudness/timbre deltas of final candidates are surgical: LUFS +0.03..+0.93,
   LRA +0.0..+0.55, crest -0.54..+0.01, centroid +38..+253 Hz, no new clipping.

## Scope

No Android, no payment, no encryption, no public library, no device-specific
mastering. Commercial audio not committed — only hash/metadata/measurements.
