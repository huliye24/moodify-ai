# MFY-CR-P06 — Blind Listening Protocol

Prepared by the pipeline (blind.py); execution is human.

## Blind set

```text
X1 X2 X3 X4  =  random permutation of {SOURCE, A, B, C}
```

- Listening files are `golden_run_out/listening/X{1..4}.wav` (48 kHz, 16-bit).
- The mapping lives in `golden_run_out/blind_mapping.json` with
  `finalized: false`. **Do not read the mapping before scoring.**
- Candidate names never appear in listening file names (tested).

## Level matching

```text
METHOD = linear gain to source integrated LUFS (-13.94 LUFS)
TARGET = SOURCE integrated loudness
MAX_DELTA = <= 0.2 LU after matching
TOOL = moodify.reconstruction.blind.level_match
```

Listening copies are NOT canonical candidates; originals (candidates/*.wav)
are preserved and untouched.

## Round 1 — Global preference (per X)

```text
Overall preference:        1-5
Naturalness:               1-5
Identity preservation:     1-5
Vocal clarity:             1-5
Low-end balance:           1-5
Space/depth:               1-5
Artificial modernization:  NONE / SLIGHT / CLEAR
Confidence:                LOW / MEDIUM / HIGH
```

## Round 2 — Pairwise

```text
SOURCE vs TOP1, SOURCE vs TOP2, TOP1 vs TOP2
Which would you choose for normal listening?
Which sounds more faithful?
Is the improvement worth the change?
```

## Repeat

Two rounds at different times (avoid fatigue).

## Thresholds

```text
NOTICEABLE   = difference stably audible
PREFERRED    = listener prefers candidate, not just "different"
IDENTITY_SAFE = no CLEAR_DRIFT on identity preservation
REPEATABLE   = two rounds agree in direction
```

Golden is claimed ONLY if NOTICEABLE + PREFERRED + IDENTITY_SAFE + REPEATABLE.

## After scoring

Report scores back; the pipeline finalizes the mapping
(`finalize_blind_mapping`), the record's golden_status is set, and the
GoldenReconstructionRecord is completed.
