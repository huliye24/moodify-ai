# MFY-DATA-FACTORY-001 — Real-Audio Pilot Notes (2026-08-10)

4 owned tracks run through the complete machine loop with the frozen
`MFY-DATA-PROTOCOL-001` (schema 1.0). Source audio is NOT committed; case
evidence lives under `outputs/data_factory/` (git-ignored).

## Case IDs

| Track (owned, music/) | Case ID | A | B | C |
|---|---|---|---|---|
| Des portes et des lampes | `case_cf920ec27dbe4290bff24362a53bd425` | INCONCLUSIVE | PASS_TO_LISTENING | PASS_TO_LISTENING |
| J'apprends la tendresse pour toi | `case_080bac74638043abacc129a3b2e51c4a` | INCONCLUSIVE | PASS_TO_LISTENING | PASS_TO_LISTENING |
| T'aimer lentement | `case_bf117642623d43e9a16fd034b394164f` | PASS_TO_LISTENING | PASS_TO_LISTENING | PASS_TO_LISTENING (2 goals) |
| Nous pouvons être calmes chacun | `case_45e96f4c663b4fbead98592511fae126` | INCONCLUSIVE | PASS_TO_LISTENING | PASS_TO_LISTENING |

12/12 judgments passed all machine guardrails (no REJECT). Response curves are
interpretable: A is often below the technical-goal threshold, B/C meet it — the
intended intensity response, not three unrelated "styles".

## Problems found and fixed during pilot

1. **DSP chain safety ceiling was not what it claimed.** `pedalboard.Gain()`
   defaults to +1 dB (not unity), and `pedalboard.Limiter` applies built-in
   auto-makeup-gain normalizing output to full scale (spotify/pedalboard#282).
   Result: every intervention output peaked at 0 dBFS with hundreds of clipping
   samples and true peak above +0.5 dBTP. Minimal fix in
   `moodify.processing.pedalboard_chain`: explicit `Gain(gain_db=0.0)` and
   `Clipping(threshold_db=-1.0)` as the true -1 dBFS hard ceiling.
   Post-fix: sample peak exactly -1.0 dBFS, zero new clipping, true peak ≈ -0.5 dBTP.
2. **TRUE_PEAK_SAFE guardrail threshold calibrated.** With the -1 dBFS sample
   ceiling, inter-sample true peak lands around -0.5 dBTP; the seed threshold
   of -1.0 dBTP could never pass. Calibrated to 0.0 dBTP (fail-closed boundary),
   versioned with the plan generator.

## Observations to keep (not bugs)

- `crest_factor_db` often INCREASES after EQ lift (presence/air boosts raise
  peaks faster than compression lowers them), so the STABILIZE_DYNAMICS goal
  rarely registers as met. Delta values are recorded as authoritative machine
  evidence; goal hit-rate is not the learning target — human ranking is.
- Plan-v1 thresholds remain calibration seeds; re-calibration is a separate
  analytics task after ≥10 valid cases (per protocol integration note 7).

## Dataset status

1 case finalized for pipeline rehearsal (simulated review, reviewer_id
`pilot-simulated-human`, noted as such in the review JSON). 3 cases remain
AWAITING_HUMAN — real listening required before the 10-song pilot.
