# Chunk Equivalence

Exact streaming peak/RMS sufficient statistics were compared at chunk sizes 1,024
and 8,192 samples against direct float64 computation on 48,001 stereo frames.
Both agree within `1e-12`. Chunk iteration validates size/overlap and never
double-counts non-overlap statistics.
