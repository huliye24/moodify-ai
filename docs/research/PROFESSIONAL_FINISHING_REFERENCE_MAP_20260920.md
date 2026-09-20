# Professional Finishing Reference Map — 2026-09-20

**Canon:** v2.0（Professional Finishing）
**性质：** 设计参考记录，不构成复制代码的指令。各项目许可证以仓库元数据为准，任何代码级复用前必须重新核验许可证与兼容性（仓库为 GPL-3.0）。

本文档记录为 Moodify 专业完成层方向评审过的外部 GitHub 项目。

| Project | What it demonstrates | Moodify lesson | License note observed during review |
| --- | --- | --- | --- |
| `spotify/pedalboard` | Python/C++ audio processing and VST3/AU hosting | Use mature effects as an execution layer; build planning/graph/verification above it（仓库现有 DSP 链已在此方向） | GPL-3.0 in GitHub metadata |
| `csteinmetz1/dasp-pytorch` | Differentiable EQ, compressor, reverb, stereo, style transfer and parameter estimation | Strong basis for automated but editable parameter search | Apache-2.0 per README |
| `adobe-research/DeepAFx` / `DeepAFx-ST` | Neural control of existing/black-box effects and production style transfer | AI should control familiar professional tools, not replace them with opaque audio generation | Adobe Research License; review before reuse |
| `nomadkaraoke/python-audio-separator` | Model-agnostic stem separation across MDX/VR/Demucs/MDXC/RoFormer, CLI/API and hardware fallbacks | Build a separation-provider interface rather than coupling to one model | MIT in GitHub metadata |
| `facebookresearch/demucs` | High-quality source separation | Important reference/model family; avoid sole dependency because upstream repo is archived | MIT; repository archived |
| `sergree/matchering` | Target + reference mastering workflow | Reference-guided finishing is intuitive; Moodify can expose the editable graph behind the result | Verify current package/repo license before code reuse |
| `Rikorose/DeepFilterNet` | Learned noise suppression / enhancement | Useful repair-stage deployment ideas; not a complete music-finishing solution | GitHub metadata reports non-standard/other; review required |
| `MTG/essentia` | Broad audio/music analysis and MIR | Useful vocabulary/feature reference for diagnosis and music understanding | AGPL-3.0 |
| `trummerschlunk/master_me` | Automatic mastering chain/plugin for streaming/podcast/radio | Useful mastering-chain and target-compliance patterns | GPL-3.0 |

## Architectural Conclusion

No single project above is the product Moodify wants to be.

The opportunity is the orchestration layer:

```text
Analyze
  ↓
Diagnose
  ↓
Plan
  ↓
Mix Graph
  ↓
Execute best available DSP / plugins / models
  ↓
Verify
  ↓
Human approval / Export
```

The replaceable algorithms are commodities. The durable asset is the professional decision representation, execution discipline, evidence, and accumulated workflow knowledge.

最值得技术团队深入研究的三件套：**dasp-pytorch + DeepAFx + Pedalboard** —— 三者拼起来即是 Moodify 新方向的技术哲学：AI 理解声音 → 决定应如何处理 → 寻找专业效果器参数 → 调用真实专业 DSP/Plugin → 工程师继续修改。
