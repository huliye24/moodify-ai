# Sample Asset Commands

> 以下是命令模板，具体命令需要根据 Moodify 代码实际 CLI 调整。

## 注册新样本

```bash
python3 scripts/samples/register_sample.py --input data/raw_inbox/song.wav --source suno --rights internal_research_only
```

## 生成 sample registry 报告

```bash
python3 scripts/samples/build_sample_asset_report.py --registry sample_asset_library/metadata/sample_registry.jsonl --out sample_asset_library/reports/sample_asset_report.md
```

## 检查缺失元数据

```bash
python3 scripts/samples/check_missing_metadata.py --registry sample_asset_library/metadata/sample_registry.jsonl --out sample_asset_library/reports/missing_metadata_report.md
```

## 创建数据集分组

```bash
python3 scripts/samples/assign_dataset_split.py --sample-id SMP-... --split baseline_set_v0.1
```
