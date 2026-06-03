# Inspect MRS Results Commands

## 查看评分记录

```bash
head -5 runs/*/mrs_scores_*.jsonl
```

## 查看最高分样本

```bash
python3 scripts/inspect_mrs_scores.py --sort desc --top 20
```

## 查看最低分样本

```bash
python3 scripts/inspect_mrs_scores.py --sort asc --top 20
```

## 查看耗时

```bash
python3 scripts/profile_mrs_runtime.py --input runs/*/mrs_scores_*.jsonl
```
