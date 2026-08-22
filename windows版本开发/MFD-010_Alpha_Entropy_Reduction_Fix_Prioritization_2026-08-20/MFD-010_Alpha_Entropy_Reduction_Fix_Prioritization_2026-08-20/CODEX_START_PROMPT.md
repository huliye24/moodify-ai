# 给 Codex 的起始指令

执行 **MFD-010 — Alpha Entropy Reduction & Fix Prioritization**。

前置条件：

> `MFD-010 = GO`

来自 MFD-009。

完整阅读：

1. `00_README.md`
2. `01_MFD-010_TASK.md`
3. `02_PRIORITY_FRAMEWORK.md`
4. `03_ENTROPY_REDUCTION_TABLE_TEMPLATE.md`
5. `04_ROOT_CAUSE_TEMPLATE.md`
6. `05_LISTENING_PATTERN_TEMPLATE.md`
7. `06_FEATURE_REQUEST_COMPRESSION.md`
8. `07_FIX_PACKAGE_TEMPLATE.md`
9. `08_PHASE_2_DECISION_TEMPLATE.md`
10. `09_ACCEPTANCE_GATE.md`
11. `10_FINAL_DECISION_REPORT_TEMPLATE.md`

这不是修复包，也不是 Phase 2 开发包。

你的角色是：

> **把 Alpha 的噪音压缩成少量高价值工程决策。**

必须：

- 归一化证据；
- 去重；
- 按根因合并；
- 给 Evidence Strength；
- 给 Core Flow Impact；
- 判断 Product Fit；
- 判断 Complexity / Entropy Cost；
- 每项只进入 FIX_NOW / FIX_NEXT / OBSERVE / EXPERIMENT / DEFER / REJECT / NEEDS_MORE_EVIDENCE；
- 独立分析听感 pattern；
- 独立分析 second-session；
- 把 Feature Requests 压缩成主题；
- 识别设备风险；
- 只设计 MFD-FIX 包，不在本包实现；
- 不默认开启 Phase 2。

核心原则：

> 高频需求不等于正确需求。  
> 用户期待传统播放器，不代表 Moodify 应该变成传统播放器。  
> 没有证据的功能，不进入主线。  
> 能删除，就不要增加。  
> 优先修 Play，而不是扩边界。

最后必须给出：

> `NEXT: FIX / MORE_ALPHA / PHASE_2_DEFINITION / HOLD`
