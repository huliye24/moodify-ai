# Run MRS Validation Commands

以下命令是模板，需要根据真实项目路径调整。

## 运行 MRS Open 验证

```bash
python3 experiments/validate_mrs_open_v03.py
```

## 运行指定版本验证

```bash
python3 experiments/validate_mrs.py --config configs/mrs_open_v03.yaml --output runs/mrs_validation/
```

## 查看验证结果

```bash
ls -lah runs/mrs_validation/
cat runs/mrs_validation/*summary*.txt
```

## 生成 Markdown 报告

```bash
python3 scripts/generate_mrs_report.py --input runs/mrs_validation/ --output reports/mrs_validation_summary.md
```
