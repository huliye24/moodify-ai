# MHP-894: Ownership Map
**Status**: done

## E-Chain 015 Ownership
| Component | Owner | Files |
|-----------|-------|-------|
| MAP formulas, schemas, thresholds | Architect | v01_types.py, v01_pipeline.py (orchestration), map_chain_report.schema.json |
| Scan, feature, diagnosis | Worker | v01_analyzer.py, v01_diagnostics.py, v01_pipeline.py (scan_audio) |
| MRS scoring integrity | Judge | mrs_engine.py (read), mrs_adapter.py, over_dark.py |
| Delivery, manifest, metadata | Worker | v01_delivery.py, v01_exporter.py |
| AWJ policy enforcement | Judge | map_judge_check.py, docs/policy/map_chain_awj_scope.md |
| Operator runbook | Architect | docs/plan/MHP-887 |
| E-Chain lifecycle | Architect | docs/echain/ECHAIN-MOODIFY-MAP-CHAIN-015.md |
