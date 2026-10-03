# MOODIFY Studio Context 0.1 — `context.json` 与 `diagnosis.json`

**Status:** EXPERIMENTAL — 已实现，未冻结。桌面侧产物契约，不是网络协议。
**Date:** 2026-10-03
**Related:** [../canon/STUDIO_PRODUCTION_PIPELINE_V3.md](../canon/STUDIO_PRODUCTION_PIPELINE_V3.md) · [MOODIFY_SOUND_PROTOCOL_0_2.md](MOODIFY_SOUND_PROTOCOL_0_2.md)

这两个产物属于 **Studio 的流程层**，位于 Core 的 case 之下、不构成第二套 case 权威：

```text
<case>/                      ← Core 的 case（case.json / report.json / scan/ …）
  stems/ manifest.json       ← 分轨（桌面 dsp_separate.py 写）
  midi/  score/              ← 结构（basic-pitch / music21 写；无 manifest）
  studio/
    pipeline.json            ← 阶段记录（非权威，见 §3）
    diagnosis.json           ← 本文件 §2
    context.json             ← 本文件 §1
    plans/  versions/  verification/  selection.json  export/
```

---

## 1. `moodify.studio.context/0.1`

**用途：** 未来 AI 完成方案规划器的**唯一上下文入口**。
它**引用**其它产物，**不复制**；并且**只列真实存在的路径**——
上下文包引用一个不存在的文件，会让规划器对不存在的东西推理。

```json
{
  "schema": "moodify.studio.context/0.1",
  "case_id": "case_…",
  "generated_at": "2026-10-03T…Z",
  "source": "E:\\…\\song.wav",
  "analysis": {
    "report": "../report.json",
    "measurements": "../measurements.json",
    "evidence": "../evidence.json"
  },
  "diagnosis": "diagnosis.json",
  "stems": {
    "manifest": "../stems/manifest.json",
    "files": ["../stems/song__vocals.wav", "…"],
    "engine": "dsp_center_hpss",
    "engine_note": "非模型快速分离……不构成母带级分轨。",
    "grade": "PREVIEW_NOT_MASTERING_GRADE"
  },
  "midi":  ["../midi/song_basic_pitch.mid"],
  "score": ["../score/song_basic_pitch.musicxml"],
  "available_capabilities": [
    { "id": "existing-presets", "kind": "processing",
      "detail": "clean_master / warm_vocal / wide_space",
      "core_command": "moodify protocol process <job.json>", "stage": "FINISH" }
  ],
  "notes": ["…"],
  "readiness": { "stage": "SEPARATED", "finish_mode": "DEEP", "facts": { } }
}
```

**路径规则：** 全部相对于 `<case>/studio/`（`context.json` 所在处）。
所以 `../report.json` 就是 `<case>/report.json`。
有测试断言每一条被引用的路径都真实存在。

**`stems.grade` 恒定 `PREVIEW_NOT_MASTERING_GRADE`**：
下游消费者不得把预览级分轨误当母带级。`engine_note` **原样搬运**分离器对自己局限的陈述。

**`available_capabilities`** 只列 Studio **确实能调用**的能力，每项带真实 Core 命令。
列一个做不到的能力，会让规划器产出跑不了的方案。

**禁止：** 把原始音频字节放进上下文（§15）。只放路径与结构化摘要。

---

## 2. `moodify.studio.diagnosis/0.1`

**用途：** 把 Core 实际发现的东西整理成一份可读、可追溯的诊断。
它是 `report.json` 的**严格投影**：不重算阈值、不重导指标、不发明结论。

```json
{
  "schema": "moodify.studio.diagnosis/0.1",
  "case_id": "case_…",
  "generated_at": "…",
  "source_report": "report.json",
  "technical_state": { "…原样来自 report.json…" },
  "judgment_boundary": { "…原样…" },
  "issues": [
    {
      "id": "issue-001",
      "type": "TRUE_PEAK_MARGIN_EXCEEDED",
      "description": "true peak margin below 0.5 dB",
      "severity": "WARNING",
      "evidence": ["report.json#/findings/0"],
      "confidence": "measured",
      "metric": "true_peak_dbfs",
      "observed_value": 0.28,
      "unit": "dBFS",
      "calibration_status": "DEFAULT_UNCALIBRATED",
      "threshold_source_class": "DEFAULT",
      "check": "absolute_rule"
    }
  ],
  "draft_plan": { "status": "DRAFT_PLAN_NOT_EXECUTED", "nodes": [], "notes": [], "next_actions": [] },
  "preserve": [],
  "human_notes": [],
  "finding_rule_coverage": { "note": "…", "producible_codes": ["CLIPPING_PRESENT", "TRUE_PEAK_MARGIN_EXCEEDED"] }
}
```

### 规则

1. **每条 issue 的 `evidence` 是指向 `report.json` 的 JSON 指针**（`file#/a/b/0`），
   必须能解析回它来源的那条 finding。有测试断言这一点。
2. **测量值原样搬运**：`observed_value` / `calibration_status` / `threshold_source_class`
   不与 Core 产生分歧。`DEFAULT_UNCALIBRATED` 必须随行，
   以免消费者把未经感知校准的工程默认值当成已验证限值。
3. **`preserve` 默认为空数组。**「该保护什么」是**听觉判断**，
   属 `AGENTS.md` 保留给人类的范围。AI 不得自行填入猜测。
4. **`human_notes`** 只能由人的显式动作写入。

### 空诊断的含义（重要）

`issues: []` **不等于**音频没问题。Core 目前只能产出两种 finding，
且多数真实歌曲不产生任何 finding。因此 UI 必须显示
**「当前规则未发现技术问题」**，不得显示「这首歌没问题」。
`finding_rule_coverage.note` 随产物携带这句话。

---

## 3. `moodify.studio.pipeline/0.1`（记录，非权威）

```json
{ "schema": "moodify.studio.pipeline/0.1", "case_id": "…",
  "stage": "DIAGNOSED", "facts": { }, "history": [ { "stage": "ANALYZED", "at": "…" } ],
  "updated_at": "…",
  "note": "记录用，不是权威来源；阶段每次由磁盘产物重新推导。" }
```

读取时**永远重新推导**。这个文件只是让 case 留下「人做过什么」的可读痕迹，
目录列表本身表达不了这件事。有测试断言：删掉诊断产物后，
`pipeline.json` 里的旧 `stage` **不会**覆盖重新推导出的真相。

---

## 4. 版本与兼容

版本字符串精确匹配，不兼容的产物必须失败而不是被猜测成新格式
（沿用 MSP 0.1/0.2 的既有纪律）。0.1 为当前唯一版本。
