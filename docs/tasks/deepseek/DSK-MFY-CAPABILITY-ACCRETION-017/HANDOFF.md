# DSK-MFY-CAPABILITY-ACCRETION-017 HANDOFF

**Status:** READY_FOR_CODEX_REVIEW  
**Worker:** DeepSeek | **Date:** 2026-08-02 UTC  
**Branch:** `codex/mainline-cloud-dev-20260603` | **HEAD:** `df3a8a3c`（未提交新 commit）

## 四阶段状态

| Stage | 状态 |
|---|---|
| Stage A（Registry 模型与 schema） | PASS |
| Stage B（环境探测器） | PASS |
| Stage C（首批能力注册） | PASS |
| Stage D（验证与文档） | PASS |

最终判定：**READY_FOR_CODEX_REVIEW**（本 Worker 不得宣布 ACCEPT）。

## CLI

```powershell
py -3.11 -m moodify.cli capability probe      # 只读探测本机工具 + 负面知识
py -3.11 -m moodify.cli capability regenerate # 从环境事实重建注册表 JSON
py -3.11 -m moodify.cli capability list       # 列出能力/ provider/状态
```

注：`capabilities` 命令名已被 cli_v2 占用（既有静态清单，未触碰）；注册表用单数 `capability`。

## 交付物

| 位置 | 内容 |
|---|---|
| `moodify-core-package/src/moodify/capability_registry/` | model / detect / bootstrap / cli |
| `moodify-core-package/src/moodify/cli.py` | 追加 `capability` 子命令 |
| `moodify-core-package/tests/capability_registry/` | 21 个测试 |
| `moodify-core-package/capability_registry.json` | 注册表实例（7 能力 / 7 provider） |
| `docs/architecture/CAPABILITY_ACCRETION_ARCHITECTURE.md` | 六层架构 + 实现状态 |
| `docs/tasks/deepseek/DSK-MFY-CAPABILITY-ACCRETION-017/` | 三件套 + PROGRESS/VALIDATION/FAILURE_LEDGER/HANDOFF |

## 注册结果（实测）

- 8 个探测器全部工作：musescore 4.5.1 / ffmpeg 8.1.1 / ffprobe 8.1.1 / sox 14.4.2 /
  rubberband 4.0.0 / audacity v3.7.3 / basic_pitch 0.4.0 / moodify_self。
- 7 个能力合同 + 7 provider 全部 active；许可证/版本真实记录。
- **负面知识（known_failure_modes）从第一天携带**：MuseScore 单 -o/无 -I/SVG 页码、
  SoX 位深、RubberBand dll、Audacity GUI、Basic Pitch 无 Demucs/无 ground truth/鼓轨
  ——来源 009/008 失败台账（地质记录起点，PR-007/EX-011 落地）。

## 验证摘要

- 21/21 测试 PASS；Ruff clean；旧 CLI（score/transcribe）无回归。
- 失败矩阵：未知字段拒绝、schema 校验、known_missing 机制、探测可重复、
  双运行一致——全部有测试。
- 未运行：179 个 Workspace v2 全量回归（未触碰 Core 实现）；真实工具调用属 018。

## 关键决策

- 注册表 = FAILURE_LEDGER 的可引用摘要层（017 已与 022 知识层对齐：
  EX-009/EX-011/EX-012 经验已落地为 known_failure_modes 与探测要求）。
- provider 名未出现在任何上层业务逻辑（本阶段无上层，018 强制执行 Law 5）。
- `capability list` 读快照、`capability probe` 实时探测——两者职责分离。

## 限制（事实边界）

- 本阶段只注册与探测，不执行任何加工（adapter 属 018）。
- 能力矩阵基于本机环境；环境变化需 `capability regenerate`。
- Demucs/Verovio/LilyPond/OSMD 保持 known_missing/能力位，不伪注册。

## Codex 验收命令

```powershell
py -3.11 -m pytest tests/capability_registry/ -v
py -3.11 -m moodify.cli capability probe
py -3.11 -m moodify.cli capability list
py -3.11 -m moodify.cli capability regenerate
py -3.11 -m moodify.cli score backends   # 旧 CLI 回归
py -3.11 -m moodify.cli transcribe --help
```

DeepSeek Worker 停止于此。最终判定属于 Codex。
