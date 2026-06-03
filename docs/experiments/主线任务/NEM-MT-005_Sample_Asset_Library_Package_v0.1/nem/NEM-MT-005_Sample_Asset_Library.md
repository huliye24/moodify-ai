# NEM-MT-005｜样本资产库

## 1. 节点定义

MT-005 是 Moodify 的样本资产库节点，目标是建立真实 AI 音乐样本体系，使音频样本可以被登记、存储、追踪、分层、评估、复用和长期积累。

本节点关注的是：

```text
真实 AI 音乐样本 -> sample_id -> metadata -> storage -> lineage -> MRS history -> preset history -> asset report
```

## 2. 节点边界

### 负责

- Sample ID 规则；
- Sample Registry；
- Metadata Schema；
- Storage Layout；
- Rights & Usage Record；
- Dataset Split；
- Processing Lineage；
- MRS History；
- Preset Usage History；
- 样本资产报告。

### 不负责

- Runtime 基础能力；
- MRS 公式优化；
- preset 工艺设计本身；
- 用户上传系统；
- 云存储付费方案采购；
- 版权规避、平台规避、指纹规避；
- 未授权音乐的公开分发或商业使用。

## 3. 核心判断

样本资产库不是网盘，而是实验记忆系统。

每个样本必须回答：

1. 它是谁？
2. 它从哪里来？
3. 它能不能用？
4. 它用于哪个数据集？
5. 它被哪些 preset 处理过？
6. 它的 MRS 历史如何变化？
7. 它是否适合作为 baseline / validation / stress 样本？
8. 它是否存在权限风险？

## 4. 样本生命周期

```text
RAW_INBOX -> REGISTERED -> BASELINE / VALIDATION / STRESS_TEST / PRODUCTION_CANDIDATE -> ARCHIVED
```

权限不确定或质量不足的样本不能进入 production_candidate。

## 5. 主要 AEP

- AEP-MT005-001｜Sample ID System
- AEP-MT005-002｜Sample Registry Schema
- AEP-MT005-003｜Storage Layout
- AEP-MT005-004｜Rights & Usage Record
- AEP-MT005-005｜Dataset Split Rule
- AEP-MT005-006｜Processing Lineage
- AEP-MT005-007｜MRS History
- AEP-MT005-008｜Preset Usage History
- AEP-MT005-009｜Sample Quality Tier
- AEP-MT005-010｜Sample Asset Report

## 6. 节点完成定义

当 Moodify 能够稳定地登记真实 AI 音乐样本，追踪其来源、权限、存储路径、处理历史、MRS 历史和 preset 使用历史，并能生成样本资产报告时，本节点才算完成。
