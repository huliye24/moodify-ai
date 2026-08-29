# W02 Acceptance Criteria

## A. Preflight

- [ ] W01 `W02_GATE = PASS`
- [ ] W01 Track authority 已读取
- [ ] W01 Library authority 已读取
- [ ] W01 persistence authority 已读取
- [ ] W01 migration requirement 已读取
- [ ] 未凭空假设 Electron / SQLite / React 等技术栈

## B. Track

- [ ] 唯一 Track authority
- [ ] Track ID 稳定
- [ ] title/artist/filename 不作为唯一 identity
- [ ] local source 有明确 representation
- [ ] availability 有明确状态
- [ ] same filename different file 可共存
- [ ] duplicate import 有确定行为
- [ ] Player 不维护第二套 Track truth

## C. Import

- [ ] 单曲导入
- [ ] 多曲导入或明确说明当前不支持
- [ ] unsupported file 安全失败
- [ ] invalid media 安全失败
- [ ] 中文路径通过
- [ ] 空格路径通过
- [ ] metadata 缺失有 fallback
- [ ] import result 可区分 imported/already exists/failed

## D. Persistence

- [ ] Track 持久化
- [ ] restart 后 Library 仍存在
- [ ] failed import 不留下半数据
- [ ] schema/version 有记录
- [ ] migration 可重复或 NOT_REQUIRED
- [ ] 没有 shadow persistence
- [ ] 旧数据不被静默抹除

## E. Missing Source

- [ ] rename 行为已验证
- [ ] move 行为已验证
- [ ] delete 行为已验证
- [ ] permission failure 行为已验证或 BLOCKED
- [ ] source missing 不使应用崩溃
- [ ] Track identity / relations 得以保留
- [ ] play missing source 安全失败

## F. Remove

- [ ] 可以从 Library 移除
- [ ] 不删除原始文件
- [ ] restart 后保持移除
- [ ] 不产生 orphan / broken foreign key
- [ ] 对已有 playlist relation 的行为明确

## G. Player Integration

- [ ] Library Track 可播放
- [ ] metadata 显示来自同一 Track authority
- [ ] duration / source resolution 正常
- [ ] restart 后仍可播放
- [ ] missing source 不 crash
- [ ] 没有临时 file-object player bypass

## H. UI Freeze

- [ ] 复用当前 UI
- [ ] 未重做首页
- [ ] 未新增 DSP/Ear/Evidence UI
- [ ] 未构建封面墙
- [ ] 未把 Library 变成 dashboard
- [ ] 新交互仅为完成 Library 必需

## I. Tests

- [ ] Track identity tests
- [ ] duplicate tests
- [ ] persistence restart tests
- [ ] invalid import tests
- [ ] missing source tests
- [ ] remove tests
- [ ] player integration tests
- [ ] regression tests
- [ ] 所有测试结果有 evidence

## J. Handoff

- [ ] `W02_IMPLEMENTATION_REPORT.md`
- [ ] `track-identity.md`
- [ ] `library-authority.md`
- [ ] `import-pipeline.md`
- [ ] `test-report.md`
- [ ] `W03_HANDOFF.md`
- [ ] W03 可直接引用 Track/Library，不需要再造数据层

## PASS Rule

只有真实证明：

```text
Import
+ Stable Track
+ Persistent Library
+ Restart
+ Play
+ Missing-source safety
+ No duplicate authority
```

才允许：

```text
W02_STATUS = PASS
W03_GATE = PASS
```
