# Moodify 系统边界 (MFD-001 阶段 B 输出)

**版本:** 2.0 (含 Desktop)
**日期:** 2026-08-20
**CANON_CHANGE:** YES — 添加 Desktop 客户端边界
**Why:** 新增 Windows Desktop 作为第三客户端，需更新系统边界

---

## 产品权威结构

```text
Moodify
│
├── Moodify Player / Moodify Music (唯一对外产品面)
│   ├── Android          ← 已有 (apps/music-android)
│   ├── Web/PWA          ← 已有 (apps/music-web)
│   ├── Desktop
│   │   └── Windows      ← 本任务建立 (NEW)
│   └── iOS (future)     ── 远期规划，不在此任务范围
│
├── Moodify Cloud (生产基础设施)
│   ├── Playback services / BFF  ← moodify-music-package
│   ├── User / library services
│   ├── Media / processed assets
│   └── Internal orchestration
│       └── 状态: PARTIAL (静态托管运行中, Ear 生产流量待部署)
│
└── Moodify Ear (内部听觉智能系统)
    ├── Listen
    ├── Represent
    ├── Judge
    ├── Intervene
    ├── Verify
    └── Learn
    └── 状态: CODE ONLY (仓库完整, 云端无生产流量)
```

## 角色定义

### Moodify Player
**当前唯一对外产品面。** 用户只做 **PLAY**。

核心体验：
```
Source / Cloud-prepared Track → Moodify → PLAY
```

用户不需要理解 Ear、分轨、预设、Evidence 或状态机。

### Moodify Desktop (Windows)
**Player 的第三个客户端。** 不是第二个产品。

职责：
- 启动 Moodify
- 用户认证 (未来)
- 获取可见音乐
- 请求播放资源
- 播放 (Play/Pause/Seek/Next/Previous)
- 显示最少必要信息
- 保存客户端本地状态
- 处理网络与播放错误

**不是:**
- Ear 终端
- Cloud 管理界面
- 第二套数据权威
- 内部处理工作台

### Moodify Ear
**内部技术/研究/听觉智能系统。** 不构成公开产品面。

Ear 的研究价值保留：WSE/MSE/PPE、Evidence 体系、判断、验证、学习循环。

**产品层级:** Moodify contains Ear. Ear serves Player/Cloud internally.

### Moodify Cloud
**Player 与 Ear 之间的生产基础设施和服务层。** 不是用户产品品牌。

---

## "Preset" 表述修正

正确结构：

```
Auditory Intelligence / processing (内部)
        ↓
Playback Decision (内部)
        ↓
Track-specific Playback Result (内部)
        ↓
Play (用户体验)
```

"每首歌一个专属播放预设" 可以作为:
- ✅ 产品机制描述
- ✅ 阶段性工程表达
- ❌ 但不能覆盖 Moodify 的全部技术身份

对外体验简单；内部系统仍然复杂。

---

## 变更记录

| 字段 | 值 |
|---|---|
| CANON_CHANGE | YES |
| Why | 添加 Desktop (Windows) 作为 Player 客户端 |
| Affected files | AGENTS.md, README.md, PRODUCT_BOUNDARY.md (建议更新) |
| Migration | 无破坏性变更 — 纯添加 |
| Rollback | 移除 Desktop 相关段落即可 |

---

*本文档是 MFD-001 阶段 B 的核心输出，定义了 Desktop 在 Moodify 系统中的位置。*
