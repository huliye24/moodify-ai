# MOOD PORTAL 013 — Navigation Model (Bridge Build)

**Version:** 1.0（MOOD PORTAL 013 bridge, 2026-08-30）
**Authority:** root `AGENTS.md` → `docs/mood/CURRENT_CANON.md` → 本文件
**Related:** [013_FINAL_REPORT.md](013_FINAL_REPORT.md) · [013_INFORMATION_ARCHITECTURE.md](013_INFORMATION_ARCHITECTURE.md)

---

## 1. 桌面主导航（声明）

```text
MOOD       →  /
World      →  /world
Protocol   →  /protocol
Network    →  /network
Library    →  /library
Build      →  /portal
Enter      →  /portal
```

**Moodify** 作为 Genesis Application，不在 MOOD 主导航层级。

## 2. 当前 013 Bridge 实现

- Moodify Player 主页（`app/page.tsx`）维持既有 sidebar + drawer：
  - sidebar：发现音乐 / 搜索 / 我的音乐（`/me/library`）
  - drawer：我的音乐 / Moodify 官网 / 荣景文川 / 使用条款 / 隐私说明 / 联系我们
- 013 不引入新顶层导航（避免与现有 sidebar 冲突）。完整统一导航属于 013 完整 TASK 的后续阶段（不在本次 bridge 范围）。

## 3. 移动端

- 主页维持既有 mobile header（`mobile-brand` + history + menu-toggle）
- 013 bridge 不引入新的 mobile nav

## 4. 设计原则

- 桌面：保留 MOOD 视觉语言（白色 / 浅色 / 大留白 / 波形 logo / 柔和紫蓝渐变）
- 移动：保留既有 hamburger menu
- 满屏 neon / DeFi dashboard / Meme coin 风格禁止
- 满屏 K 线 / 价格 ticker 禁止

## 5. 与既有 Public Form 的关系

- `docs/canon/CURRENT_CANON.md`（v1.1 Public Form）：处理 Moodify Music / Player 对外面，本文件不覆盖。
- `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`：公共品牌语言最高主题权威；本文件不覆盖。
- `docs/mood/CURRENT_CANON.md`：MOOD 总体身份与 Token Gate；本导航模型服从。