# W10 Handoff Gate — Moodify Cloud Bridge

W10 将第一次把 Windows 客户端接入 Moodify 真正差异化的云端链路。

## Required

- [ ] W09_STATUS = PASS
- [ ] Track / Library stable
- [ ] Playback stable
- [ ] Queue stable
- [ ] Recovery stable
- [ ] Windows native adapter does not own business state
- [ ] Open File/import path stable
- [ ] desktop network/API client location known
- [ ] cloud capability reality can be audited

## W10 Target

```text
Local Source
→ Moodify Cloud request
→ preparation
→ Cloud-prepared Track
→ PLAY
```

公开状态保持：

```text
正在准备…
准备完成
▶ Play
```

## Must Hide

```text
Ear
Stem
Judge
Intervene
Evidence
internal job graph/state machine
```

## Must Not Claim

任何未真实验证的 AI inference、自动完整云 pipeline、生产规模处理，都不能包装成 live capability。

```text
W10_GATE = PASS | BLOCKED
```
