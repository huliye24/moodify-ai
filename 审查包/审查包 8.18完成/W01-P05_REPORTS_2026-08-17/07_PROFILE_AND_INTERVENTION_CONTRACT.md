# 07 — Profile & Intervention Contract

**W01-P05 · 2026-08-17**

## Profile / Preset 定位（§11）

用户不要求理解内部技术 preset。profile/preset 是**生产系统内部的处理决策对象**。

记录：profile_id / profile_version / reason / source judgment / parameters / chain reference / compatibility requirements。

**版本化强制**（TST-06）：修改参数必须 bump profile_version；禁止"改了 preset 仍用同一 version identity"。

## INTERVENE 输入/输出（§10）

输入：source/stems + judgment + profile + approved processing chain。
输出：transformed object(s) + processing manifest + parameter manifest + tool version + evidence refs。

## 现有实现基底（01 Capability Map）

- v01_presets：warm_vocal / clean_master / wide_space（CANONICAL_AVAILABLE）。
- processing/pedalboard_chain.MoodifyDSPChain + operators（参数化 DSP）。
- intervention 原语 3 个（EXPERIMENTAL，P07 评估）。
- reconstruction objective（INTERNAL，经典重建域，P05 主线不依赖）。

## 本包实现

- PROFILE stage：输出 profile 决策（id/version/params）到 StageResult.decision。
- INTERVENE stage：调用注入 renderer（profile 参数）；无 renderer 或 BYPASS → 不处理。
- profile_id/profile_version 进 production_fingerprint（参数变化 → 指纹变化）。
