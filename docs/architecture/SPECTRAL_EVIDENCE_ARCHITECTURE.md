# Moodify Spectral Evidence Architecture v0.1

```text
rights-authorized before/after pair
  -> strict case/track identity and source-format preflight
  -> explicit mono/resample analysis actions
  -> common-reference STFT and time-domain metrics
  -> before / after / signed difference images
  -> JSON + CSV fact layer
  -> XLSX human research view
  -> hashes, validation and limitations
```

The package is isolated under `science/Moodify_Spectral_Evidence_v0_1_Package`. It does not modify source audio, production DSP, Treatment Records or Human Review. Source sample-rate/channel mismatch and timeline mismatch are rejected rather than silently aligned. Every output bundle is new, manifest-addressed and independently verifiable.

The layer supplies evidence to future Treatment Records and data-asset governance. It is not a sound-quality decision engine and cannot promote rules or training data.

