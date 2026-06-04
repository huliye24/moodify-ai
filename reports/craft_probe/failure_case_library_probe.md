# Failure Case Library Probe — MHP-153

**Date**: 2026-06-04 | **Result**: JSONL queryable library proven ✅

## Method

`FailureCase` dataclass with preset, genre, defect_type, severity. JSONL storage with `query_failure_cases()` filter.

## Schema

```json
{"case_id":"FC_001","preset":"warm_vocal","genre":"piano",
 "defect_type":"over_dark","severity":"severe",
 "sample_id":"CALPIA015","notes":"Bass resonance excessive"}
```

## Query Example

```python
query_failure_cases(dir, defect_type="over_dark", preset="warm_vocal")
# → returns all over_dark cases for warm_vocal
```

## Conclusion

Library is queryable by 4 dimensions. Ready for Build NEM to populate with real failure cases from batch validation (MHP-173).
