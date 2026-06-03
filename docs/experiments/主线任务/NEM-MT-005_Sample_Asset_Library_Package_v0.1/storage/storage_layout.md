# Sample Asset Library Storage Layout

```text
sample_asset_library/
  raw_inbox/
  registered/
  baseline/
  validation/
  stress_test/
  production_candidate/
  archived/
  metadata/
  lineage/
  features/
  reports/
```

## Per-sample folder

```text
{split}/{sample_id}/
  original.wav
  metadata.json
  processed/
    {run_id}/
      output.wav
      report.md
  features/
  notes.md
```
