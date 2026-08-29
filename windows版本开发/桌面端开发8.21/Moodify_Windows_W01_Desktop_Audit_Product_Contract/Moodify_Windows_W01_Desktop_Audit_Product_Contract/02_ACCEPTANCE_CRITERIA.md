# W01 Acceptance Criteria — MFY-WIN-W01-DESKTOP-AUDIT-001

W01 不是“写完一份报告”就算完成。以下验收项需要以真实代码、运行结果、测试或明确 blocker 为依据。

## A. Authority 与边界

- [ ] 已读取根 `AGENTS.md`
- [ ] 已读取当前 Canon / Product Boundary / Authority Order
- [ ] 已确认 `CANON_CHANGE = NO`
- [ ] 已确认 Moodify Ear 仍为内部系统，不进入公开桌面 UI
- [ ] 已确认 `VISUAL_REDESIGN = FORBIDDEN`
- [ ] 未将历史文档覆盖到当前 Canon

## B. Windows 实现发现

- [ ] 已证明 Windows app 的真实代码位置
- [ ] 已证明实际桌面技术栈，不凭背景假设 Electron
- [ ] 已定位 bootstrap / entrypoint
- [ ] 已定位 renderer / UI root
- [ ] 已定位 player engine
- [ ] 已定位 persistence layer
- [ ] 已定位 IPC / native bridge（若不存在也需有证据）
- [ ] 已定位 build / packaging config
- [ ] 已定位测试入口

## C. 用户闭环审计

- [ ] 冷启动完成
- [ ] 单曲导入完成或 blocker 已记录
- [ ] 歌单创建完成或 blocker 已记录
- [ ] “添加歌曲到歌单”已真实操作并定位断点
- [ ] 歌曲从歌单移除能力已核验
- [ ] play / pause 已核验
- [ ] previous / next 已核验
- [ ] restart 恢复已核验
- [ ] missing / moved / renamed file 行为已核验

## D. 数据与状态

- [ ] Track source of truth 已明确
- [ ] Library source of truth 已明确
- [ ] Playlist source of truth 已明确
- [ ] PlaylistItem / Track relation 已明确
- [ ] Queue authority 已明确（不存在则标 MISSING）
- [ ] PlaybackSession authority 已明确
- [ ] UI state 与 domain state 是否混用已明确
- [ ] 持久化 schema 已记录
- [ ] schema version / migration 状态已记录
- [ ] duplicate import identity 已记录
- [ ] local track 与 cloud track 身份是否混用已记录

## E. 根因与风险

- [ ] `playlist-add-root-cause.md` 不只写“功能未完成”
- [ ] 根因定位到具体层：UI / event / state / schema / persistence / sync / ID / other
- [ ] 每个 P0/P1 缺口都有代码路径和 evidence
- [ ] 没有无法解释的 P0 `UNKNOWN`
- [ ] 关键 P1 UNKNOWN 若无法消除，已触发 W02 BLOCKED
- [ ] 已记录重复 authority / shadow state / stale data 风险

## F. 产品模型

- [ ] 已对 Track / Playlist / PlaylistItem 给出 KEEP / REPAIR / MIGRATE
- [ ] Queue 与 Playlist ordering 被明确分离或解释为何当前未分离
- [ ] missing file 不应自动破坏 playlist relation 的目标约束已评估
- [ ] 本地与云端 Track identity 边界已评估
- [ ] migration proposal 不会丢现有用户数据
- [ ] W01 未提前执行大规模 migration

## G. UI 冻结

- [ ] 当前 Windows Alpha 截图已作为视觉参考
- [ ] 未增加信息密集 dashboard
- [ ] 未重做主导航
- [ ] 未新增 Ear / DSP / Evidence 面板
- [ ] 后续功能扩展优先 contextual / secondary / modal / state-change

## H. Build / Verification

- [ ] install 命令已记录并验证或 BLOCKED
- [ ] dev 命令已记录并验证或 BLOCKED
- [ ] test 命令已记录并验证或 BLOCKED
- [ ] build 命令已记录并验证或 BLOCKED
- [ ] package 命令已记录并验证或 BLOCKED
- [ ] 测试结果保存
- [ ] changed files 保存
- [ ] evidence manifest 完整
- [ ] 没有 secrets / private audio / heavy generated artifacts

## I. Handoff

- [ ] `W01_AUDIT_REPORT.md` 完成
- [ ] `function-matrix.csv` 完成
- [ ] `state-authority-map.md` 完成
- [ ] `W02_HANDOFF.md` 完成
- [ ] W02 的第一施工点明确
- [ ] W02 Gate 明确给出 `PASS` 或 `BLOCKED`

---

## PASS Rule

只有在下面条件同时成立时：

```text
关键 authority 已查明
+ 歌单添加根因已查明
+ persistence 已查明
+ player 基础链路已查明
+ build/test 入口已查明
+ UI freeze 被接受
```

才允许：

```text
W01_STATUS = PASS
W02_GATE = PASS
```

否则：

```text
W01_STATUS = BLOCKED
W02_GATE = BLOCKED
```
