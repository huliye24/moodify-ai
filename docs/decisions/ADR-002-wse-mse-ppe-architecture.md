# ADR-002｜WSE—MSE—PPE architecture

- Status: Accepted
- Date: 2026-07-31

## Context
声音测量、音乐结构和生产流程目前分散，导致指标、决策和资产无法形成共同证据。

## Decision
采用 WSE（声音变化）、MSE（音乐结构）、PPE（稳定生产）三层；共享 schemas、case ID 和 evidence packet。

## Alternatives
按现有包演进；仅按 DSP/GUI/API 技术层分层；以单一模型为核心。

## Consequences
边界更清楚但需 adapter；MSE 可保持 Planned；不为目录完整创建假实现。

