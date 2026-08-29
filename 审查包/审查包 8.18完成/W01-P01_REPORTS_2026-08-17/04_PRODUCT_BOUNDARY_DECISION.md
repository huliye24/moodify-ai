# 04 — Product Boundary Decision

**Decision:** CD-001 / CD-011（W01-P01, 2026-08-17）

## External Product

**Name:** Moodify Music / Moodify Player
**Primary user action:** PLAY
**Public promise（现状声明）:** 以 PLAY 为核心的音乐聆听体验；本地文件或云端准备曲目；云端准备是内部生产环节。

## Internal（不对外）

- Moodify Ear / Auditory Intelligence
- audio analysis / stem separation / judgment / controlled intervention / preset decision / verification / evidence / learning
- Cloud Production System（intake → job → storage → compute → render → delivery）
- Classic Reconstruction（内部生产哲学）

## 边界规则

1. 用户表面极简：`Source/Cloud-prepared Track → Moodify → PLAY`。
2. 复杂度由 Moodify 承担，不转嫁给用户。
3. 不暴露内部状态机为产品 UX；不强迫用户选择工程预设；不把 Ear 作为第二个公开产品。
4. 不得声称云端能力可用，除非运行时证据已验证（P00 现实边界）。

## 对外命名待决（HUMAN_DECISION_REQUIRED）

「Moodify Music」与「Moodify Player」的最终对外命名、品牌表现与域名策略（含 rongjingmusic.com）——本包不猜。

## 落地文件

- README.md（External Product / Internal Systems 节）
- docs/canon/PRODUCT_BOUNDARY.md
- docs/canon/CURRENT_CANON.md
