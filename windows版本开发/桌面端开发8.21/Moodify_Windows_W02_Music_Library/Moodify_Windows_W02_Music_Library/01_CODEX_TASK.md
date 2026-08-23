# Codex 执行任务书 — MFY-WIN-W02-MUSIC-LIBRARY-001

## 0. 执行模式

```text
PACKAGE = W02
FOCUS = MUSIC_LIBRARY
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
START_W03 = NO
```

本包必须在真实 W01 结果上施工。

---

## 1. Phase 0 — Gate Check

先读取 W01 产物。

至少确认：

- Windows app root
- actual desktop stack
- Track authority
- Library authority
- persistence authority
- Track identity
- player entry
- test entry
- W02 Gate

输出：

`artifacts/windows/w02/preflight.md`

内容至少：

```text
W01_STATUS =
W02_GATE =
TRACK_AUTHORITY =
LIBRARY_AUTHORITY =
PERSISTENCE_AUTHORITY =
PLAYER_AUTHORITY =
MIGRATION_REQUIRED =
```

若 `W02_GATE != PASS`，停止。

---

## 2. Phase 1 — Preserve / Repair Existing Authority

先判断 W01 对 Track / Library 的结论：

```text
KEEP
REPAIR
MIGRATE
```

### KEEP
直接复用，不另建 store。

### REPAIR
只修现有 authority 的缺口。

### MIGRATE
按 W01 migration plan 执行最小可逆迁移。

任何情况下都禁止：

- 再建第二个 Track repository
- 再建第二个 Library store
- UI local state 成为业务 truth
- 同时维护两套 persistence schema 而无 compatibility plan

---

## 3. Phase 2 — Track Contract

以仓库现有语言 / 类型系统实现或加固 Track contract。

至少需要表达：

```text
id
source_kind
source_ref
title
artist
album
duration_ms
format
availability
created_at
updated_at
```

字段名可适配仓库，但语义必须清楚。

### Required invariants

1. `Track.id` 稳定。
2. display metadata 不能决定 identity。
3. 本地 path normalization 必须一致。
4. Library 内不能因为重复导入同一 source 而无限生成重复 Track。
5. 同名不同文件必须允许共存。
6. source 失效时 Track 进入明确不可用状态，不 crash。
7. Track 不复制成 Player 私有数据模型。
8. 未来 CloudTrack 接入时不能迫使重做所有本地 Track ID。

---

## 4. Phase 3 — Local Import Pipeline

实现 / 修复：

```text
Select File(s)
→ Validate
→ Normalize Source
→ Deduplicate
→ Extract Metadata
→ Build/Resolve Track
→ Persist
→ Publish Library Update
```

### 4.1 File validation

至少覆盖：

- supported audio
- unsupported extension
- unreadable file
- zero-byte / invalid media
- path with Chinese
- path with spaces
- duplicate selection

不要仅依赖扩展名；若现有音频引擎能做 decode probe，应复用。

### 4.2 Metadata

优先使用：

```text
embedded metadata
→ safe fallback to filename
```

至少安全处理：

- title missing
- artist missing
- album missing
- duration unavailable
- malformed tags

不要因为 tag 失败导致整个导入失败，除非音频本身不可用。

### 4.3 Import result

对每个文件产生明确结果：

```text
IMPORTED
ALREADY_EXISTS
UNSUPPORTED
INVALID
FAILED
```

如果 UI 当前没有结果反馈，本包可增加最小反馈，但禁止重设计。

---

## 5. Phase 4 — Track Identity & Dedupe

必须实现一套**确定性规则**，但具体算法服从 W01 现实。

至少测试：

```text
same exact file imported twice
same path imported twice
same filename in two folders
same metadata but different content
same content copied to another path
case differences where Windows resolves same path
slash normalization
Unicode path
```

如果当前架构不能做 content hash，不强制在 W02 引入重型 hashing pipeline。

可以采用分层 identity，例如：

```text
stable internal UUID
+
normalized source locator uniqueness
+
optional fingerprint/hash
```

但要把选择和 trade-off 写入 `track-identity.md`。

---

## 6. Phase 5 — Persistence

Library 必须经 restart 验证。

如果现有系统使用：

- SQLite
- JSON
- localStorage / IndexedDB
- filesystem DB
- other

继续服从唯一 authority。

### Required

- atomic or transaction-safe write where applicable
- schema/version 明确
- migration 可重复
- restart 不丢 Track
- failed import 不产生半条记录
- duplicate import 不产生 orphan
- remove 不破坏其他无关 Track
- app upgrade 路径不被本包破坏

---

## 7. Phase 6 — Availability & Missing Source

实现 / 修复 source resolution。

至少区分：

```text
AVAILABLE
UNAVAILABLE
UNKNOWN
```

测试：

1. 正常文件
2. 导入后 rename
3. 导入后 move
4. 导入后 delete
5. 权限不可读

目标行为：

```text
Library still loads
Track relation preserved
Play fails safely
User gets minimal understandable state
No crash
```

W02 不要求完整 relink UX，但应留下未来 repair API / seam。

---

## 8. Phase 7 — Remove from Library

必须严格区分：

```text
Remove from Library
≠
Delete original file
```

W02 默认只允许：

```text
remove reference / library membership
```

不得删除用户原始音乐文件。

如果当前代码已有 delete-file 行为，视为高风险，必须审计并加保护。

同时检查：

- Playlist relation（若当前已存在）
- current playback
- queue（若已有）
- unavailable Track

本包不完整实现 Playlist，但不能静默留下 referential corruption。

---

## 9. Phase 8 — Player Integration

目标：

```text
Library Track
→ source resolver
→ existing player
```

禁止 Player 私下重新解析另一套 raw file object。

验证：

- play imported Track
- pause
- next/prev 若当前已有
- source missing
- metadata display
- duration
- restart 后再次播放

如果 Player 当前高度耦合文件选择器结果，应在 W02 做最小解耦。

---

## 10. Phase 9 — Minimal Library Surface

UI 只做功能验证所需的最小扩展。

优先复用：

- 当前 “添加歌曲”
- 当前 Sidebar / Secondary View
- 现有列表容器
- modal / context menu

允许最小 Library view 展示：

```text
title
artist
availability
play action
context action
```

禁止：

- 大规模表格化
- 封面墙重做
- 新 dashboard
- 推荐流
- AI 控制台

如果已有“全部歌曲”页面，优先修复现有页面，不另建重复页面。

---

## 11. Phase 10 — Tests

必须新增 / 修复自动化测试。

至少覆盖：

### Domain
- stable Track creation
- duplicate handling
- same name different source
- metadata fallback
- availability transitions

### Persistence
- import → restart → exists
- remove → restart → absent
- failed import no half-record
- migration idempotent（如有）

### Integration
- import → player resolves source
- missing source → safe failure
- current UI/store sees Library update

### Regression
- existing play still works
- existing playlist data not destroyed
- no second authority introduced

---

## 12. Required Outputs

写入：

`artifacts/windows/w02/`

至少：

1. `W02_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `track-identity.md`
4. `library-authority.md`
5. `import-pipeline.md`
6. `persistence-change.md`
7. `migration-report.md`（无迁移则明确 `NOT_REQUIRED`）
8. `missing-source-behavior.md`
9. `test-report.md`
10. `evidence-manifest.json`
11. `W03_HANDOFF.md`

---

## 13. Commit Discipline

建议最小提交序列：

```text
1. test: lock current library behavior
2. refactor/fix: establish Track/Library authority
3. feat: local import pipeline
4. feat: persistence + availability
5. feat: remove from library
6. integration: player resolves Library Track
7. test/docs: regression + evidence
```

实际提交数量可变，但不要做一个巨型不可审查 commit。

---

## 14. Definition of Done

完成时必须能真实证明：

```text
File
→ Import
→ Track
→ Library
→ Persistence
→ Restart
→ Resolve
→ Play
```

以及：

```text
Duplicate Import → no dirty duplicate
Missing Source → no crash / relation preserved
Remove from Library → original file untouched
```

最后：

```text
W02_STATUS = PASS | BLOCKED
W03_GATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```
