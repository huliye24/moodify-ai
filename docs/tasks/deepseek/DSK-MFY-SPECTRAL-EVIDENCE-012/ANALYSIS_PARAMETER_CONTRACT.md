# ANALYSIS_PARAMETER_CONTRACT

- `n_fft`: 2048, `hop_length`: 512, `window`: hann
- `sample_rate`: 22050 (resample if native differs)
- `channels`: mono (mean of L+R), or L/R separately per track spec
- `amplitude_scale`: dB, referenced to digital full scale
- `db_range`: (-80, 0) for magnitude; symmetric (-40, 40) for difference
- `loudness_match`: false by default; separate run enabled via `--loudness-match`
- Before/after MUST use identical parameters throughout
