# 给 Codex 的起始指令

执行 **MFD-008 — Alpha Release Gate**。

开始前确认：

> `MFD-008 = GO`

来自 MFD-007。

然后完整阅读：

1. `00_README.md`
2. `01_MFD-008_TASK.md`
3. `02_RELEASE_GATE_MATRIX.md`
4. `03_DEFECT_POLICY.md`
5. `04_REAL_WORLD_SCENARIOS.md`
6. `05_SECURITY_RELEASE_CHECKLIST.md`
7. `06_RELEASE_ARTIFACT_TEMPLATE.md`
8. `07_ROLLBACK_TEMPLATE.md`
9. `08_IMPLEMENTATION_SEQUENCE.md`
10. `09_FINAL_DECISION_TEMPLATE.md`
11. `10_PHASE_1_CLOSURE.md`

你的角色已经从“开发者”切换为：

> **Release Gatekeeper**

严格规则：

- 不增加新功能；
- 不重做 UI；
- 不改验收标准来适配失败；
- 先冻结 RC；
- 真实 Windows 安装；
- 真实 Cloud；
- 真实 PlaybackManifest；
- 真实歌曲；
- 真实 Windows 发声；
- 必须人工确认 audible；
- 必须测试 session / manifest expiry；
- 必须测试断网 / 重连；
- 必须测试 restart / forced kill；
- 必须测试 corrupted local state；
- 必须测试 rapid interaction；
- 必须测试 single instance / tray / media controls；
- 必须测试 upgrade / uninstall；
- 必须做 secret / Electron security audit；
- unsigned build 只能进入 internal Alpha；
- 不得未经人类授权公开发布。

如发现阻塞缺陷：

> 停止 Gate，记录 P0/P1，不要在本任务中偷偷扩开发范围。

最终必须输出：

> `MOODIFY DESKTOP 0.1 ALPHA: GO / CONDITIONAL GO / NO-GO`
