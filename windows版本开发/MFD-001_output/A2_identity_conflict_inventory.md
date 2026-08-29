# MFD-001 产品身份冲突清单

**生成时间:** 2026-08-20
**任务:** MFD-001 阶段 A2 — 产品身份冲突搜索

---

## 冲突清单

| 文件 | 当前声明 | 权威级别 | 与 2026-08-20 人类决策冲突? | 建议 |
|---|---|---|---|---|
| AGENTS.md | Moodify Music / Player 对外；Ear 内部 | CANON | ❌ 不冲突 | 保持现状 |
| README.md | Moodify Music / Player 对外；Ear 内部 | CANON | ❌ 不冲突 | 保持现状 |
| docs/canon/PRODUCT_BOUNDARY.md | Moodify Music / Player 对外；Ear 内部 | CANON | ❌ 不冲突 | 保持现状 |
| docs/canon/CURRENT_CANON.md | 一致 | CANON | ❌ 不冲突 | 保持现状 |
| docs/brand/public/ | Moodify 品牌 | PUBLIC_BRAND | ❌ 不冲突 | 保持现状 |
| 历史文档 (实验图库等) | 可能包含旧 "Ear of AI" 表述 | HISTORICAL | ⚠️ 文字残留但已被 Canon 覆盖 | 标记为历史，不修改 |

## 关键概念搜索结果

| 概念 | 出现位置 | 当前用法 | 是否冲突 |
|---|---|---|---|
| "The Ear of AI" | 历史文档 | 已标记为失效的公开产品身份 | ❌ 已解决 |
| "Auditory Intelligence" | AGENTS.md, INTERNAL_SYSTEMS.md | 内部系统描述 | ❌ 正确 |
| "Moodify Ear" | 多处 | 内部系统名称 | ❌ 正确 |
| "Moodify Music" | AGENTS.md, README.md | 对外产品名 | ❌ 正确 |
| "Moodify Player" | AGENTS.md, README.md | 对外产品别名 | ❌ 正确 |
| "player" | Android/Web 代码 | 播放器实现 | ❌ 正确 |
| "music platform" | REPOSITORY_STATUS.md | 产品描述 | ❌ 正确 |
| "desktop" | 仅本任务包 | 待建立 | N/A |
| "windows" | 仅本任务包 | 待建立 | N/A |
| "android" | apps/music-android | 已有客户端 | ❌ 正确 |
| "preset" | core-package | 内部处理参数 | ❌ 正确（不对外） |
| "post-processing" | 历史文档 | 旧表述 | ⚠️ 被 "Classic Reconstruction" 替代 |
| "automatic mastering" | 历史文档 | 旧表述 | ⚠️ 被明确拒绝为产品身份 |
| "cloud" | 多处 | 生产基础设施 | ❌ 正确 |
| "BFF" | moodify-music-package | API 边界层 | ❌ 正确 |
| "playback" | Android/Web | 核心用户动作 | ❌ 正确 |

## 结论

**产品身份已完全收敛，无活跃冲突。**

关键裁决：
1. "The Ear of AI" 作为公开产品身份 → **已失效 (CD-001/CD-002)**
2. Moodify Music / Player → **当前唯一对外产品面**
3. Moodify Ear → **内部技术/研究系统**
4. preset/post-processing/automatic mastering → **内部机制，不构成产品身份**

Desktop 加入后应延续此结构：作为 Player 的第三个客户端（Windows），不创建新品牌。
