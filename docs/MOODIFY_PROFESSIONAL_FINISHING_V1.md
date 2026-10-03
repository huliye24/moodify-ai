# Moodify Professional Finishing Architecture v1

**Date:** 2026-09-20
**Canon:** v2.0（Professional Finishing）
**Status:** **TARGET architecture — not runtime truth.** 本文件描述目标态；在 Mix Graph v0.1 工程包落地并有测试证据之前，不得在任何文档、README 或对外材料中写成已实现能力（R6/R10）。

## 1. Design Goal

Turn raw/generated audio into a professional, editable, verifiable production session rather than a black-box processed file.

产品命题：**Generated is not finished.** Moodify 的生产端不产出「一份不知道发生了什么的 wav」，而是产出可继续编辑的生产会话。

## 2. End-to-End Flow

```text
Input audio / stems / reference
            ↓
       Session Intake
            ↓
        Analysis Pack
            ↓
      Diagnosis Graph
            ↓
      User Intent Layer
            ↓
          Planner
            ↓
         Mix Graph
            ↓
     Processor Runtime
            ↓
       Candidate Render
            ↓
     A/B + Verification
       ↙             ↘
   Revise             Export
```

## 3. Mix Graph v0.1 Concept

A Mix Graph is a directed graph whose nodes represent sources, analyses, processors, buses, references and verification gates.

Illustrative JSON shape（示意，非冻结 schema；正式 schema 必须对照现有 evidence/contracts 设计后再冻结）：

```json
{
  "schema": "moodify.mix_graph.v0.1",
  "session_id": "...",
  "sources": [
    {"id": "mix", "kind": "stereo", "asset": "source.wav"}
  ],
  "intent": {
    "reference": null,
    "notes": "clearer vocal, preserve dynamics"
  },
  "nodes": [
    {
      "id": "eq-01",
      "type": "parametric_eq",
      "provider": "moodify.dsp",
      "enabled": true,
      "parameters": {},
      "reason": "diagnosis: spectral masking",
      "evidence_refs": []
    }
  ],
  "verification": [],
  "provenance": {}
}
```

每个节点至少携带：`processor` / `provider` / `parameters` / `reason` / `reference` / `enabled(bypass)` / `version` / `evidence` / `before/after`。

## 4. Processor Provider Interface

Each processor/provider should expose approximately:

```text
capabilities()
validate(parameters)
render(audio, parameters, context)
measure_cost()
provenance()
```

Learned models and external services should additionally expose model/provider version and fallback behavior.

## 5. Parameter Search

Three complementary strategies can coexist:

1. **Rule/heuristic initialization** from diagnosis（复用现有 v01_diagnostics → 干预规则路线）。
2. **Reference matching** against target/reference features（参考 matchering 的 Target + Reference → Master 工作流，但把可编辑图暴露出来）。
3. **Differentiable or black-box optimization** for supported processors（参考 dasp-pytorch 的可微 EQ / 压缩 / 混响 / stereo）。

用户看到的是选定的目标与 resulting parameters，不是不透明的「AI 置信度」。

## 6. Verification Contract

Every rendered candidate should be able to attach:

- input/source identity;
- graph version;
- processing provider versions;
- before/after loudness/peak/dynamics measurements;
- relevant spectral/stereo checks;
- constraint violations;
- machine uncertainty;
- human review state.

与现有 evidence 体系（treatment records、inspector、algorithmic review）对齐，不建第二套 evidence authority。

## 7. Non-destructive Editing

A graph node should support:

- enable/disable;
- bypass;
- parameter revision;
- provider replacement;
- branch/compare candidate;
- rollback to previous render.

## 8. UI Implication

The professional UI should revolve around:

- waveform/timeline;
- source/stem browser;
- diagnosis panel;
- Mix Graph / chain view;
- parameter inspector;
- A/B loudness-matched preview;
- revision history;
- verification/export panel.

This is closer to a professional finishing workbench than a streaming player. App/Player 端的 PLAY 不删除；A-B/Review/Delivery 由 Listener Side 接口承担（Canon v2.0）。

## 9. First Engineering Slice（Mix Graph v0.1）

Implement the smallest graph that can run the existing stereo analysis and controlled DSP path:

```text
Source → Analyze → EQ → Compressor → Stereo → Limiter → Verify → Export
```

Do not add more node types until this graph is serializable, replayable, bypassable and testable.

## 10. 位置定位

```text
Suno / Udio / AI Models
Human recording / DAW
          ↓
       MOODIFY（Professional Finishing）
          ↓
 Spotify / Apple Music
 Film / Game / Distribution
```

可替换的算法是 commodity；持久的资产是专业决策表示、执行纪律、证据与沉淀的工作流知识（见 reference map 文档结论）。
