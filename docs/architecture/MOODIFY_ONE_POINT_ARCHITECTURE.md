# Moodify One-Point Architecture

**文档编号：MFY-OPA-001**
**状态：架构增量 — 不覆盖 MOODIFY_SYSTEM_ARCHITECTURE_v0.4.md**
**生效日期：2026-08-01**

## 1. 架构命题

现有架构（v0.4）正确地将 Moodify 分解为 WSE / MSE / PPE / Gate / Craft 等模块。One-Point 架构不替换这些模块，而是在它们之上增加一个**单一入口门面**，使操作者通过一个意图合同进入，获得一个以作品为中心的结果包。

## 2. 层次关系

```text
┌──────────────────────────────────────────┐
│  One-Point Facade (refine prepare)       │  ← NEW: single entry
│  OnePointSpec → OnePointResult + summary │
├──────────────────────────────────────────┤
│  PPE Runner (ppe run)                    │  ← EXISTING: reused
│  Gate evaluation / Ledger / Evidence     │
├──────────────────────────────────────────┤
│  WSE / MSE / Treatment / Candidate       │  ← EXISTING: untouched
│  Core analyzers / DSP / Craft Memory     │
└──────────────────────────────────────────┘
```

One-Point 门面：
- **接收** OnePointSpec（人的意图合同）
- **委托** PPE Runner 执行 case 创建、资产验证、证据编译和报告
- **翻译** 内部结果（GateResult、ValidationResult、MeasurementRecord）为五项外部叙事
- **产出** 渐进披露结果包（默认层只有 5 个概念，证据层保留全部）

## 3. 数据流

```text
OnePointSpec (YAML)
  → validate (fail-closed: essence/protect/allow/avoid/owner all required)
  → case_load (ProductionCase manifest at spec.source)
  → case_validate (asset identity, hash check)
  → evidence_compile (existing PPE evidence pipeline)
  → gate_evaluation (existing 6 gates)
  → translate (map internal results → OnePointResult 5-field narrative)
  → write result.json + summary.md + evidence/
  → FINAL_STATUS.txt
```

## 4. 新增对象

### OnePointSpec (schemas.py)
```text
schema_version, spec_id, source, case_id (optional),
essence, must_preserve, desired_change, must_avoid,
human_owner, limitations, reference_assets, delivery_conditions
```

严格模式：未知字段拒绝；essence/must_preserve/desired_change/must_avoid/human_owner 不得为空。

### OnePointResult (schemas.py)
```text
schema_version, result_id, spec_identity,
status (READY_FOR_REVIEW | BLOCKED | NEEDS_EVIDENCE | FAILED),
essence, protect, allow, avoid, action, entrust, owner,
evidence_path, created_at
```

### Conflict Detection

`must_preserve` 与 `desired_change` 的冲突检测通过关键字重叠实现初筛。不声称自动语义理解——冲突候选标记为 BLOCKED 并写明理由，由 human_owner 判断。

## 5. 新增 CLI

```powershell
py -3.12 -m moodify_bridge.cli refine prepare SPEC.yaml --output-dir NEW_DIR
```

`refine` = 唯一动作名（来自 LANGUAGE_CANON）。
`prepare` = 诚实后缀：当前实现只形成计划和证据，不生成音频。

该命令：
1. 读取 OnePointSpec
2. 验证合同（冲突检测、完整性检查）
3. 委托现有 PPE Runner 执行底层流程
4. 翻译结果 → OnePointResult
5. 写入渐进披露结果包
6. 预期错误使用稳定码、无 traceback

## 6. 结果包布局

```text
NEW_DIR/
  result.json           # OnePointResult: 5 项核心叙事 + 状态
  summary.md            # 默认阅读面（12 词以内语言）
  summary.html          # 克制、可访问的 HTML
  evidence/             # 完整技术证据
    run_manifest.json   # RunManifest
    gate_results.json   # GateResult[]
    case.yaml           # ProductionCase
    spec.yaml           # OnePointSpec（输入副本）
    package_manifest.json # SHA-256 inventory for the complete result package
    lyrics/             # optional, authorized lyrics evidence only
      original.txt
      original.txt.sha256
      lyrics_evidence.json
    ledger/             # DuckDB
  FINAL_STATUS.txt
```

## 7. 兼容策略

- 不修改现有 schema 或 migration
- 不移动、重命名或删除现有 CLI 命令
- OnePointSpec 通过 source 引用现有 ProductionCase YAML manifest；case_id 只用于可选的一致性核对
- PPE Runner（`ppe run`）继续独立可用
- 旧测试不修改、不减量、不因新功能而降低断言

## 8. 不做什么

- 不新增 DuckDB table 或 migration
- 不创建创作者前端
- 不替换 WSE/MSE/PPE 内部命名
- 不生成音频（`refine prepare` 是计划和证据，不是处理）
- 不声称"更好听"或"已完成"
- 不自动选择 Final candidate

## 9. 歌词证据适配器

`OnePointSpec.lyrics` 是可选引用。适配器在 PPE 之前执行权利、
路径、文件类型、大小、UTF-8 和 NUL 检查，然后只产生确定性结构
事实。授权不明时不读取正文；人工声明与 `must_avoid` 出现词汇张力
时进入 `NEEDS_EVIDENCE`，不修改原合同。

歌词正文不进入 CLI、`result.json` 或默认摘要；它只保存在可审计
`evidence/lyrics/` 中，并由 `package_manifest.json` 覆盖。
