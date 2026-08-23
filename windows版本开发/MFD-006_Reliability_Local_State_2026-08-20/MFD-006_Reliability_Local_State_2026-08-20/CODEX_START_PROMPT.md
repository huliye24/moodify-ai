# 给 Codex 的起始指令

执行 **MFD-006 — Reliability & Local State**。

先确认 MFD-005 最终结论：

> `MFD-006 = GO`

然后完整阅读：

1. `00_README.md`
2. `01_MFD-006_TASK.md`
3. `02_LOCAL_STATE_CONTRACT.md`
4. `03_RECOVERY_STATE_MACHINE.md`
5. `04_RELIABILITY_TEST_MATRIX.md`
6. `05_IMPLEMENTATION_SEQUENCE.md`
7. `06_ACCEPTANCE_GATE.md`
8. `07_EVIDENCE_TEMPLATE.md`

本包不要增加新产品功能。

核心目标是：

> **让 Moodify Desktop 在重启、断网、session 过期、PlaybackManifest 过期、异常退出和快速连续操作下仍然保持可恢复、可理解、不泄露 secret、不复制 Cloud authority。**

关键规则：

- 只建立一套 LocalStateStore；
- signed URL 绝不落盘；
- token 不得明文；
- session refresh / manifest refresh 要 single-flight；
- retry 必须 bounded；
- rapid next/previous 必须能取消旧 intent；
- 重启必须重新从 Cloud 校验 track 并取得新 manifest；
- 不做完整 offline mode；
- 不做后台音频下载；
- 不做 tray / media keys / auto update / installer；
- 不碰 DSP / WASAPI / native audio。

完成后必须做：

- 正常重启
- 强制 kill
- 本地状态损坏
- session expiry
- manifest expiry
- 断网/恢复
- 50 次连续切歌

最后明确：

> `MFD-007: GO / CONDITIONAL GO / NO-GO`
