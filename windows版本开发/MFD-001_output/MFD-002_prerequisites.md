# MFD-002 前置条件 & 验收清单

**生成时间:** 2026-08-20
**来源:** MFD-001 完成输出

---

## MFD-001 Definition of Done 检查

| # | 完成条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 有真实仓库快照 | ✅ | `A1_repository_snapshot.md` |
| 2 | 有 identity conflict inventory | ✅ | `A2_identity_conflict_inventory.md` |
| 3 | 有 Android reuse map | ✅ | `A4_android_reuse_map.md` |
| 4 | 有 Desktop–Cloud readiness map | ✅ | `A5_desktop_cloud_readiness.md` |
| 5 | 根 authority 已与最新产品决策一致 | ✅ | 现有 AGENTS.md/README.md 已正确；Desktop 边界已定义 |
| 6 | 有新的 Moodify system boundary (v2) | ✅ | `B1_system_boundary_v2.md` |
| 7 | 有 Desktop responsibility boundary | ✅ | `C1_desktop_boundary_decision.md` C2 |
| 8 | 有 repo strategy decision | ✅ | `C1_desktop_boundary_decision.md` C1 → **独立仓库** |
| 9 | 有 open questions | ✅ | 6 个 OQ 已记录 |
| 10 | 有 MFD-002 prerequisites | ✅ | 见下方 |
| 11 | 没有新增 Electron 功能代码 | ✅ | 纯文档输出 |
| 12 | 没有修改生产环境 | ✅ | 只读调查 |
| 13 | 所有变更可被清楚审计 | ✅ | 全部 Markdown 文档 |

---

## MFD-002 前置条件

### 必须在 MFD-002 开始前完成

- [x] **MFD-001 = GO** — 本文档确认
- [x] **Desktop repository location 决策** → 独立 `moodify-desktop` 仓库
- [x] **License 确认** → GPL v3.0 (从主仓库继承或独立定义)
- [x] **Package manager** → npm (Node.js 生态)
- [x] **Node 版本策略** → 当前 v22.22.2 (managed)
- [ ] **创建独立仓库** `huliye24/moodify-desktop`
- [ ] **初始化 .git + README**

### 技术栈基线 (MFD-001 建议，MFD-002 执行)

```text
Electron (最新稳定版)
TypeScript
React
Vite
Electron Forge
npm
```

### 仓库位置

```
E:\moodify-desktop\   (新仓库根目录)
```

或 GitHub:
```
https://github.com/huliye24/moodify-desktop
```

---

## 给 MFD-002 的关键输入

### 从 MFD-001 继承的决策

1. **仓库结构:** 独立仓库（非 monorepo 子目录）
2. **技术栈:** Electron + TS + React + Vite + Forge
3. **安全模型:** contextIsolation + preload bridge + 无 renderer Node
4. **API 边界:** 仅 BFF 公开 API (`/api/v1/music/*`)
5. **不连接:** 内部 API、数据库、Ear、service-key

### 从 Android 继承的参考

1. **BFF Base URL:** `https://rongjinwenchuan.xyz/api/v1/music`
2. **核心端点:** bootstrap, catalogue, tracks/{id}
3. **数据模型:** Bootstrap, Catalogue, Track (含 audioAssetKey)
4. **错误模式:** ApiError with code/message

### MFD-003 待解决的问题 (不阻塞 MFD-002)

- audioAssetKey → 播放 URL 转换机制
- Auth 策略
- Signed URL / expiry
- CORS 配置

---

## 最终回报 (MFD-001)

### 1. 实际发现了什么

1. **仓库是 monorepo**，包含 Python core、Android、Web、BFF、文档
2. **产品身份已收敛**: Moodify Music/Player 对外，Ear 内部
3. **无现有 Desktop 代码** — 需要从零建立
4. **Cloud 状态**: 静态托管运行中，Ear 仅代码
5. **Android 是最佳参考实现** — BffClient.kt 清晰展示 API 用法
6. **BFF 公开 API 可用**: bootstrap/catalogue/tracks 已验证

### 2. 修改了什么

- **未修改任何源文件** (阶段 A 只读)
- **产出 6 个文档** 到 `windows版本开发/MFD-001_output/`

### 3. 新的权威结构

```
Moodify Player (对外)
├── Android (已有)
├── Web (已有)
└── Desktop/Windows (新建) ← 第三客户端，非第二产品

Moodify Ear (内部) ← serves Player internally
Moodify Cloud (基础设施) ← Player 与 Ear 之间
```

### 4. Desktop 放在哪里

**独立仓库: `huliye24/moodify-desktop`**
- 理由: 技术栈隔离、发布独立、CI 简化、secret 安全

### 5. Cloud / API 真实缺口

| 缺口 | 严重性 | 解决于 |
|---|---|---|
| Media URL 交付机制不明 | 🔶 HIGH | MFD-003 |
| Auth 策略未定 | ⚠️ MEDIUM | MFD-003 |
| CORS 未验证 | ⚠️ MEDIUM | MFD-003 |
| Queue endpoint 缺失 | ℹ️ LOW | MFD-004 (local queue) |

### 6. 阻塞 MFD-002 的项

- [ ] 创建 GitHub 仓库 `huliye24/moodify-desktop`
- [ ] 无其他阻塞 (MFD-002 可并行准备技术选型)

### 7. 验证结果

- ✅ 所有结论基于真实文件/代码/运行证据
- ✅ 未虚构能力
- ✅ 产品身份与现有 Canon 一致
- ✅ Desktop 定位清晰 (Player 客户端，非新产品)

### 8. Commit / Branch / Diff

- **无 commit** (纯只读调查 + 文档产出)
- **Branch:** `codex/moodify-classic-reconstruction-001` (读取)
- **Diff:** N/A (未修改仓库文件)

---

**MFD-001 结论: GO → 可以进入 MFD-002**
