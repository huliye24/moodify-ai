# BENCHMARK_PLAN — DSK-MFY-STEM-MIDI-008

## Synthetic Ground Truth (Stage 3)

Programmatically generated MIDI → render to WAV → transcribe → compare.

| Fixture | Content | Purpose |
|---|---|---|
| Monophonic scale | C4-C5 单音阶梯 | Note precision baseline |
| Chord triad | C-E-G 同时发声 | Polyphony accuracy |
| Bass line | E2-A2 八度跳跃 | Octave error check |
| Pitch bend slide | C4→D4 glide | Pitch bend preservation |
| Mixed poly/mono | Alternating chords + melody | Realistic scenario |

All fixtures rendered with `pretty_midi` → fluidsynth (if installed) or basic sine synthesis.

## Metrics

| Metric | Threshold (target) | Notes |
|---|---|---|
| Note precision | >0.80 | Correct notes / total detected |
| Note recall | >0.70 | Correct notes / total reference |
| Note F1 | >0.74 | Harmonic mean |
| Onset tolerance | ±50ms | Acceptable onset deviation |
| Octave error rate | <0.10 | Fraction of octave errors |

## No False Claims

- Real songs with no ground truth → smoke test only (does backend run without crash?)
- "Accuracy" only reported when verified against known MIDI
- Every metric report includes: what was measured, against what reference, what uncertainty

## Performance

| Metric | Target | Measurement method |
|---|---|---|
| Cold start latency | Recorded | perf_counter before/after first transcribe |
| Per-stem latency | Recorded | per-stem elapsed |
| Peak memory | <4 GB | psutil (if available) or OS tools |
| Model load count | 1 | Check backend singleton |
