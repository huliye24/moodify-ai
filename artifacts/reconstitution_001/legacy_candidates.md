# Legacy Positioning Candidates

These are references to review, not automatic deletion targets.

- `docs/LEGACY_AND_EXPERIMENTAL_POLICY.md:41` — post-processing system
- `docs/engineer/2026-05-28/2026-05-28_高性能处理方案_HPSS频谱替代Demucs.md:5` — AI 音乐后处理是错误的技术选择。HPSS + M/S 频谱架构在速度上快 30-60 倍，在质量上可能更好。  ---  ## 0. 问题的重新定义  ### 0.1 不是「源分离」，而是「差异化处理」  Demucs 的设计目标是把混合音频分离成独立声部（人声/鼓/贝斯/其他），然后用户可以分别处理每个声部再混音。  但 Moodify 的真实需求不是「分离声部」，而是「对音频的不同成分施加不同的处理参数」。  这两个问题看似相同，
- `docs/xuanzhen/泫榛武器定理：强工具的秩序压制律.md:522` — AI 音乐的声学工程武器  Moodify 的价值不在于“再生成一首歌”，而在于把 AI 音乐从生成阶段推进到工业后期阶段。  它的核心链条是：  \[ \text{生成原声} \rightarrow \text{声学诊断} \rightarrow \text{频谱分析} \rightarrow \text{情绪判断} \rightarrow \text{二次处理
- `docs/xuanzhen/泫榛软件极限方程_三元核心式_Princeton_Style.md:345` — AI 音乐二次处理软件，该方程可以具体解释为：  $$ \mathcal{L}_{\mathrm{Moodify}} = \mathcal{T}_{\mathrm{audio}} \cdot \mathcal{E}_{\mathrm{processing}} \cdot \mathcal{U}_{\mathrm{creator}} $$  其中：  | 符号 | 含义 | |---|---| | $\mathcal{T}_{\mathr
- `moodify-core-package/src/moodify/cli.py:369` — AI 音乐二次处理
- `moodify-core-package/src/moodify/orchestration/workflow_engine.py:9` — AI 音乐特性。 """  import os import time import uuid import logging from pathlib import Path from datetime import datetime from dataclasses import dataclass, field from enum import Enum  import numpy as np import soundfile  l
