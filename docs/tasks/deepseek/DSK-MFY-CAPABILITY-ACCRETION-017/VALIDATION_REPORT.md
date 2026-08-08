# DSK-MFY-CAPABILITY-ACCRETION-017｜验证报告

**日期：** 2026-08-02 UTC

## 1. 测试结果

| 套件 | 结果 |
|---|---|
| `tests/capability_registry/`（新增 21 个） | **21/21 PASS** |
| Ruff（src + cli.py + tests） | clean |
| CLI smoke：`capability list / probe / regenerate` | 正常 |
| 旧 CLI 回归：`score backends`、`transcribe --help` | 无回归 |

## 2. 探测器实测（2026-08-02）

| 工具 | found | version | 负面知识 |
|---|---|---|---|
| musescore | ✅ | 4.5.1 | 3 条（单 -o / 无 -I / SVG 页码） |
| ffmpeg | ✅ | 8.1.1 | — |
| ffprobe | ✅ | 8.1.1 | — |
| sox | ✅ | 14.4.2 | 1 条（位深精度） |
| rubberband | ✅ | 4.0.0 | 1 条（sndfile.dll） |
| audacity | ✅ | v3.7.3 | 1 条（GUI/headless 未假定） |
| basic_pitch | ✅ | 0.4.0 | 3 条（Demucs / ground truth / drums） |
| moodify_self | ✅ | — | 2 模块存在 |

## 3. 注册表内容

- 7 能力合同（media.transcode/probe、notation.render、audio.time_stretch/
  measure_loudness、audio.separate_manifest、waveform.region_edit）
- 7 provider，全部 active；许可证/版本/路径/哈希事实真实
- `capability_registry.json` 生成并 round-trip 校验通过

## 4. 失败矩阵

| 场景 | 期望 | 实测 |
|---|---|---|
| 非法 manifest 字段 | ValueError（未知键拒绝） | ✅ 测试通过 |
| 非法 schema_version | ValueError | ✅ |
| 非法 provider status | ValueError | ✅ |
| provider 缺失（如 Demucs） | known_missing 而非 active | ✅ 机制测试通过 |
| 探测可重复 | 两次探测一致 | ✅ |
| 双运行序列化一致 | 字节一致 | ✅ |

## 5. 未运行项（如实记录）

- 完整 Core 回归（179 个 Workspace v2 测试）未全量重跑——只新增 capability_registry/
  目录与 cli.py 追加子命令，未触碰 Core 实现；Codex 可全量验收。
- 真实工具调用（transcode/stretch/measure）属 018 Adapter 范围，本任务只探测不执行。

## 6. 过程中失败与修正（记入 FAILURE_LEDGER）

- ffmpeg/sox 探测失败 2 轮（winget 目录布局：`bin/` 与根目录差异、glob 通配符用法）→ 已修复
- `capabilities` 命令名与 cli_v2 冲突 → 改用 `capability`
- basic_pitch 版本探测取到 WARNING 行 → 改用 importlib.metadata
- moodify_self 路径层级错误 → 修正 parents[1]
