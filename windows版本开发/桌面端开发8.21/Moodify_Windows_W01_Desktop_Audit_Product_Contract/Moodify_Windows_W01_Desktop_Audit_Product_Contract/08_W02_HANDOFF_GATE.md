# W02 Handoff Gate

W02 的任务是 Music Library。本门槛的作用是防止 W02 在未知基础上重新造 Track / Library / persistence。

## W02 可开始的必要事实

- [ ] Windows app root 已定位
- [ ] 实际 desktop stack 已确认
- [ ] UI root / player root 已定位
- [ ] Track source of truth 已明确
- [ ] Track ID 规则已明确
- [ ] Local file identity / path 规则已明确
- [ ] Library source of truth 已明确
- [ ] Playlist source of truth 已明确
- [ ] PlaylistItem relation 已明确
- [ ] 当前 persistence technology 已明确
- [ ] persistence schema 已明确
- [ ] restart 数据恢复已验证
- [ ] duplicate import 当前行为已验证
- [ ] missing / moved / renamed file 当前行为已验证
- [ ] “Add Track to Playlist” 根因已定位
- [ ] player 最小 playback path 已画出
- [ ] tests 入口已明确
- [ ] build / dev 入口已明确
- [ ] 没有第二套未解释 state authority
- [ ] UI Freeze Contract 已确认
- [ ] `CANON_CHANGE = NO`

## Gate PASS

允许 W02 开始的最低条件：

```text
Track identity KNOWN
Library authority KNOWN
Playlist relation KNOWN
Persistence authority KNOWN
Playlist-add root cause KNOWN
Build/test entry KNOWN
```

## Gate BLOCKED

以下任一存在则 BLOCKED：

- Track ID / identity 仍 UNKNOWN
- Playlist 真实持久化结构仍 UNKNOWN
- 同一 domain 存在竞争 authority 且没有判断
- 无法启动桌面端且没有可替代运行证据
- 当前数据可能在 W02 修改后不可恢复
- 需要 Canon change 才能继续，但人类尚未批准

## Handoff Output

`artifacts/windows/w01/W02_HANDOFF.md`

必须写：

```text
W02_GATE = PASS | BLOCKED

SAFE_TO_REUSE:
- ...

MUST_REPAIR_FIRST:
- ...

DO_NOT_DUPLICATE:
- ...

DATA_MIGRATION_REQUIRED:
- YES | NO

RECOMMENDED_FIRST_COMMIT:
- ...

EVIDENCE:
- ...
```
