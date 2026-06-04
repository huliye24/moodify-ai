# Human Label Taxonomy — MHP-198

## Label Types

| Type | Description | Use Case | Reliability |
|------|-------------|----------|-------------|
| **Pairwise A/B** | "A is better than B" or "No difference" | Preset comparison | High (relative judgment is easier) |
| **Absolute score** | Rate 1-5 on: clarity, warmth, naturalness, overall | Benchmark scoring | Medium (needs calibration) |
| **Gate agreement** | "Would you approve this track?" (yes/no/needs review) | Gate calibration | High (binary decision) |
| **Defect tagging** | Tag specific issues: over_dark, over_bright, transient, vocal_thinning | Safety gate training | Medium (needs training) |

## Label Quality Dimensions

| Dimension | Measure | Target |
|-----------|---------|--------|
| Intra-reviewer reliability | Same track, 2 reviews, score difference | ≤1 point on 5-point scale |
| Inter-reviewer agreement | % agreement on pairwise A/B | ≥70% |
| Reviewer-gate agreement | % match with automated gate | ≥85% (after calibration) |
| Review latency | Time per A/B pair | ≤30s |
