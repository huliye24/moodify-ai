# 给 Codex 的起始指令

执行 **MFD-009 — Alpha Field Validation & Evidence**。

前置条件：

> MFD-008 = GO 或经过人类批准的 CONDITIONAL GO。

完整阅读：

1. `00_README.md`
2. `01_MFD-009_TASK.md`
3. `02_ALPHA_COHORT_TEMPLATE.md`
4. `03_LISTENING_EVIDENCE_PROTOCOL.md`
5. `04_TELEMETRY_MINIMUM_SCHEMA.md`
6. `05_FEEDBACK_AND_DEFECT_TEMPLATE.md`
7. `06_ALPHA_BATCH_REPORT_TEMPLATE.md`
8. `07_ACCEPTANCE_GATE.md`
9. `08_MFD-010_INPUT_CONTRACT.md`

这不是功能开发包。

核心任务：

> **让真实 Alpha 使用产生可靠证据。**

必须建立：

- controlled tester cohort；
- device matrix；
- reliability evidence；
- playback evidence；
- minimal telemetry/support bundle；
- blinded/simple listening comparison；
- second-session signal；
- bug / feature request separation；
- privacy boundary；
- Alpha Batch Report；
- final Alpha Validation Report。

严禁：

- 收到功能需求就立刻开发；
- 为了反馈加 EQ / 歌词 / 社区 / 皮肤 / WASAPI；
- 过滤负面听感；
- 收集不必要个人数据；
- 把 signed URL/token 写入 telemetry；
- 用几个人的偏好宣称普遍音质提升。

如果出现 P0 安全/权限/崩溃问题：

> 暂停扩大 Alpha，先记录 blocker。

最后明确：

> `MFD-010: GO / CONDITIONAL GO / NO-GO`
