# 重授权收尾审计（moodify-ai-relicense 补丁包 01）

日期：2026-08-09
背景：补丁包 01 为 2026-08-04 的重授权现场快照（HEAD=ea0e1c1 Apache 采用提交，已放置 GPL 文件）。当前仓库已于 0b355e7 完成 GPL-3.0-only 采用（PR #14），本审计为收尾清理。

## 1. 法律文件一致性（快照 vs 当前仓库）

| 文件 | 状态 |
|---|---|
| LICENSE | ✅ 一致（GPL-3.0 官方文本，仅行尾符差异） |
| COPYRIGHT | ✅ 一致 |
| SOURCE_HEADER.txt | ✅ 一致 |
| CONTRIBUTING_LICENSE.md | ✅ 一致 |
| TRADEMARKS.md | ✅ 一致 |
| OPEN_SOURCE_NOTICE.md | ⚠️ 有差异：快照为早期版（含 "Positioning: AI 的耳朵"）；当前保留补丁 03 的 **v1.0 更新版**（分节编号 + 边界声明更完整）——以 v1.0 为准 |

## 2. Apache-2.0 残留扫描与处置

### 已清理（Moodify 自身旧许可标注 → GPL-3.0-only）

| 文件 | 改动 |
|---|---|
| `capability_registry/adapters/lyric_align_adapter.py` | license_label `Apache-2.0 (internal)` → `GPL-3.0-only (internal)`（Moodify 自研 lyric_align） |
| `capability_registry/bootstrap.py` | lyric_align.core provider 同步改为 `GPL-3.0-only (internal)` |
| `capability_registry/adapters/basic_pitch_adapter.py` | docstring 澄清：Basic Pitch 为 Spotify AB 的 Apache-2.0 依赖（内部集成），Moodify 侧适配器代码 GPL-3.0-only |

### 历史文档（保留历史事实 + superseded 标注，不重写）

| 文件 | 处置 |
|---|---|
| `docs/PROJECT_STATUS_2026-06-04.md` | 头部加 Superseded 标注（Apache 表述为历史事实） |
| `docs/tasks/deepseek/DSK-MFY-SCORE-ENGINE-009/LICENSE_INTEGRATION_NOTE.md` | 头部加 Superseded 标注（重授权前隔离分析，结论已被取代） |

### 保留（提及第三方依赖许可，非残留）

- `basic_pitch_adapter.py` / `bootstrap.py` 中 Basic Pitch 的 `Apache-2.0 (internal)`（Spotify 依赖，正确）
- `AUDIO_TO_MIDI.md`、`CAPABILITY_ACCRETION_ARCHITECTURE.md`（第三方许可事实陈述）
- `docs/legal/GPLv3_VS_APACHE_2.0.md`、`README_LICENSE.md`（许可决策文档本身）
- `.venv-basic-pitch/`（第三方包安装目录，不入库）

## 3. 验证

- capability_registry 69 测试通过；ruff 干净；git diff --check 通过
- 全量回归：见测试记录（955 基线，本补丁改动为标签/文档级）
- 法律文件族完整：根 6 件 + docs/legal 4 件（03 补丁落地）

## 4. 结论

重授权（Apache-2.0 → GPL-3.0-only）**收尾完成**。仓库自身代码无 Apache 残留标注；历史文档保留并标注 superseded；第三方依赖许可如实记录（THIRD_PARTY_NOTICES.md）。
