# Repository Binary Inventory — 2026-10-03

**Scope:** proposed current tree after untracking `moodify-core-package/outputs/`
**Method:** `git ls-files` plus exact working-tree byte sizes; ignored/untracked files are excluded

## Summary by extension

| Extension | Files | Bytes | Classification |
|---|---:|---:|---|
| `.wav` | 17 | 26,689,132 | KEEP — bounded regression, benchmark and golden-case fixtures |
| `.png` | 24 | 1,960,832 | KEEP / REVIEW — product assets and bounded documentation screenshots; review separately before any removal |
| `.jpg` / `.jpeg` | 0 | 0 | — |
| `.jar` | 2 | 87,528 | KEEP — Gradle wrapper build infrastructure |
| `.apk` | 0 | 0 | — |
| `.zip` | 0 | 0 | — |
| `.tar` / `.gz` | 0 | 0 | — |
| `.exe` | 0 | 0 | — |
| `.dll` / `.so` | 0 | 0 | — |
| `.onnx` | 0 | 0 | — |
| `.pt` / `.pth` | 0 | 0 | — |
| `.npz` | 15 | 1,140,899 | KEEP — benchmark expected data, golden-case evidence and one bounded data matrix |
| `.svg` | 3 | 851,697 | KEEP — brand/source artwork |
| `.pdf` | 1 | 182,859 | REVIEW — bounded Android release documentation; no deletion authorized |

## WAV classification

### KEEP — Core baseline regression audio

| Path | Bytes |
|---|---:|
| `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav` | 8,640,172 |
| `moodify-core-package/tests/baseline/test_audio/electronic.wav` | 7,680,172 |
| `moodify-core-package/tests/baseline/test_audio/piano.wav` | 5,760,172 |

These three fixtures total 22,080,516 bytes and remain tracked as explicitly required.

### KEEP — benchmark reference fixtures

Ten bounded files remain under `moodify-core-package/benchmarks/reference_audio/fixtures/`:
`clipped.wav`, `dual_tone.wav`, `dynamic_program.wav`, `impulse.wav`, `mono.wav`,
`pink_noise.wav`, `silence.wav`, `sine_1khz.wav`, `stereo_correlated.wav`, and
`stereo_phase_inverted.wav`. They total 2,496,440 bytes.

### KEEP — golden example audio

`examples/golden_case/` retains `source.wav` and three candidate WAVs, totaling
2,112,176 bytes. The task explicitly excludes this bounded example from removal.

### HISTORY ONLY / local ignored — generated Core outputs

The 27 generated WAVs formerly tracked under `moodify-core-package/outputs/` are absent
from the proposed tree. They remain in Git history and may remain on this machine as ignored
local output. Removing them from history is not authorized.

## PNG classification

- **KEEP — product/build assets:** Android launcher/artwork, Moodify brand assets, Studio
  logo/watermark, Core UI assets, and website assets.
- **KEEP — bounded evidence:** six `docs/public-form/**/screenshots/*.png` files document
  reviewed public-form outputs.
- **REVIEW:** screenshot retention may be reconsidered in a later evidence-policy task;
  nothing here is deleted by Cleanup 001.

## Other binary classification

- **KEEP:** both `gradle-wrapper.jar` files are required to bootstrap their Android builds.
- **KEEP:** `.npz` files under benchmark `expected/` and `examples/golden_case/` are bounded
  reproducibility fixtures, not unconstrained runtime output.
- **KEEP:** `brand/assets/moodify-horizontal.svg` is editable brand source artwork.
- **REVIEW:** the one release PDF is small and tied to an existing Android deliverable, but
  the canonical Android client remains unresolved; a later human decision may revisit it.
- **REMOVE LATER:** no additional current-tree binary is classified for automatic removal on
  present evidence.

## Known historical debt

Current-tree cleanup does not reduce historical Git objects. The 32 generated output files
remain reachable from earlier commits, and GitHub repository metadata therefore will not
immediately fall by the 48,208,058 bytes removed from the current tree.
