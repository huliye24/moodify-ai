# Runtime Linkage Commands

## Runtime 处理时写入 lineage

```bash
python3 -m moodify.cli process sample_asset_library/baseline/SMP-.../original.wav   --preset PRESET-...   --output-dir sample_asset_library/baseline/SMP-.../processed/RUN-.../   --write-lineage sample_asset_library/lineage/processing_lineage.jsonl
```

## MRS 评分写入 history

```bash
python3 scripts/mrs/score_and_record.py   --sample-id SMP-...   --run-id RUN-...   --out sample_asset_library/lineage/mrs_history.jsonl
```
