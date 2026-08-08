# DSK-MFY-CAPABILITY-ACCRETION-018 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 三阶段状态

| Stage | 状态 |
|---|---|
| Stage A（Adapter Protocol 与基类） | PASS |
| Stage B（六个适配器） | PASS |
| Stage C（CLI、验证与文档） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## CLI

```powershell
py -3.11 -m moodify.cli capability adapters                    # 列出 provider 适配器与可用性
py -3.11 -m moodify.cli capability invoke --provider ffmpeg.cli \
    --input source=a.wav --parameter format=flac --output-dir out  # 显式受控调用
```

## 交付物

| 位置 | 内容 |
|---|---|
| `moodify-core-package/src/moodify/capability_registry/adapters/` | base（Protocol/结果/错误分类/受控执行）+ 6 适配器 + cli |
| `moodify-core-package/src/moodify/cli.py` | `capability adapters` / `capability invoke` 挂载 |
| `moodify-core-package/tests/capability_registry/test_adapters.py` | 15 个适配器测试 |
| `docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md` | Adapter 层状态更新（见下） |
| `docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-018/` | PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF |

## Adapter 清单（实测 2026-08-02）

| provider | capability | 可用 | 版本 | 真实 E2E |
|---|---|---|---|---|
| musescore.cli | notation.render | ✅ | 4.5.1 | PDF ✅ |
| ffmpeg.cli | media.transcode | ✅ | 8.1.1 | FLAC ✅ |
| ffprobe.cli | media.probe | ✅ | 8.1.1 | JSON ✅ |
| sox.cli | audio.measure_loudness | ✅ | 14.4.2 | stats ✅ |
| rubberband.cli | audio.time_stretch | ✅ | 4.0.0 | WAV ✅ |
| audacity.cli | waveform.region_edit | ❌ human_handoff | v3.7.3 | 如实降级 |
| basic_pitch.moodify | audio.separate_manifest | ✅ | 0.4.0 | 接口包装（未跑推理） |

## 关键决策

- **provider 名不泄漏**：上层只见 capability contract；provider 知识全部在
  adapter 内（Law 5）。
- **009 知识组合而非修改**：MuseScoreAdapter 内置单 `-o`/无 `-I`/SVG 页码
  失败模式，未 import 009 实现；009 musescore_backend 未被触碰。
- **Audacity 诚实降级**：headless 未实现 → 恒返回 unavailable +
  human_handoff + policy_rejection，不伪造自动化。
- **BasicPitchAdapter 是唯一允许 import 008 的内部适配器**（Apache-2.0 内部能力）。
- 统一错误分类：invalid_input / provider_defect / environment_failure /
  timeout / partial_output / policy_rejection（论文 Gate 8）。
- 所有外部调用 argv 数组、超时、stdout/stderr、版本、命令、输入/输出哈希入
  evidence；输出目录全新/为空，拒绝覆盖与路径逃逸。

## 验证摘要

- 36/36 capability_registry 测试 + 55/55 score_engine 回归；Ruff clean。
- 5 个真实工具端到端成功（合成 fixture）；audacity 如实 UNAVAILABLE。
- 失败矩阵：超时/非零退出/输入缺失/目录非空/argv 安全/单 -o 均有测试。

## 限制（事实边界）

- Audacity 自动化未实现（human_handoff，需人工操作或未来 headless 验证）。
- BasicPitch 真实推理未跑（耗时，008 已验证底层；Codex 可自行执行）。
- 179 个 Workspace v2 全量回归未跑（未触碰 Core 实现）。
- 每适配器错误翻译已统一分类，但跨 provider 的语义等价映射是 019 的
  Envelope/Record 工作，不在本包。

## Codex 验收命令

```powershell
py -3.11 -m pytest tests/capability_registry/ -v
py -3.11 -m moodify.cli capability adapters
py -3.11 -m moodify.cli capability invoke --provider ffprobe.cli --input source=<wav> --output-dir <newdir>
py -3.11 -m moodify.cli capability invoke --provider audacity.cli --input source=x.wav --output-dir <newdir>  # 应返回 human_handoff
py -3.11 -m moodify.cli score backends   # 旧 CLI 回归
py -3.11 -m moodify.cli transcribe --help
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
