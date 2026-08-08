# Round-Trip 损失合同（Stage 0 冻结）

**冻结日期：** 2026-08-02  
**版本：** `roundtrip/0.1`

## 1. 定义

round-trip 指：`源 MIDI → MoodifyScore → MusicXML →（MuseScore 后端）→ 重新解析`
过程中，每个阶段保留/丢失的信息。损失合同定义**哪些字段必须守恒、哪些允许
告警损失**，并强制差异可见。

## 2. 必须守恒字段（P0，loss 报告为 `preserved`）

| 字段 | 说明 |
|---|---|
| part 数量与 part_id 顺序 | MusicXML part 列表与 MoodifyScore parts 一一对应 |
| measure 数量与顺序 | 每 part 的 measure 序列一致 |
| note pitch（MIDI 0-127） | 重解析后的音高与源一致 |
| note duration（tick 相对时长） | 允许因分辨率/量化产生微小误差，误差必须报告 |
| tempo 映射 | 重解析的 BPM 序列与源一致 |
| time signature 映射 | 重解析的拍号序列与源一致 |
| note 相对顺序 | 同 voice 内事件顺序一致 |

## 3. 允许告警损失（loss 报告为 `warning`，不得静默）

| 字段 | 类型 | 说明 |
|---|---|---|
| velocity | warning | 排版层可能归一化；数值差异报告 |
| tick 绝对精度 | warning | MusicXML divisions 量化导致的 tick 误差报告 |
| tie 跨小节表示 | warning | 不同引擎表示法差异，但连接关系必须可推导 |
| voice 划分 | warning | 后端可能合并/重排 voice；差异报告 |
| measure 边界（无拍号时） | warning | 无拍号时 measure 推断属未知，报告 `unknown` |

## 4. 禁止隐藏的损失（P0 违规）

1. 重解析后 part/measure/note/pitch/duration/tempo 关键差异**不写入**
   `roundtrip_report.json`。
2. 后端非零退出码、超时、stderr 非空却报告"成功"。
3. 后端缺失却报告可用；`UNAVAILABLE` 必须显式。
4. 为追求一致而**修改源 MIDI**（源 MIDI 只读，SHA-256 不变是 P0）。

## 5. roundtrip_report.json 结构

```json
{
  "schema": "roundtrip/0.1",
  "source": {"path": "...", "sha256": "...", "backend": "midi_ingest"},
  "stages": [
    {"stage": "midi_to_score", "status": "preserved", "losses": [], "warnings": []},
    {"stage": "score_to_musicxml", "status": "preserved", "losses": [], "warnings": []},
    {"stage": "musicxml_reparse", "status": "preserved", "losses": [], "warnings": [...]}
  ],
  "comparison": {
    "parts": {"matched": 3, "mismatched": 0},
    "measures": {"matched": 64, "mismatched": 0},
    "notes": {"matched": 480, "mismatched": 0, "pitch_mismatch": 0, "duration_epsilon": 12},
    "tempo": {"matched": true},
    "time_signature": {"matched": true}
  },
  "verdict": "PASS | WARNINGS | FAIL"
}
```

## 6. 判定规则

| verdict | 条件 |
|---|---|
| PASS | 无 warning、无 loss |
| WARNINGS | 仅存在允许类损失（§3），关键字段守恒 |
| FAIL | 关键字段（§2）不守恒或 §4 任一项 |

**round-trip 结果必须对用户可见**：CLI 输出 verdict 与 warning 摘要；manifest
包含完整报告路径。关键语义损失被隐藏 = P0 失败 = HOLD。
