# MFY-CR-P03 — Validation Corpus

## Synthetic controls (generated at test time, deterministic seeds)

`tests/era_diagnostic/conftest.py`:

- clean full-band stereo reference (11 tones 220 Hz-19 kHz + -40 dBFS noise bed,
  -75 dBFS generation noise, silence gaps 1.2s/1.2s/1.0s, stereo corr ~0.97);
- low-pass ladder (18k / 15k / 12k / 9k, 4th-order Butterworth);
- hiss ladder (-70 / -60 / -50 dBFS, everywhere incl. silence);
- heavy clipping (x50 + hard clip at 0.999);
- mono fold-down;
- width 50 % / 30 % (side scaling);
- phase perturbation (right channel sign flip 2-4 s);
- dark-but-clean (220/440 Hz only, 9 kHz LP);
- lo-fi texture (12 kHz LP + -45 dBFS hiss);
- soft-compressed aesthetic (tanh, no hard clipping).

All fixtures know their ground truth. No copyrighted material, no binaries in git.

## Negative controls (style must not be called a defect)

| Test | Character | Desired behavior (asserted) |
|---|---|---|
| N01 | intentional mono | LIKELY_ARTISTIC_CHARACTER, LOW |
| N02 | dark-but-clean | LIKELY_ARTISTIC_CHARACTER, LOW |
| N03 | lo-fi / tape texture | noise never HIGH; ambiguity recorded |
| N04 | compressed aesthetic | NOT_APPLICABLE or OBSERVED, never POSSIBLE |
| N05 | narrow vintage stereo | never POSSIBLE; ambiguity recorded |

## Owned / authorized listening set

Not applicable in P03 (no human listening in this execution; human review is
a P04+ calibration step). Manifest structure is defined by the constitution;
no commercial audio enters git.
