# Reviewer Bias Risk Map — MHP-199

| Bias | Description | Mitigation |
|------|-------------|------------|
| **Expectation bias** | Knowing which is "processed" affects judgment | Blind A/B (randomize order, hide labels) |
| **Loudness bias** | Preferring louder version (not better) | Loudness-normalize all samples before review |
| **Genre preference** | Reviewer inherently prefers certain genres | Per-genre reviewer calibration |
| **Fatigue** | Degraded judgment after many reviews | Limit to 20 pairs per session |
| **Order effect** | First track in pair rated differently | Randomize A/B order per pair |
| **Anchor effect** | Extreme-quality anchor track skews subsequent ratings | Shuffle extreme cases into normal distribution |
| **Training drift** | Reviewer criteria shift over time | Monthly calibration with reference tracks |
