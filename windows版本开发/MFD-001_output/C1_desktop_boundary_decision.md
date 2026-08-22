# Desktop 工程边界决策 (MFD-001 阶段 C 输出)

**日期:** 2026-08-20
**决策基于:** 仓库真实证据 + 工程约束分析

---

## C1. 仓库策略决策

### 方案评估

| 方案 | 描述 | 优势 | 劣势 | 评估 |
|---|---|---|---|---|
| A: `moodify-ai/apps/desktop` | Monorepo 内 | 统一管理、共享配置 | Node/Python 混合、CI 复杂、体积增长 | ⚠️ 可行但不够干净 |
| B: **独立 `moodify-desktop`** | 独立仓库 | 清晰边界、独立发布、Node 生态原生 | 跨仓库协调 | ✅ **推荐** |
| C: 其他结构 (workspace 等) | 混合方案 | 灵活性 | 复杂度增加 | ❌ 过度工程 |

### 最终决策: **方案 B — 独立 `moodify-desktop` 仓库**

#### 理由:

1. **技术栈隔离**
   - Desktop: Electron + TypeScript + React + Vite + Forge (纯 Node 生态)
   - 主仓库: Python 核心 + Android Kotlin + Web JS
   - 混合会导致依赖管理混乱

2. **发布周期独立**
   - Desktop 可能有频繁的 alpha 发布
   - 不应受主仓库分支策略影响
   - 独立 versioning 和 changelog

3. **CI/CD 简化**
   - Desktop 构建: Node + Electron Forge → Windows installer
   - 主仓库 CI: Python tests + Android gradle
   - 混合会增加 CI 复杂度和时间

4. **Secrets 边界清晰**
   - Desktop 不需要 Python 依赖或数据库访问
   - 独立仓库减少误用风险

5. **协作友好**
   - Desktop 开发者不需要 checkout 整个 monorepo
   - PR 更聚焦

6. **GPL 兼容**
   - 独立仓库可明确 license 边界
   - Desktop 前端代码可能采用不同 license 策略

7. **未来 macOS/Linux 扩展**
   - 独立仓库更容易支持多平台
   - 不影响主仓库结构

#### 仓库关系

```text
huliye24/moodify-ai (主仓库)
    │  ← 引用: API 文档、Track schema、BFF 端点规范
    │
    └── depends on (运行时): moodify-music-bff
         ↑
         │ HTTP API (公开)
         │
huliye24/moodify-desktop (新仓库)  ← 本任务建立
    │
    ├── Electron + TypeScript + React
    ├── Vite + Forge
    └── 仅依赖 BFF 公开 API
```

---

## C2. Desktop 责务边界

### Desktop SHOULD (必须做)

- [x] 启动 Moodify 应用
- [x] 用户认证 (Alpha 阶段可能简化)
- [x] 获取用户可见音乐 (via BFF)
- [x] 请求 playback manifest/resource (via BFF)
- [x] 播放音频 (Chromium `<audio>` / Web Audio API)
- [x] Pause / Seek / Next / Previous 控制
- [x] 显示最少必要信息 (曲目名、艺术家、进度)
- [x] 保存客户端本地状态 (音量、窗口位置、最后曲目)
- [x] 处理网络与播放错误
- [x] 后续支持 Windows system integration (Tray, Media Controls)

### Desktop SHOULD NOT (禁止做)

- [ ] 成为 Ear 或执行听觉分析
- [ ] 在 renderer 中执行重型音频处理
- [ ] 保存内部 service key 或 token
- [ ] 直接连数据库 (PolarDB/SQLite)
- [ ] 复制 Cloud 业务状态机
- [ ] 创建第二套 track authority
- [ ] 暴露 stems / internal judgment / processing graph
- [ ] 在首版承担训练或模型推理
- [ ] 在首版实现复杂 DSP / WASAPI / ASIO
- [ ] 在首版实现皮肤市场 / 社区 / 歌词

---

## C3. 边界接口草案 (供 MFD-003 确认)

### Desktop → Cloud 接口

```text
Desktop (Electron App)
    ↓ typed HTTPS (via service layer)
Public Player API / BFF (:8100)
    ↓ internal
Moodify Music Services
```

### 核心资源 (MFD-003 必须确认)

| Resource | 当前状态 | 优先级 |
|---|---|---|
| **Session** | MISSING (Alpha 可能不需要) | P2 |
| **Library** | PARTIAL (catalogue 存在) | P1 |
| **Track** | ✅ EXISTS (`/tracks/{id}`) | **P0** |
| **PlaybackManifest** | ⚠️ 需确认 (audioAssetKey?) | **P0** |
| **Queue** | MISSING (用 local queue) | P2 |
| **PlaybackError** | PARTIAL (ApiError 存在) | P1 |
| **ClientCapability** | ABSENT (未来预留) | P3 |

### 接口版本化

```
/api/v1/music/{resource}
```

Android 已使用此格式，Desktop 应保持一致。

---

## Open Questions (待解决)

| # | 问题 | 影响 | 计划解决于 |
|---|---|---|---|
| OQ-1 | audioAssetKey 如何转换为实际播放 URL? | **阻塞播放** | MFD-003 |
| OQ-2 | 是否需要用户认证? Alpha 策略? | 安全模型 | MFD-003 |
| OQ-3 | CORS 是否允许 Electron origin? | 开发/生产 | MFD-003 |
| OQ-4 | Media URL 是否 signed? 有过期时间? | 缓存策略 | MFD-003 |
| OQ-5 | Range request 是否支持? | Seek 功能 | MFD-004 |
| OQ-6 | 独立仓库的 GitHub 创建时机? | 工作流 | 即时 (MFD-002 前) |

---

## C4. 安全边界 (预定义)

```
Renderer Process
    ↓ 只通过 window.moodify bridge
Preload Script
    ↓ 白名单 IPC channels only
Main Process / Service Layer
    ↓ HTTPS (无 secret)
BFF Public API
```

禁止:
- Renderer → Node.js fs
- Renderer → process.env
- Renderer → raw ipcRenderer
- Main → database
- Main → internal API (service-key)

---

*本决策基于真实仓库证据。预期倾向（独立仓库）与证据一致，非迎合预设。*
