# Memory

- Large arrays use NumPy storage and compressed NPZ cache with pickle disabled.
- Feature Bus records byte estimates and supports explicit release.
- Exact chunked direct metrics avoid additional full-length float64 copies.
- Sequential process RSS observed after 30 s / 3 min / 10 min runs was approximately
  117 MB / 176 MB / 320 MB. This is not isolated peak RSS, but growth is bounded and
  sublinear relative to audio duration in the observed series.
