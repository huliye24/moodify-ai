# Capability Accretion Architecture

**Status:** v0.1 — Phase 1-5 全部实现（Registry/Adapter/Approved Execution/Validation/Knowledge Feedback）(DSK-MFY-CAPABILITY-ACCRETION-017~021, 2026-08-02)

## 原点

Moodify 吸收的是能力，不是接口；注册的是合同，不是品牌。外部工具提供执行，
Moodify 保留发现、执行授权、解释、编排与知识积累五种权力。本文档描述
六层架构与当前实现状态；未实现层只冻结能力位，不创建假实现。

## 六层架构与实现状态

```text
+-------------------------------------------------------+
| Moodify Experience Layer        （设计，未实现）      |
| Case UI | CLI v2 | Production Console | Review UI    |
+-------------------------------------------------------+
| Production Authority Layer      （既有：cli_v2 case） |
| State machine | Approval | Policy | Evidence | Audit  |
+-------------------------------------------------------+
| Workflow and Decision Layer     （本系列已实现）      |
| Planning | Routing | Candidate | Recovery             |
|   ├ ApprovedExecutionEnvelope（019，签名不可变）      |
|   ├ ExecutionGateway（019，唯一执行入口）             |
|   ├ ExecutionRecord（019，全量证据落盘）              |
|   ├ ValidationRule（020，带地质来源）                 |
|   ├ Candidate/Ranker/RejectionReason（020）           |
|   ├ Measurement/Judgment/NegativeKnowledge（021）     |
|   └ PolicyLedger/RuleChangeProposal（021）            |
+-------------------------------------------------------+
| Capability Contract Layer       （本任务已实现）      |
| media.transcode/probe | notation.render | time_stretch |
| measure_loudness | separate_manifest | region_edit     |
+-------------------------------------------------------+
| Provider Adapter Layer          （本任务已实现）      |
| MuseScore | FFmpeg/ffprobe | SoX | RubberBand |      |
| Audacity(human_handoff) | BasicPitch(内部)            |
+-------------------------------------------------------+
| External Capability World       （只读探测）          |
+-------------------------------------------------------+
```

## 已实现模块（Phase 1: Registry + Phase 2: Adapter）

| 模块 | 职责 |
|---|---|
| `capability_registry/model.py` | 严格类型模型：CapabilityContract / ProviderRecord / CapabilityRegistry；canonical JSON（键排序、未知键拒绝、schema_version 校验） |
| `capability_registry/detect.py` | 只读探测器 ×8（musescore/ffmpeg/ffprobe/sox/rubberband/audacity/basic_pitch/moodify_self）；版本探测、known_failure_modes（负面知识） |
| `capability_registry/bootstrap.py` | 从真实环境构建注册表；provider 缺失 = known_missing；负面知识必须非空 |
| `capability_registry/cli.py` | `moodify capability probe / regenerate / list`（注：`capabilities` 名已被 cli_v2 占用，注册表用单数） |
| `capability_registry.json` | 生成的注册表实例（7 能力 / 7 provider） |
| `capability_registry/adapters/base.py` | ProviderAdapter Protocol、AdapterResult、六类错误分类、受控进程基类（argv 数组/超时/evidence/路径防护） |
| `capability_registry/adapters/*.py` | 7 个适配器：MuseScore/FFmpeg/FFprobe/SoX/RubberBand/Audacity(human_handoff)/BasicPitch(内部 008) |

CLI 入口挂载于 `moodify.cli`（`moodify capability ...`，含 `adapters` / `invoke`）。

## 首批能力矩阵（实测 2026-08-02）

| capability_id | provider | 状态 | 版本 | 许可（外部进程） |
|---|---|---|---|---|
| media.transcode | ffmpeg.cli | active | 8.1.1 | GPLv3/LGPL |
| media.probe | ffprobe.cli | active | 8.1.1 | GPLv3/LGPL |
| notation.render | musescore.cli | active | 4.5.1 | GPLv3 |
| audio.time_stretch | rubberband.cli | active | 4.0.0 | GPLv2 |
| audio.measure_loudness | sox.cli | active | 14.4.2 | LGPL |
| audio.separate_manifest | basic_pitch.moodify | active | 0.4.0 | Apache-2.0（内部） |
| waveform.region_edit | audacity.cli | active | v3.7.3 | GPLv2 |

未安装（known_missing 机制已就位）：Demucs 分离、Verovio/LilyPond/OSMD 后端。

## 负面知识（known_failure_modes，地质记录起点）

注册表从第一天携带真实失败史（来源：009/008 失败台账）：

- MuseScore：单 `-o` 限制、无 `-I` 参数、多页 SVG 页码后缀
- SoX：整数位深转换精度损失
- RubberBand：依赖同目录 sndfile.dll
- Audacity：GUI 应用，headless 自动化未假定可用（可能 human_handoff）
- Basic Pitch：Demucs 未装、无 ground truth、鼓轨 UNSUPPORTED

## 已实现模块（Phase 3: Approved Execution）

| 模块 | 职责 |
|---|---|
| `capability_registry/execution/envelope.py` | ApprovedExecutionEnvelope（不可变、输入哈希锁定、签名绑定）、ExecutionRecord、verify/sign |
| `capability_registry/execution/gateway.py` | 唯一执行入口：签名验证→哈希重校验→权限（网络拒绝/绝对路径）→adapter→record 落盘；in-flight 追踪 |
| `capability_registry/execution/cli.py` | `capability plan / approve / execute` |

核心保证（实测）：篡改 envelope（含 output_dir 路径逃逸）在签名层被拦截，
无法到达 provider；未批准执行被拒绝；失败记录全量保留。

## 已实现模块（Phase 4: Validation & Candidate）

| 模块 | 职责 |
|---|---|
| `capability_registry/validation/rules.py` | ValidationRule（带 historical_source 地质记录）、RuleResult、ValidationReport；6 条通用规则全带真实来历；规则不可被 provider 关闭 |
| `capability_registry/validation/candidates.py` | CandidateSpec/Candidate（绑定独立 envelope）、CandidateRanker（accepted 优先）、RejectionReason（rule_id+measured+expected 结构化） |
| `capability_registry/validation/cli.py` | `capability validate`（ExecutionRecord 重放）、`capability candidates`（参数变体） |

## 已实现模块（Phase 5: Knowledge Feedback）

| 模块 | 职责 |
|---|---|
| `capability_registry/knowledge/records.py` | MeasurementRecord / JudgmentRecord / NegativeKnowledgeRecord + 追加式 KnowledgeStore（失忆防护） |
| `capability_registry/knowledge/policy.py` | RuleChangeProposal（不自动生效）+ PolicyLedger（版本化 + 地质引用）+ 样本门槛 N≥3 |
| `capability_registry/knowledge/cli.py` | `capability history / propose / policy` |

## 后续方向（系列外）

1. 知识循环与 019/020 的跨包自动编译（执行→测量→判断）接入真实生产案例。
2. 多 provider 候选/回退真实触发（第二 provider 环境）。
3. 与 moodify_runtime / cli_v2 case 系统的对接（需 SCOPE_CHANGE_REQUEST）。

## 限制（G-Boundary）

- Audacity headless 自动化未实现（human_handoff，如实降级）。
- BasicPitch 适配器已包装 008 接口，真实推理未在本包执行。
- 019 本地签名为模拟批准；真实人工审批签名机制是后续工作。
- 019 未接入 cli_v2 case 系统（编排明确不强行接入，独立最小证明）。
- 020 验证规则库为首批 6 条，按地质记录规则扩充；多 provider 候选/回退
  真实触发待第二 provider 环境。
- 021 知识记录按 record_id 与 019/020 关联（不重复存储）；跨包自动编译
  与真实数据积累留给后续集成。
- provider 名禁止出现在上层工作流（Law 5）——adapter 层已隔离。
- 能力矩阵基于本机环境；环境变化需重新 `capability regenerate`（探测只读）。
- `moodify capability list` 读取的是 `capability_registry.json` 快照，不是实时探测；
  实时状态用 `capability probe`。
