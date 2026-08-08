# XLSX Research Schema v0.1

`spectral_evidence.xlsx` is a deterministic human research view. JSON and CSV remain the fact layer.

| Sheet | Contract |
|---|---|
| README | case identity, generator, parameters, limitations and interpretation rules |
| Track_Summary | one row per track with hashes, source format and before/after metrics |
| Band_Comparison | one row per track/band; numeric before/after/delta values |
| Time_Sections | explicit `NOT_PROVIDED` when the case has no section contract |
| Decision_Log | processing action metadata; never inferred from audio |
| Human_Review | blank until an authorized human enters reviewer, decision and reason |
| Data_Quality | warnings, errors and explicit conversion actions |

The workbook contains no macros, embedded audio or automatic preference labels. Parquet absence is recorded as `NOT_AVAILABLE_NO_PYARROW`.

