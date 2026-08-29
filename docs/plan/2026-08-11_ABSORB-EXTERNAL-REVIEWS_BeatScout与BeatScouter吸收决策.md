# 2026-08-11 — 外部项目评审吸收决策（BeatScout / BeatScouter）

**决策类型:** 9 月分析规划（不影响 8 月冻结边界）
**评审对象:**
- [BeatScout](https://github.com/advaitbd/BeatScout) — R 项目，TikTok 走红预测（Spotify 启发式特征 + 平台信号）
- [BeatScouter](https://github.com/gardenqu/BeatScouter) — Kotlin Android + Flask，Spotify 音频特征余弦相似度歌曲推荐

---

## 1. 吸收（融入 Moodify）

### A. 误判代价不对称框架 → 9 月阈值校准（吸收）
来源: BeatScout 显式以 FPR/FNR 财务代价不对称选择模型（宁可漏报不误报）。

Moodify 语境下的落点:
- Moodify 已有 **fail-closed** 判断哲学（证据不足时保守拒绝，补丁包23）。BeatScout 的框架提供的是**用数据量化这个不对称强度的流程**。
- 9 月分析新增问题（协议 5 章问题列表第 9 条）:
  > **干预强度阈值校准**：基于盲评数据的 delta 分布，显式定义"过度干预（把可接受听感改坏）"vs"干预不足（保留问题声音）"的代价不对称，校准 judgment rules 阈值，使错误方向偏向保守侧。
- 方法: 代价加权评估（如以代价矩阵代替纯准确率）、阈值-代价曲线、与盲评 pairwise 数据对照。
- 落点文件: 9 月分析 notebook/报告（`docs/` 下 9 月产出）。

### B. 特征降维实证流程 → 9 月指标冗余分析（吸收）
来源: BeatScout 用 RF varImp + OOB 误差曲线选最优特征数（11/13）。

落点: 协议 5 章问题 4"哪些指标冗余"的具体方法——对 28 指标权威矩阵做:
- 重要性排序（对盲评偏好的预测贡献）
- 相关性分析（如 spectral centroid vs rolloff 的冗余确认）
- 冗余指标降级为追踪（不进核心训练），数量目标 ≥ 8 个指标仍覆盖 Reference 分级。

### C. 相似推荐卡片 UI → 未来 feed 参考（延后吸收）
来源: BeatScouter 的搜索→相似度卡片列表交互（封面 + 分数 + 跳转）。

落点: Moodify feed/推荐 UI 的交互形态参考。**8 月冻结协议禁止新 UI 表面**，记为延后（9 月后产品阶段），且内核用 Moodify 测量指标 + 盲评数据，不用 Spotify 特征。

---

## 2. 明确不吸收（边界确认）

| 不吸收 | 理由 |
|---|---|
| Spotify 启发式音频特征（danceability/valence 等） | 无定义、无容差、无版本 —— 协议 Tier C 边界 |
| TikTok/平台传播信号预测走红 | 弱问题（BeatScout 自证 FNR 51.5%），不是音频测量；与"Moodify = AI 的耳朵"定位冲突 |
| 无证据余弦相似度推荐 | 无评审、无人类权威 —— Moodify 用 A/B Judge / NTrack Elo / 盲评结构替代 |
| BeatScouter 后端缺失的架构 | 仓库必须可复现（"仓库即实验室"原则） |

---

## 3. 落地清单

- [x] 追踪表 September_Protocol 新增行：代价不对称阈值校准（ALLOWED）
- [x] 本决策备忘（docs/plan/）
- [ ] 9 月分析问题 9（干预阈值校准）纳入 9 月分析 notebook 规划
- [ ] 9 月指标冗余分析（问题 4）方法细化：varImp + OOB 流程
- [ ] Gate 5 科学发布素材："Moodify 测量 vs 启发式特征"对比论证（文档）
