# MHP-019B：Git Data Policy Cleanup — 设计规格

> 日期：2026-05-30
> 来源：ChatGPT
> 等级：L1
> 目标：建立生成文件的 Git 提交边界

## 核心

- .gitignore 忽略大型资产（WAV/PNG/HTML/bak/reports/），保留 baseline test audio + treatment records
- README + Snapshot 增加 Data Commit Policy 章节
- 不修改任何源码/测试/脚本
