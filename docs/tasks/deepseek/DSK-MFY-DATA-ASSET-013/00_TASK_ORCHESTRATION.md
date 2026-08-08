# DSK-MFY-DATA-ASSET-013｜数据资产治理与晋升基础 v0.1

**计划日期：** 2026-08-04  
**执行 Worker：** DeepSeek  
**最终 Judge：** Codex / 授权用户  
**前置依赖：** 012 形成可审计 HANDOFF；否则 HOLD  
**执行窗口：** 当日 WSE-02 之后串行；建议新增时间盒 5 小时

## 1. 唯一目标

把 Moodify 产生的数据从“散落文件”变成有身份、有权利边界、有质量状态、有来源链、有删除能力且能安全晋升的数据资产：

```text
Operational Data
  -> 权利 / 隐私 / 完整性检查
Research Evidence
  -> 质量 / 人工标签 / 来源检查
Candidate Dataset
  -> 去标识 / 偏差 / 泄漏 / 许可审计
Approved Training Dataset
  -> 人工批准 / 版本冻结 / 可撤回清单
Model Evaluation Input（未来任务，非本轮实现）
```

本任务不以文件数量代表资产价值，不把运营数据自动变成训练数据，不训练模型，也不实现 AI 音乐平台 App。

## 2. 必读事实源

开始前完整读取：

```text
E:\moodify\docs\tasks\deepseek\DSK-MFY-DATA-ASSET-013\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DATA-ASSET-013\02_CODEX_ACCEPTANCE_MATRIX.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DATA-ASSET-013\03_DATA_ASSET_PRINCIPLES.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-SPECTRAL-EVIDENCE-012\HANDOFF.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DECISION-INTELLIGENCE-011\00_TASK_ORCHESTRATION.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-THICKNESS-001\CODEX_INDEPENDENT_ACCEPTANCE_2026-07-30.md
E:\moodify\docs\product\daily\2026-07-30\ASSET_INVENTORY.md
E:\moodify\docs\experiments\主线任务\NEM-MT-005_Sample_Asset_Library_Package_v0.1\rules\Rights_And_Usage_Rules.md
E:\moodify\moodify_runtime\learning_store.py
E:\moodify\moodify_runtime\craft_memory.py
E:\moodify\scripts\v01_aggregate_treatment_records.py
```

同时检查适用 `AGENTS.md`、Git/dirty 状态、现有 schema、数据权利事实和测试。所有现有音频、数据、Treatment Records、数据库和输出均只读。特别继承既有事实：试听完成不等于版权或训练授权；rights-pending 数据不得被晋升。

编码前完成 `00_IMPLEMENTATION_AUDIT.md`，说明现有 registry/rights/learning/craft 能力、重复模型、冲突、可复用字段、权利缺口和迁移风险。不得通过回填虚假权利状态让样本通过门禁。

## 3. 允许范围

```text
E:\moodify\science\Moodify_Data_Asset_Governance_v0_1_Package\
E:\moodify\docs\architecture\DATA_ASSET_GOVERNANCE_ARCHITECTURE.md
E:\moodify\docs\tasks\deepseek\DSK-MFY-DATA-ASSET-013\
E:\moodify\outputs\deepseek_validation\DSK-MFY-DATA-ASSET-013\
```

仅通过只读 adapter 审计现有事实。禁止修改生产数据库、Runtime、Bridge、DSP、MRS、Learning Store、Craft Memory、历史 records、真实音频和 011/012 实现。禁止联网、云上传、新依赖、GPU、migration、模型训练、生产接入和 Git 操作。需要越界时写 `SCOPE_CHANGE_REQUEST.md`，HOLD 并停止。

## 4. Stage 0｜数据资产合同与权利模型（60 分钟）

冻结以下文件：

- `DATA_ASSET_IDENTITY_CONTRACT.md`：asset、version、derivation、case/work/creator/project 关系；
- `RIGHTS_PURPOSE_MATRIX.md`：保存、处理、研究、内部评估、公开展示、商业使用、训练、再许可分别授权；
- `DATA_CLASSIFICATION_AND_PRIVACY.md`：公开、内部、机密、个人/敏感、客户隔离及去标识规则；
- `PROVENANCE_AND_LINEAGE_CONTRACT.md`：source hash、父子关系、生成器、参数、人工来源；
- `RETENTION_DELETION_WITHDRAWAL_CONTRACT.md`：保留期、legal hold、撤回、派生资产和模型影响登记；
- `PROMOTION_STATE_MACHINE.md`：四层状态、进入/退出条件和 fail-closed 规则；
- `STAGE_0_GATE.md`。

权利必须按“主体 × 资产 × 用途 × 地域/期限 × 证据”表达。`owner-provided`、上传、生成、购买、试听通过或处理完成都不能自动推出训练授权。未知、冲突、过期或撤回一律阻止晋升。

## 5. Stage 1｜只读资产目录与质量画像（90 分钟）

在隔离包实现：

```text
python -m moodify_data_assets audit --roots ... --output-dir NEW_DIR
python -m moodify_data_assets catalog --spec SPEC.yaml --output-dir NEW_DIR
python -m moodify_data_assets validate CATALOG_DIR
```

输出 `asset_catalog.jsonl`、`asset_versions.jsonl`、`lineage_edges.jsonl`、`rights_findings.jsonl`、`quality_findings.jsonl`、`manifest.json` 和 `DATA_ASSET_CARD.md`。目录只保存必要元数据、引用和哈希，不复制音频、歌词正文或客户敏感内容。

最少字段包括：稳定 ID、asset type、版本、来源引用、内容哈希、case/work/project、权利证据引用、允许用途、隐私等级、质量状态、人工标签状态、父资产、派生生成器、保留/删除状态、schema/version。缺失、未知、冲突、不适用和真实 false 必须分开。

目录构建必须确定、可增量、能识别重复与近重复风险，并产生 rejected/quarantine ledger；禁止修改被扫描源。

## 6. Stage 2｜晋升门禁、数据集快照与价值计量（90 分钟）

实现离线、只读的晋升评估：

```text
python -m moodify_data_assets evaluate-promotion --catalog ... --target research
python -m moodify_data_assets evaluate-promotion --catalog ... --target candidate
python -m moodify_data_assets evaluate-promotion --catalog ... --target approved-training
python -m moodify_data_assets snapshot --approved-manifest ... --output-dir NEW_DIR
```

晋升只能生成 proposal，不得自动批准。`Approved Training Dataset` 必须要求显式人工批准人、批准时间、用途、权利证据、版本冻结、删除映射和泄漏审计。数据集快照默认只含 manifest/IDs/hashes/feature references；不复制媒体正文。

实现 `DATA_ASSET_SCORECARD.md/json`，至少报告：

- rights coverage、provenance completeness、schema validity；
- human-label coverage 与标签来源；
- unique work/creator/project coverage 与分布；
- duplicate/near-duplicate、missing、conflict、quarantine 比率；
- deletion/withdrawal resolvability；
- 可用于各用途的资产数量，而非资产总文件数；
- 数据陈旧度和生成器版本分布。

不得用单一总分宣称商业估值或竞争优势。规模、质量、独特性、合法可用性和可学习性分开展示；每个指标带算法、分母、时间和限制。

## 7. Stage 3｜撤回演练、泄漏防护与路线图（60 分钟）

至少完成：

1. 双构建确定性与源哈希不变验证；
2. 模拟一项权利撤回，证明所有直接/派生资产和数据集快照均可定位，旧快照进入 revoked 状态；
3. 模拟 creator/work/project 跨 split 泄漏、重复内容、伪造权利、过期许可、缺人工批准、删除请求和路径逃逸；
4. 证明运营数据不会因为被 catalog 就自动晋升；
5. 测试、lint、type check、CLI smoke，未运行项如实说明；
6. 输出 `APP_DATA_FLYWHEEL_REQUIREMENTS.md`，只定义未来 App 的同意、退出、导出、删除、推荐反馈和训练授权需求，不开发 App；
7. 输出 `VALIDATION_REPORT.md`、`FAILURE_LEDGER.md`、`PROGRESS.md`、`HANDOFF.md`。

HANDOFF 必须报告各层资产数量、rights-pending/quarantine/revoked 数量、晋升 proposal 数、实际批准数（本轮应为 0，除非有独立人工授权）、撤回演练、测试、限制和绝对路径。

## 8. P0 门禁

以下任一情况立即 HOLD：

- 012 无可审计 HANDOFF，却继续假定其输出成立；
- 上传/处理/试听/交付状态被当作训练授权；
- rights unknown/pending/conflict/expired/revoked 资产被晋升；
- 自动批准训练集或伪造人工批准、同意、用途或权利证据；
- 复制受限音频、歌词正文或敏感客户数据进入目录/快照；
- 删除或撤回不能传播到派生资产和快照；
- 同一 work/creator/project 或近重复内容产生不可解释的跨 split 泄漏；
- 覆盖源数据、历史记录或生产数据库；
- 用文件数量或单一总分宣称数据资产价值；
- 越界写入、联网、新依赖、migration、训练或生产接入。

最终状态只能为 `READY_FOR_CODEX_REVIEW`、`DATA_GOVERNANCE_NOT_READY`、`REWORK` 或 `HOLD`。DeepSeek 不得宣布训练数据已获批、数据具备商业估值、App 数据飞轮已经成立或 Moodify 已获得模型优势。

