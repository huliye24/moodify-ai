# Evaluation Commands

## 对比 MRS before / after

```bash
python3 scripts/mrs/compare_before_after.py --before original.wav --after processed.wav --preset PRESET-CATEGORY-NAME-v0.1
```

## 检查响度作弊风险

```bash
python3 scripts/mrs/check_loudness_cheat.py --before original.wav --after processed.wav
```

## 检查高质量输入损伤

```bash
python3 scripts/mrs/check_hq_damage.py --input high_quality.wav --preset PRESET-CATEGORY-NAME-v0.1
```
