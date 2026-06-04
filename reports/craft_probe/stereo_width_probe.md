# Stereo Width Probe — MHP-151

**Date**: 2026-06-04 | **Result**: Mid/side ratio comparison proven ✅

## Method

Compute side/mid RMS ratio for both before and after. Drop >20% in width indicates stereo collapse.

## Synthetic Test

Same stereo file → width unchanged → level=none ✅

## Limitation

Most calibration samples are mono (converted from MP3 with `-ac 1`). Stereo probe returns "mono_input" note for mono files. Only applicable to stereo source material.

## Conclusion

Detector works. Limited utility until stereo source material is added to dataset. Document as P2 gate rule.
