# MOOD PORTAL 013 — Information Architecture (Bridge Build)

**Version:** 1.0（MOOD PORTAL 013 bridge, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [013_FINAL_REPORT.md](013_FINAL_REPORT.md) · [013_NAVIGATION_MODEL.md](013_NAVIGATION_MODEL.md) · [013_HUMAN_DECISION_REQUIRED.md](013_HUMAN_DECISION_REQUIRED.md)

---

## 1. 总 IA

```text
/
├── /world               MOOD WORLD Home         (PLANNED, placeholder only)
├── /protocol            Moodify Protocol Shell   (placeholder, module list only)
├── /portal              MOOD Portal              (visitor / connected state)
├── /library             MOOD Library             (Protocol docs, 014 fills content)
├── /me/library          User Music Library       (favorites / recent)
├── /network             placeholder              (Package 017)
├── /agents              placeholder              (Package 018)
├── /nodes               placeholder              (Package 019)
├── /governance          placeholder              (Package 020)
└── /treasury            placeholder              (Package 021)
```

## 2. 路由语义

| 路径 | 语义 | 来源 |
|---|---|---|
| `/` | Moodify Player 主页（PLAY-first user app） | 既有 `app/page.tsx` |
| `/world` | MOOD WORLD Home（PLANNED） | 013 新建 placeholder |
| `/protocol` | Moodify Protocol shell（10 模块列表） | 013 新建 placeholder |
| `/portal` | MOOD Portal（连接钱包后空间） | 013 新建 placeholder |
| `/library` | MOOD Library（协议文档馆） | 014 填充 |
| `/me/library` | 用户音乐库（收藏 / 最近） | 旧 `/library` 内容迁来 |
| `/network` | Network Observatory | 017 |
| `/agents` | AI Agents Registry | 018 |
| `/nodes` | Nodes Registry | 019 |
| `/governance` | MIP Governance | 020 |
| `/treasury` | Treasury & Transparency | 021 |

## 3. URL 移交：旧的 `/library` → 新的 `/me/library`

| 项 | 旧值 | 新值 |
|---|---|---|
| 路径 | `/library` | `/me/library` |
| 用途 | 用户音乐收藏 | 用户音乐收藏 |
| 模板 | `apps/web/app/library/page.tsx` | `apps/web/app/me/library/page.tsx` |
| 历史 | 保留 | 由 `git mv` 保留 |

原因：`/library` 现在承担协议文档馆入口，与 014 任务书一致。

## 4. 013 Bridge 的边界

013 bridge 只交付：

- `/world` `/protocol` `/portal` `/library` 占位页面
- `/me/library` URL 迁移
- nav + test 同步

013 bridge 不交付：

- 完整 IA 的视觉 / 文案 / 真实模块卡片
- 统一导航组件
- 设计系统扩展
- Accessibility / Responsive 完整测试

后续由 014（Library）+ 017/018/019/020/021（其他占位页）逐步填充。