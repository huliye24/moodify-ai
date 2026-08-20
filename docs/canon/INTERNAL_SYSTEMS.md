# INTERNAL SYSTEMS — Moodify

**Canon v1.0（W01-P01, 2026-08-17）**

以下系统是 Moodify 的内部能力，不构成对外产品面。保留其研究与工程资产，不删除。

## 1. Moodify Ear / Auditory Intelligence

内部听觉智力层：listen → represent → judge → evidence → uncertainty → learn → verify → controlled intervention。

- 权威参考：[AUDITORY_INTELLIGENCE_ARCHITECTURE.md](../AUDITORY_INTELLIGENCE_ARCHITECTURE.md)（INTERNAL）
- 资产：`moodify-core-package/src/moodify/auditory`、`era_diagnostic`、`identity_guard`、`reconstruction_objective` 等（按各自包文档分类）

## 2. Cloud Production System

云端生产系统（角色级；拓扑由 W01-P02 决定）：

```text
Intake → Identify → Analyze → Stem → Judge → Intervene
      → Preset Decision → Render → Verify → Evidence → Delivery
```

## 3. 状态机 / 队列 authority（现状）

| 系统 | 分类 | 依据 |
|---|---|---|
| `orchestration/workflow_engine` | LEGACY | 既有声明（REPOSITORY_STATUS） |
| `node`（moodify-node worker） | CANONICAL（云端队列实跑） | P00 TT-009 |
| `data_factory` | CANONICAL（pilot 10/10） | P00 TT-008 |
| `reconstruction_factory` | EXPERIMENTAL | P00 TT-013 |

单一 authoritative state machine 的统一方案 → `HUMAN_DECISION_REQUIRED`（控制面任务范围）。

## 4. 外部能力分类（引用 P00，维持原状态）

| 能力 | 状态 |
|---|---|
| LALAL.AI / Audiolla（LA 容器） | CONNECTED_UNTESTED（已部署，无自动 pipeline） |
| FFmpeg | DEPLOYED_NOT_VERIFIED（双节点部署） |
| Demucs | PLANNED_ONLY（权重未下载） |
| Basic Pitch | IMPLEMENTED_NOT_MERGED（工具代码） |

## 5. 认知基础设施

- Canon：`docs/canon/*`
- Evidence：`artifacts/`、`moodify-core-package/golden_run_out/` 等
- Cases / Rules / Failures：见 `docs/ASSET_MODEL.md`（INTERNAL）与各包文档

> 内部系统可以复杂；复杂度由 Moodify 承担，不转嫁给用户。
