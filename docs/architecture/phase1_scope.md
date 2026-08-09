# Moodify Phase I 范围（MFY-PHASE1-FREEZE-001）

**日期**: 2026-08-08
**执行**: 仓库审计 + 冻结 + 核心整合（见 `artifacts/phase1_freeze/` 五件套）

## 产品身份

Moodify Phase I 是 **AI 生成音乐的听觉智能系统**。不是 DAW、不是市场、不是社交网络。

> 上传一段声音。Moodify 倾听、表示、判断、解释、给出置信度与证据，并沉淀为可复用的案例。

规范能力循环：`LISTEN → REPRESENT → JUDGE → EVIDENCE → LEARN`

## 规范用户路径

1. 上传音频
2. 创建/注册分析案例（stable case ID）
3. 运行听觉分析（scan / compare）
4. 产生归一化听觉表示（metrics + representation）
5. 产生判断（severity + confidence + evidence_refs）
6. 渲染听觉报告（human + machine JSON）
7. 保存到 Library / 案例历史
8. 可选二次动作：Experiment / Improve（保持次要）

## 主导航面（Android 已落地 4-tab）

- Home（首页/发现）
- Analyze（听觉检测/处理中心）
- Library（案例/作品）
- Profile（我的）
- Auditory Report 是主要内容面（非 tab）

## Phase II 冻结清单与机制

| 冻结项 | 机制 |
|--------|------|
| CWC token 经济 | 代码已删（git 历史可恢复）；`docs/DEEPSEEK_TASK_CWC_CREATOR_PASS.md` 已标记 PHASE2_FROZEN |
| 市场/交易中心 | `CollaborationHubScreen.kt`（含 Marketplace）@Deprecated 不可达 |
| 版权交易 | `CopyrightCenterScreen.kt` @Deprecated 不可达 |
| 创作者中心 | `CreatorCenterScreen.kt` @Deprecated 不可达 |
| 发布流程 | `PublishWorkScreen.kt` @Deprecated；WorkDetail 入口已移除 |
| 社交通知 | `NotificationCenterScreen.kt` @Deprecated；Home 铃铛入口已移除 |
| 社交图谱/feed/邀请增长 | 无实现（grep 0 命中） |
| AI 漫画/3D/生态扩展 | 无实现 |

冻结策略配置：`moodify-core-package/configs/phase1_scope.yaml`（feature_flag_off 默认）

## 核心承诺（不得破坏）

1. **规范控制脊柱**：`app/production_control.py` 16 状态全链（source registration → spec binding → analysis → planning → technical validation → artistic approval → execution → verification → packaging → completion），ApprovedExecutionEnvelope 不可变授权
2. **CLI v2**：`python -m moodify case ...` JSON-first 稳定契约
3. **证据优先**：HIGH/CRITICAL 判断必须解析到证据；evidence_manifest.json 全链 hash 校验
4. **学习安全**：单案例反馈不自动修改全局阈值；提交前须 review（RightsMetadata）
5. **失败语义**：分析失败不产生 COMPLETED 案例；部分结果明确标注

## Phase I 退出门（12_PHASE1_EXIT_GATE）

Gate 1-8 状态见 `artifacts/phase1_freeze/validation_report.md`；全部满足前不扩展 Phase II 基础设施。
