# ADR-003｜Production Case as core unit

- Status: Accepted
- Date: 2026-07-31

## Context
Job、Workspace、Treatment Record、报告和 Craft 分别保存事实，缺少统一不可变单位。

## Decision
Production Case 是核心聚合；原始记录不可变，修正追加 revision；资产用 SHA-256；大指标用 Parquet；规则/假设用 YAML；元数据用 DuckDB。

## Alternatives
以音频文件、Job、Workspace 或报告为核心；单一 JSON 目录。

## Consequences
需要兼容映射和迁移；换来可追溯、重放和规则证据链。

