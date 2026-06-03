# Preset Library Commands

> 这些是命令模板，具体命令需要根据 Moodify 代码实际 CLI 调整。

## 生成 preset registry

```bash
python3 scripts/presets/build_registry.py --preset-dir presets/ --out data/preset_registry.jsonl
```

## 使用指定 preset 处理样本

```bash
python3 -m moodify.cli process data/night_inputs/example.wav --preset PRESET-CATEGORY-NAME-v0.1 --output-dir runs/preset_test/
```

## 批量评估 preset

```bash
python3 scripts/presets/evaluate_preset.py --preset PRESET-CATEGORY-NAME-v0.1 --input-registry input_registry.jsonl --scoring mrs_open_v031
```

## 生成 preset 报告

```bash
python3 scripts/presets/build_preset_report.py --registry data/preset_registry.jsonl --out reports/preset_library_report.md
```
