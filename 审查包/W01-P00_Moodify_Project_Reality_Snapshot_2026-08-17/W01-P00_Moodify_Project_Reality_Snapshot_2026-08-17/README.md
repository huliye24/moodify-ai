# W01-P00 Package README

本压缩包是 **Moodify Cognitive Wave 01** 的第一个任务包：

> **W01-P00 — Moodify Project Reality Snapshot**

它不是开发包，而是下一轮开发之前的**只读现实基线**。

## 推荐执行顺序

1. 阅读 `W01-P00_MASTER_TASK.md`
2. 执行 `scripts/readonly_node_scan.sh`（只在你明确拥有只读 SSH 权限的 Linux 节点）
3. 按 `templates/` 中模板生成事实报告
4. 用 `schemas/truth_table.schema.json` 校验 Truth Table 字段
5. 完成 `templates/ACCEPTANCE_CHECKLIST.md`
6. 停止，等待人类审核

## 包结构

```text
W01-P00/
├── README.md
├── W01-P00_MASTER_TASK.md
├── 01_CODEX_EXECUTION_PROMPT.md
├── 02_KNOWN_STARTING_ANCHORS.md
├── scripts/
│   └── readonly_node_scan.sh
├── templates/
│   ├── REALITY_REPORT_TEMPLATE.md
│   ├── TRUTH_TABLE_TEMPLATE.csv
│   ├── CURRENT_SYSTEM_MAP_TEMPLATE.mmd
│   └── ACCEPTANCE_CHECKLIST.md
└── schemas/
    └── truth_table.schema.json
```

## 最重要的原则

**先获得现实，再改变现实。**

如果扫描发现严重问题，也不要在本包中修复。
