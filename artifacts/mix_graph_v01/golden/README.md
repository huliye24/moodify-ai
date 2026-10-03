# Mix Graph v0.1 — Golden Case Evidence

**Schema:** `moodify.mix_graph/0.1`（EXPERIMENTAL — freeze gate: this golden case + deterministic replay）
**Generated:** 2026-09-29, core `1.0.0-rc.1`, branch `codex/professional-finishing-layer-20260920`

## Contents

| File | What it is |
|---|---|
| `graph.json` | The session graph (derived from preset `clean_master`) |
| `example_mixgraph_8eec7960.wav` | Rendered output (48 kHz / stereo / PCM_16) |
| `example_mixgraph_8eec7960.evidence.json` | Per-node before/after + verification evidence |

- `graph_digest_sha256`: `8eec79605d78ffc947aee6a21eb1da7f017d44cc5f493cf669697c33a560efdd`
- `source_sha256`: `a7b3ca0b99c28f9e15e9bbf585b9a6760fb118c9ad2181c7e7825517fb521f57` (`demo/input/example.mp3`, 174.6 s)
- `output_sha256`: `aaf090e425bb80889acfacafe47c902b8c4e49185e9d6de5c7c698785041870e`
- Peak gate: limit -1.0 dBFS, measured -2.08 dBFS → **passed**
- Loudness delta: -0.25 LU; all invariants (finite / length / channels) **true**

## Reproduce

```bash
cd moodify-core-package
PYTHONPATH=src python -m pytest tests/mix_graph/test_golden.py -m v01 -q
# or regenerate these files from scratch:
PYTHONPATH=src python -c "from moodify.release_cli import main; \
main(['finishing','new','--preset','clean_master','--source','../demo/input/example.mp3','--out','../artifacts/mix_graph_v01/golden/graph.json']); \
main(['finishing','render','../artifacts/mix_graph_v01/golden/graph.json','--output-dir','../artifacts/mix_graph_v01/golden'])"
```

Same core version + same graph + same source must reproduce the output byte-for-byte
(asserted by `tests/mix_graph/test_golden.py` and `tests/mix_graph/test_replay.py`).

## Fact boundary

Machine measurements only. This evidence makes **no** listening-quality claim;
perceptual judgement remains with the algorithmic review authority. v0.1 scope:
serial EQ → Compressor → Stereo → Limiter on one stereo source; no stems/buses,
no reference matching, no VST hosting.
