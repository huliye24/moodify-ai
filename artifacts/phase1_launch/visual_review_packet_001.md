# Visual Product Finalization — Codex 审查证据包

**Document ID:** MFY-VISUAL-REVIEW-PACKET-001
**Version:** 1.0
**Date:** 2026-08-14
**Package:** MFY_CODEX_VISUAL_PRODUCT_FINALIZATION_001 (64)
**角色边界:** DeepSeek 提供稳定环境、页面、状态与截图（无视觉模态，不作最终判断）；Codex 执行最终审美/层级/完成度终审。

## 1. 审查入口（真机/本地可访问）

| 面 | URL | 状态 |
|---|---|---|
| 官网 | https://rongjingmusic.com/（本地: http://localhost:5198/） | 静态站待发布；本地截图可用 |
| Ear 工作台 | apps/ear-workbench/（dev_proxy 本地） | 本地可用；真机待部署 |
| Music Web | https://rongjinwenchuan.xyz/（线上） | **线上已部署**（可真机审查） |
| 设计陈列 | apps/music-web /design（本地 dev） | 本地可用 |

## 2. 截图矩阵（已生产，DeepSeek 提供）

| 截图 | 位置 | 状态 |
|---|---|---|
| 官网 index/ear/evidence × 1440/390 | artifacts/phase1_launch/official_site_001/ | 6 张，像素已验（石墨底 + evidence 绿） |
| Ear 工作台 home/case/result × 1440 + case 390 | artifacts/phase1_launch/ear_workbench_001/ | 6 张，真实数据（SUCCEEDED case） |
| Music 首页 × 1440/390 | artifacts/phase1_launch/music_listening_001/ | 2 张 |
| 设计系统陈列 × 1440/390 | artifacts/phase1_launch/design_system_001/ | 2 张 |

## 3. 审查清单（Codex 执行项）

1. 三端同一品牌可识别、产品用途可分辨（45 P0）；
2. 信息层级：官网叙事 → Ear 仪器 → Music 作品；
3. 语义色纪律：amber=人工、red=阻塞、evidence green=进行/验证；
4. 无装饰渐变冒充证据、无伪入口、无 autoplay；
5. 移动宽度无遮挡、键盘焦点可见；
6. 动效克制 + reduced-motion；
7. 完成度：空态/错误/恢复/离线面真实可用；
8. 输出：每面 ACCEPT / REVISE（含具体问题与归包）。

## 4. 交付接口

- Codex 结论写入本文件 §5（或 artifacts/phase1_launch/visual_review_001/）；
- REVISE 项按 62 变更政策分类（视觉打磨默认下季度，除非阻断性）；
- 终审通过 → 65 包 canary 视觉复查入口。

## 5. Codex 终审结论（待填）

```text
官网：ACCEPT / REVISE — …
Ear 工作台：ACCEPT / REVISE — …
Music Web：ACCEPT / REVISE — …
设计系统：ACCEPT / REVISE — …
发现项（归包）：…
签署：Codex / 日期
```

## 6. 事实边界

- 本证据包基于冻结 HEAD 与 47c4db2 修复后的完整页面（干净环境已验证）；
- Music Web 线上截图可由 Codex 真机复核（线上已部署）；
- 官网/工作台真机审查需部署后（65 流程），本地截图已覆盖静态渲染。
