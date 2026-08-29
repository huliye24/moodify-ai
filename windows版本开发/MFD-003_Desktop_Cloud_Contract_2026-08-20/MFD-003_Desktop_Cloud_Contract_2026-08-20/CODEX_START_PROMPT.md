# 给 Codex 的起始指令

执行 **MFD-003 — Desktop–Cloud Contract**。

先读取 MFD-002 最终输出并确认：

> `MFD-003 = GO`

然后完整阅读：

1. `00_README.md`
2. `01_MFD-003_TASK.md`
3. `02_PLAYER_API_CONTRACT_DRAFT.md`
4. `03_SECURITY_AND_AUTH_BOUNDARY.md`
5. `04_CONTRACT_TEST_MATRIX.md`
6. `05_IMPLEMENTATION_SEQUENCE.md`
7. `06_ACCEPTANCE_GATE.md`

先做真实后端只读核验，再修改。

本包核心不是播放，而是：

> Desktop 和 Moodify Cloud 之间只存在一条正式、用户级、安全、可版本化的 Player API 依赖面。

关键禁止：

- Desktop 不能拿 service-key
- 不能直连数据库
- 不能拿 OSS secret
- 不能调用 Ear internal API
- 不能把 internal processing 细节暴露给客户端
- 不要在本包实现完整音频播放
- 不要提前做正式播放器 UI

最终必须用真实用户级会话、真实 track、真实 PlaybackManifest 做 smoke，并验证媒体资源可达性。

最后明确：

> `MFD-004: GO / CONDITIONAL GO / NO-GO`
