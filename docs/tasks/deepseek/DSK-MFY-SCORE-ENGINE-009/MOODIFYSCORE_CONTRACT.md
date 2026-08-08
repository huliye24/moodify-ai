# MoodifyScore v0.1 合同（Stage 0 冻结）

**冻结日期：** 2026-08-02  
**版本：** `moodifyscore/0.1`  
**变更流程：** 任何变更必须经 STAGE 门禁评审并更新本文件版本号。

## 1. 身份与事实源

1. MoodifyScore 是 Moodify 持有曲谱语义、来源、置信度、修订和后端证据的内部事实源。
2. `.mscz`、MusicXML、PDF、SVG 都不是内部事实源；MusicXML 只是可交换导出格式。
3. MoodifyScore 必须不依赖任何具体渲染后端；同一份 MoodifyScore 可进入多个后端。
4. 原始演奏事实、曲谱解释和视觉排版必须分层保存，不得混淆。

## 2. 顶层结构（canonical JSON）

```text
MoodifyScore v0.1
├── schema_version         固定 "moodifyscore/0.1"
├── score_id               稳定 ID（内容派生，同输入双运行一致）
├── revision               修订号 + revision_note
├── metadata               title / composer / lyrics / language / comments / source_label
├── source_assets          [ {kind, path, sha256, role} ]  源 MIDI 等只读资产
├── timeline               tempo_map / time_signature_map / key_map
├── parts                  [ Part ]
├── lyrics_references      [ {part_id, measure_index, note_slot, text, source, status, confidence} ]
├── evidence               { import: {...}, export: {...}, roundtrip: {...} }
└── schema_meta            { unknown_fields_rejected, strict: true }
```

## 3. 核心元素合同

### Part
| 字段 | 类型 | 说明 |
|---|---|---|
| `part_id` | str | 稳定 ID（如 `P-1`） |
| `name` | str | 乐器/声部名 |
| `instrument` | str \| None | GM 乐器名或 None=unknown |
| `channel` | int \| None | MIDI channel（未知=null） |
| `program` | int \| None | GM program（未知=null） |
| `source_track` | int \| None | 源 MIDI track 号（未知=null） |
| `staves` | [Staff] | 至少一个 |

### Staff / Voice
| 字段 | 类型 | 说明 |
|---|---|---|
| `staff_id` | str | 稳定 ID |
| `clef` | str \| None | 推断时带 `source/status` |
| `voices` | [Voice] | 声部列表 |

### Voice（事件序列）
| 字段 | 类型 | 说明 |
|---|---|---|
| `voice_id` | str | 稳定 ID |
| `events` | [Event] | 严格有序 |

### Event（note / rest）
| 字段 | 类型 | 说明 |
|---|---|---|
| `event_id` | str | 稳定 ID |
| `event_type` | `"note"` \| `"rest"` | |
| `tick_start` | int | 原始 MIDI tick（保持原值） |
| `tick_end` | int | 原始 MIDI tick（rest 时 = tick_start） |
| `pitch_midi` | int | 仅 note；0-127 |
| `velocity` | int \| None | 仅 note；原始力度 |
| `duration_ticks` | int | tick_end - tick_start |
| `measure_index` | int \| None | 推断或来自拍号映射；未知=null |
| `position_in_measure` | int \| None | tick 粒度；未知=null |
| `ties` | [str] | 指向后续 note event_id 的 tie；无=[] |
| `source` | str | 如 `"midi_ingest"` |
| `status` | `"raw"` \| `"inferred"` \| `"confirmed"` | |
| `confidence` | float \| None | 0-1；raw 可 null |
| `inference_notes` | [str] | 推断说明（status=inferred 时） |

## 4. 时间线合同

| 映射 | 字段 | 说明 |
|---|---|---|
| tempo | `{tick, bpm}` 列表 | MIDI 节拍器事件；无则 `[]` + `tempo_known=false` |
| time signature | `{tick, numerator, denominator}` | MIDI 拍号事件；无则 `[]` + `time_signature_known=false` |
| key | `{tick, fifths, mode}` | 仅当源明确存在（MIDI 调号事件或已确认信息）；否则 `key_known=false`，**禁止推断** |

**规则：** 无法可靠推断的 key/voice/measure 保持 `null`/unknown/warning，不得为追求美观伪造音乐学结论。

## 5. 推断与置信度规则

1. 每个推断字段必须带 `source`、`status`、`confidence`。
2. `status` 只能是 `raw`（直接来自源）、`inferred`（算法推断）、`confirmed`（人工确认）。
3. 推断不得伪装人工确认；`confirmed` 只能来自显式人工输入（本任务无人工输入，因此不会出现）。
4. `inference_notes` 记录推断依据，便于审计。

## 6. 序列化与规范化

1. 严格类型 + 版本化 schema；**未知关键字段一律拒绝**（`strict: true`）。
2. canonical JSON：dict 键排序、稳定 ID 派生、无时间戳/绝对路径等非确定性内容进入内容指纹。
3. 同输入双运行：`score_id`、事件序列、JSON 内容（除显式标注的非确定性字段）必须一致。
4. 非确定性元数据（如 PDF 内嵌时间戳）不得进入 canonical JSON。

## 7. 输入/输出边界

1. MIDI ingest：读取原始 tick/time、track/channel/program、tempo/time signature；源 MIDI 只读，SHA-256 记录到 evidence。
2. 输出：canonical JSON（事实源）→ MusicXML（可交换）→ 后端渲染（PDF/SVG）。
3. MusicXML 不承载 Moodify 全部证据（evidence/revision/confidence 只属于 MoodifyScore）。
4. 覆盖输入 MIDI 是 P0 违规。

## 8. 版本与兼容

1. `schema_version` 语义化：同版本内只做向后兼容扩展；破坏性变更必须升主版本。
2. 旧版本 canonical JSON 必须仍可读取（容忍未知字段仅在旧版本文件上）。
3. 本任务实现范围：v0.1 最小集（上述字段）；超出范围的能力位冻结在能力矩阵，不实现。
