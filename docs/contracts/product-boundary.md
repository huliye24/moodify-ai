# Moodify Product Boundary & Shared Contracts — v1

Status: FROZEN — MFY_PRODUCT_BOUNDARY_AND_SHARED_CONTRACTS_001

> **CLASSIFICATION UPDATE (2026-08-14) — Per Constitution v2.0 and Release Topology v1.0: Moodify Music is the only PUBLIC_PRODUCT; Moodify Ear is INTERNAL_CANONICAL (internal research and production authority, not a public consumer product). Contract rules below are unchanged; only the public/internal classification labels are updated.**

## 产品组合

| 产品 | 核心任务 | 主要用户 | 客户端 | 权威数据 |
|---|---|---|---|---|
| **Moodify Ear** | 听、表示、判断、干预、验证、学习 | 研究/制作/判断者 | Web + desktop/client | case、measurement、evidence、rules |
| **Moodify Music** | 发现、播放、收藏、创作、发布 | 听众与创作者 | Web/PWA + mobile app | user、creator、track、version、passport、library |
| Auditory Intervention Laboratory | Ear 的受控干预子系统 | Ear 操作者 | 工具 | evidence 产物（非 Music 后台母体） |

## 目录分类（E:\moodify）

| 目录 | 分类 | 说明 |
|---|---|---|
| moodify-core-package | **INTERNAL_CANONICAL** | Ear 权威后端（job queue/cases/measurements/evidence） |
| apps/android | **INTERNAL_CANONICAL** | Ear 原生客户端（pairing/jobs/results；CreatorCenter 等 UI = EXPERIMENTAL 标注） |
| apps/music-web | **PUBLIC_PRODUCT** | Music Web/PWA |
| apps/music-android | **PUBLIC_PRODUCT CANDIDATE** | Music 最小移动壳（33D） |
| apps/tools | SHARED / EXPERIMENTAL | 工具脚本 |
| ops/ | SHARED | 部署/运维（web_origin、ear_batch、data_node） |
| docs/contracts/music | SHARED | Music 契约（身份/所有权/发布/公开 API/生命周期/共享客户端） |
| schemas/canonical | SHARED | JSON 契约 schema |
| artifacts/ | SHARED | 证据/实验产物（EAR evidence 为主） |
| 补丁包/ | LEGACY / PROCESS | 历史任务包与交接记录 |
| 07Music、RJWC_*、deliverables、experiments 等根目录 | EXPERIMENTAL / LEGACY | 历史素材与实验（不参与生产） |

## 依赖规则

- `apps/music-*` 与 `moodify-music-package` **不得 import** `moodify.auditory`、`moodify.orchestration`、
  `moodify.intervention`（Intervention Lab 内部模块）或访问 Ear SQLite 数据库。
- `moodify-core-package` 不得修改 Music 发布状态（Track status 由 Music API 独占）。
- 共享仅限：不可变 Asset ID/SHA-256、Ear Production Case ID、Evidence Artifact 稳定引用、
  版本/错误模型/request ID（见下）。

## 共享契约（有限）

| 项 | 规则 |
|---|---|
| Asset ID / 版本 ID | 不可变字符串 + SHA-256 可验证；不复制私人音频进 Git 或 App 包 |
| Ear Production Case ID | Music 侧仅外部引用字符串（无 FK） |
| Evidence Artifact 引用 | 生成版本 + 验证状态（experimental/verified/human-reviewed）+ 人类审核时间 |
| 错误模型 | `{error:{code,message,request_id}}`（Music 与 Ear API 同构） |
| 跨系统请求 | 见「分析请求交换状态」 |

## 分析请求交换状态（Music 请求 Ear 分析）

```text
requested -> processing -> evidence_ready -> human_reviewed -> optionally_attached
```

- 该状态**不取代** Ear Production Case 状态机或 Music Track 状态机；只描述跨系统请求。
- 实验指标（experimental）永不成为公开质量分数、排名或版权结论。
- Creation Passport 是创作者来源声明，不是 Ear 验证或版权认证。
- 本阶段仅冻结契约，不实现持久化（若实现必须选定唯一权威服务 + 幂等键）。

## 命名矩阵

| 项 | Ear | Music |
|---|---|---|
| 域名 | rongjingmusic.com（工作台）、rongjingwenchuan.com（产品站） | rongjinwenchuan.xyz（聆听站） |
| API namespace | /api/v1（Ear）、/internal/v1（内部） | /api/v1/music（BFF）、/internal/v1/music（内部） |
| Android applicationId | com.moodify.app | com.moodify.music |
| 存储 | SQLite + case 目录 | PolarDB moodify_dev + LA 媒体根 |
| 部署 | LA nginx/FastAPI、杭州 8000 | LA BFF :8100、杭州 8000、PolarDB |

## 禁止退化

- Music 不得退化为 Ear 指标展示壳或音频处理工具。
- Ear 不得退化为自动母带/preset 产品。
- 旧处理 App（apps/android 的 Music UI 实验）评估迁移到 Ear 客户端或 Lab 工具，
  不直接改名发布为 Music App。
