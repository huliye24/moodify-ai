# 02 — Metadata Data Model

**W01-P03 · 2026-08-17 · 目标库：PolarDB MySQL moodify_dev（P02 ADR-003，SCHEMA_WRITE_BLOCKED）**

## 实体

### tracks（Track 逻辑身份）

| 字段 | 类型 | 说明 |
|---|---|---|
| track_id | VARCHAR(64) PK | `trk_<uuid7>` |
| owner_scope | VARCHAR(128) | 归属范围（当前产品无用户体系 → NULL；INV-12 与 hash 分离） |
| source_object_id | VARCHAR(64) | canonical source 对象 |
| source_hash | CHAR(64) | source 内容 sha256（INV-05 追溯起点） |
| source_format / duration_ms / sample_rate / channels | 元数据 | 来源技术属性 |
| status_class | VARCHAR(32) | 当前阶段（P04 定义权威状态机，此处仅承载） |
| canonical_source_version | VARCHAR(64) | 版本引用 |

### jobs（一次处理任务；字段承载，状态机归 P04）

job_id / track_id(FK) / job_type / requested_at / created_by / pipeline_version / processing_profile_version / current_state / current_attempt / failure_code / failure_summary / started_at / finished_at / ready_object_id

### objects（对象索引；本体在 OSS）

object_id PK / track_id FK / job_id FK / artifact_type / artifact_role / bucket / object_key (UNIQUE) / content_hash / hash_algorithm / byte_size / mime_type / producer / producer_version / pipeline_version / parent_object_id / immutable / retention_class / evidence_class / created_at

### evidence（判断与验收追溯）

evidence_id PK / track_id FK / job_id FK / object_id FK / evidence_type / **claim（非空，INV-07）** / method / evaluator / evaluator_version / verdict / uncertainty / evidence_object_id / created_at

### versions（生产版本记录；非 Git 简单拷贝）

version_id PK / version_kind（pipeline/preset/model/toolchain/app_contract）/ version_value / created_at / status — UNIQUE(kind, value)

## ID 原则（§2.7）

- UUIDv7（RFC 9562）时间有序：`moodify.data_plane.ids.uuid7()`（标准库实现，零依赖）。
- 前缀 ID：`trk_` / `job_` / `obj_` / `ev_` / `ver_`（日志友好、跨 worker/API/object store 传递）。
- 不依赖单数据库实例解释；适合跨区域迁移。

## Hash 原则（§2.8）

- source identity = SHA-256 内容哈希（`moodify.auditory.manifests.sha256_file` 复用 + data_plane 注册）。
- 禁止：文件名 / 上传时间 / DB 行号作为 identity。
- 相同 hash ≠ 相同 ownership（INV-12；Test A 验证：同 hash 两 track 不合并）。

## 数据平面分离

| 内容 | 去处 |
|---|---|
| 元数据/关系/状态字段 | PolarDB（本模型） |
| 音频/渲染/证据二进制 | OSS（key convention 见 01） |
| 运行期临时文件 | worker 本地 scratch（P02 R5） |

## 现有 19 表对照

- moodify_dev 已有 tracks/track_versions 等表（黑箱调查，≈0 数据）→ **合并策略见 05_CURRENT_TO_TARGET_DATA_MAPPING + 06_MIGRATION_PLAN**；本模型不覆盖既有表，非破坏性。
