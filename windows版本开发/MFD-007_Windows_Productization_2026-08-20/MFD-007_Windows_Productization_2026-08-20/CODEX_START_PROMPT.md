# 给 Codex 的起始指令

执行 **MFD-007 — Windows Productization**。

先确认 MFD-006 最终结论：

> `MFD-007 = GO`

然后完整阅读：

1. `00_README.md`
2. `01_MFD-007_TASK.md`
3. `02_WINDOWS_PRODUCT_CONTRACT.md`
4. `03_RELEASE_AND_UPDATE_POLICY.md`
5. `04_SIGNING_READINESS.md`
6. `05_WINDOWS_TEST_MATRIX.md`
7. `06_RELEASE_ARTIFACT_CONTRACT.md`
8. `07_IMPLEMENTATION_SEQUENCE.md`
9. `08_ACCEPTANCE_GATE.md`
10. `09_EVIDENCE_TEMPLATE.md`

本包的核心不是继续增加播放器功能，而是：

> **把 Moodify Desktop 从开发环境中的 Electron App，变成具有 Windows 安装、系统集成、版本、更新边界和可重复发行工程的软件。**

重点完成：

- stable application identity；
- Windows installer；
- Squirrel lifecycle（如果使用 Squirrel.Windows）；
- single instance；
- tray；
- background playback；
- Windows media controls；
- packaged logging；
- update service boundary；
- internal/public/stable channel；
- signing readiness；
- reproducible build；
- checksums；
- clean install / upgrade / uninstall。

重要限制：

- 如果没有签名能力，不要阻塞 internal Alpha；
- 但 unsigned build 必须明确标记 internal-only；
- 未签名不得判定 public release ready；
- 自动更新的真实生产启用依赖签名、update host、metadata 和 release gate；
- update failure 绝不能阻塞 Play；
- 不要为了 Windows media keys 引入 native C++；
- 不做 WASAPI / DSP / offline library；
- 不得未经人类授权公开发布 Release 或上传生产更新源。

最后明确：

> `MFD-008: GO / CONDITIONAL GO / NO-GO`
