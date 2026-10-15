# Wavefield Core Principle — From Waveform to Wavefield

**Status:** CANON  
**Human decision:** 2026-10-06  
**CANON_CHANGE:** YES

## Core thesis

> **Moodify 的核心技术方向是：从波形到波场。**

数字音频文件不是最终的声音，而是触发声音发生的条件。传统音乐软件主要修改 waveform；Moodify
把 waveform 置入一个明确描述、可重放、可验证的 wavefield，使声音在空间中发生，再由 Judge 判断
该波场是否改善了听感、保护了作品身份并能在目标播放条件下成立。

```text
Waveform
  → HEAR: source evidence
  → Wavefield Model: space / transducer / listener / propagation conditions
  → Render or physical reproduction
  → HEAR: reproduced-field evidence
  → JUDGE: source ↔ field ↔ perception
  → ACT: revise field or keep original
  → Wavefield Profile + renders + evidence
```

`Moodify Judge` 仍是核心模型与唯一判断权威；Wavefield 是核心技术对象和处理范式。二者不冲突：
Wavefield 使声音成为可观测、可干预的场，Judge 决定哪个场值得采用。

## Core formula

Moodify 在巨大的声学空间中寻找最适合当前音乐与目标播放条件的场。白皮书的北极星公式为：

\[
F^\* = \arg\max_F J\bigl(\operatorname{Render}(Audio, F)\bigr)
\]

- \(Audio\)：不可变的原始音乐；
- \(F\)：候选 Wave Field，包括模拟空间或已校准的真实重放空间；
- \(\operatorname{Render}\)：使音乐在该场中发生的模拟渲染或物理重放；
- \(J\)：Moodify Judge；
- \(F^\*\)：在声明条件与证据范围内的佳波场。

生产工程采用受约束、跨目标条件的形式：

\[
F^\* = \arg\max_{F \in \mathcal{F}_{feasible}}
\mathbb{E}_{c \sim \mathcal{C}_{target}}
\left[J\left(\operatorname{Render}(Audio,F;c), Audio, Intent\right)\right]
\]

subject to：identity preservation、loudness-matched comparison、reproduction safety、evidence completeness、
reproducibility，以及 human authority。\(J\) 在完成校准前不是可任意合并的单一真理分数；多目标权重与
“什么叫更好听”由人类治理。若所有可行 \(F\) 均不优于原始播放基线，结果必须是 `KEEP_ORIGINAL`，
而不是强行选择一个波场。

## Canonical object

一次 Wavefield Session 至少必须描述：

- `source`：不可变的输入音频与 provenance；
- `field_target`：目标空间、尺度、监听位置和意图；
- `reproduction_chain`：渲染器或真实扬声器/房间/采集链；
- `field_parameters`：几何、传播、反射、衰减、相位、声道/对象布局等可重放参数；
- `observations`：时间–频率、能量、相位/相干、空间采样和不确定性；
- `judge_before` / `judge_after`：为什么尝试、是否净改善、保护了什么；
- `outputs`：Wavefield Profile、面向明确播放条件的 render、证据和回退路径。

“找到佳波场”不是无条件求最大值。`best` 必须相对于作品意图、目标播放条件、保护约束和人工听审
定义；证据不足时返回 `HUMAN_REQUIRED` / `INCONCLUSIVE`，净增益为负时保留原版。

## Physical truth boundary

- 单个 mono/stereo 文件只能支持 source-field 与 stereo-field **projection**，不能证明真实三维声压场。
- 真实空间重现需要已校准的扬声器/房间、测量麦克风、双耳头或麦克风阵列，以及位置与环境元数据。
- 一个 stereo render 不能把某个房间的物理波场普遍“保存”到所有设备。可保存的是可重放的
  `Wavefield Profile` 与针对特定条件的 binaural / stereo / multichannel / object-based renders。
- 模拟、实测和推断必须分层标记；不得把可视化或生成结果冒充测量事实。

## Repository migration

### Keep and promote

- auditory analysis、WSE、phase/coherence、evidence、uncertainty、playback profiles；
- Judge Before / Judge After、A/B/ORIGINAL、human review、provenance；
- Mix Graph 的可编辑、可旁路、可回退能力。

### Reframe

- DSP / mixing / spatial / mastering：从“修改波形”改为 Wavefield ACT 的可替换 operators；
- playback/device adaptation：从消费端附属能力提升为 field realization；
- Studio：从处理步骤界面转向 `source → observable field → judged field` 工作台。

### Stop expanding

- 没有目标播放条件、空间模型和处理后验证的黑箱成品处理；
- 只输出漂亮频谱、但不能追溯数据与坐标的装饰性可视化；
- 将单文件立体声投影宣传成真实三维声场；
- 为追求“空间感”而重新引入不可归因 preset 产品面。

### Build next (not yet implemented)

1. Wavefield vocabulary and observation schema（MIP required）。
2. Deterministic Wavefield Profile and render contract。
3. Stereo projection baseline + binaural reference renderer。
4. Calibrated studio capture experiment：digital source ↔ physical field ↔ human blind review。
5. Judge calibration for field selection and cross-environment robustness。

## Rollback

若受控实验不能证明 Wavefield 方法相对 source-only processing 有稳定净收益，回退本方向为 Research；
保留既有 Core、Judge、Protocol 与播放链，不删除历史或伪造成功证据。
