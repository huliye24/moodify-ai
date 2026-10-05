# PROCESS performance — ThinkPad Heavy Lane, 2026-10-05

Machine: ThinkPad (LENOVO 21SJ, Core Ultra 5 135H 14c/18t, 16 GB, NVMe SSD, **no CUDA**)
Pipeline: official `moodify protocol` CLI path · backend: **cpu** · tool: `scripts/benchmark_process.py`
Raw outputs: `local_audio_assets/bench/{A,B,C}_*/` (ignored, not committed)

## Baseline (warm steady state, medians)

| Input | validate | analyze | process | verify | total | analyze peak RAM |
|---|---:|---:|---:|---:|---:|---:|
| A 10 s | 0.59 | 3.54 | 1.42 | 1.72 | **7.30** | 126 MB |
| B 60 s | 0.56 | 5.36 | 1.86 | 2.18 | **10.00** | 281 MB |
| C 180 s | 0.55 | 10.09 | 2.96 | 3.06 | **16.74** | 655 MB |

Cold first-run penalty: **+35–40 %** on every stage (C: 25.5 s cold → 16.7 s warm).
Warm cost model: analyze ≈ 3.2 s fixed + 0.038 s/audio-s; process ≈ 1.3 s + 0.009 s/s.

## Optimization 001 — ffmpeg discovery/version memoization

`ffmpeg -version` was spawned 3× per analyze for identical metadata (2× in
`spectrogram.py`, 1× in `decode.py`) plus duplicated PATH discovery;
now one memoized probe per process (warm spawn cost: 0.167 s).

| Input | analyze before | analyze after | Δ |
|---|---:|---:|---:|
| A 10 s | 3.736 s | 3.539 s | −0.197 s (−5.3 %) |
| B 60 s | 5.825 s | 5.364 s | −0.461 s (−7.9 %) |

Zero behavior change: spectrum PNG sha256 byte-identical; 199 focused tests +
full 1403-test suite pass (0 regressions). Observed delta straddles machine
warm-up drift; effective range stated as −0.2 … −0.46 s, direction consistent
with the 0.33 s mechanism prediction.

## Soak (15 jobs)

15/15 ok · process 1.29–1.58 s · peak RAM 91.1 → 91.1 MB (flat) · 0 hash
mismatches · 0 stray ffmpeg/ffprobe · no leftovers · outputs byte-identical
across independent runs.

Bottleneck candidates identified but **not** yet done (see
`docs/development/THINKPAD_PROCESS_PERFORMANCE.md` §4): CLI import diet
(~0.2–0.3 s × 4 stages), single-pass dual spectrogram, scipy.signal import
(structural).
