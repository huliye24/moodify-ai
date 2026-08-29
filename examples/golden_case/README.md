# Golden Production Case

**Case:** `case_00000000000000000000000000000001`
**Source:** `dynamic_program.wav` (deterministic synthetic fixture from the
[Reference Audio Suite](../../moodify-core-package/benchmarks/reference_audio/REFERENCE_SUITE.md),
public-domain-like, no copyright material)
**Status:** ALGO_REVIEWED — full closed loop, algorithmic review
**Ranking:** `["A", "B", "C", "SOURCE"]`, no rejected candidates

## What this is

One complete, reproducible Auditory Production Case produced by the canonical
loop:

```text
SOURCE -> before scan -> diagnosis -> ABC plans -> candidates
       -> after scans -> comparisons -> algorithmic review
```

Every artifact here is machine-generated and versioned:
`case_manifest.json` records source/candidate sha256 hashes and all software
versions (scan profile, plan generator, judgment rules, package version).

## Reopen and verify

```bash
cd moodify-core-package
pip install -e .
python ../examples/golden_case/reopen_golden.py
```

Expected output: `GOLDEN CASE OK` — the case bundle hash-verifies, the review
reloads, and 6 deterministic pairwise rows are produced.

## Reproduce from scratch

```bash
cd moodify-core-package
python benchmarks/reference_audio/generate_reference_suite.py
python - <<'EOF'
from pathlib import Path
from moodify.data_factory.runner import run_production_case
run_production_case(
    Path("benchmarks/reference_audio/fixtures/dynamic_program.wav"),
    Path("../examples/golden_case_repro"),
    case_id="case_" + "0" * 25 + "0000001",
)
EOF
```

The regenerated case must match this one's metrics (cross-machine
repeatability: 52/52 identical, 2026-08-11) and produce the same review ranking.
