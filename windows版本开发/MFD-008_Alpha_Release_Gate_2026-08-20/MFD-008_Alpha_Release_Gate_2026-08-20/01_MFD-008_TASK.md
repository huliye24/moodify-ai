# MFD-008 — Alpha Release Gate
## Codex 正式执行任务书

**任务编号：** MFD-008  
**执行对象：** Codex  
**执行模式：** Final QA / Release Candidate Audit / No Feature Expansion  
**前置条件：** MFD-007 = GO

---

# 0. 总命令

你现在不是开发者角色。

你是：

> **Release Gatekeeper。**

不要继续扩功能。

只做：

- 核验；
- 复现；
- 分类；
- 阻塞；
- 生成发行证据。

---

# 1. Preflight

开始前记录：

```text
Desktop repo
branch
commit
version
Windows build number
Node
Electron
Forge
package manager
backend API version
release channel
signed/unsigned
installer SHA256
```

确认：

- working tree clean；
- release candidate commit 固定；
- installer 与 commit 对应；
- 没有测试过程中自动重新 build 混入新代码。

---

# 2. Release Candidate Freeze

建立：

```text
RC_VERSION
RC_COMMIT
RC_INSTALLER
RC_SHA256
```

从 Gate 开始到结束：

> 不允许 silently 修改 RC。

如果必须修复：

```text
FAIL
→ exit Gate
→ fix
→ new commit
→ new RC
→ restart affected Gate sections
```

---

# 3. Build Verification

从 clean checkout / clean environment 验证：

```text
install dependencies
→ typecheck
→ lint
→ tests
→ package/make
```

要求：

- lockfile 生效；
- 无 hidden local dependency；
- 无 dev machine absolute path；
- 无生产 secret；
- build reproducible enough to regenerate release artifact。

记录完整命令与结果。

---

# 4. Artifact Verification

核对：

```text
installer
version
file size
SHA256
signed status
publisher
channel
build info
release notes
```

如 unsigned：

必须明确：

```text
UNSIGNED_INTERNAL_ALPHA
```

并限制发行范围。

---

# 5. Fresh Install Test

在尽可能干净的 Windows 环境：

```text
install
→ launch
```

验证：

- installer 正常；
- app name 正确；
- icon 正确；
- Start Menu 正确；
- no Electron default branding；
- 首次启动不白屏；
- 没有开发服务器依赖；
- 没有需要 Node/npm 才能运行。

---

# 6. First Launch Test

首次启动验证：

- local state 空；
- session 流程可理解；
- network unavailable 时不崩；
- backend available 时可以进入 Player；
- no debug harness；
- no internal metadata；
- no traceback；
- no secret exposure。

---

# 7. Authentication Gate

验证：

```text
valid session
expired session
invalid session
revoked session if supported
refresh success
refresh failure
```

要求：

- 不无限 401；
- refresh single-flight；
- failure 可恢复；
- token 不出现在 UI / log；
- plaintext token 不落盘。

如果 Alpha 使用临时 auth：

必须明确标记：

```text
ALPHA_TEMPORARY_AUTH
```

并评估是否允许外部测试。

---

# 8. Library / Track Gate

验证：

- 用户只看见有权限的 track；
- empty library；
- missing track；
- unavailable track；
- malformed track id；
- backend error。

Desktop 不能：

- 显示 DB id 内部信息；
- 泄露无权限曲目；
- 直连数据库。

---

# 9. Playback Core Gate

至少使用 3 首真实 READY track（如果当前真实数据少于 3 首，使用所有可用并明确说明）。

对每首验证：

```text
load
play
audible
pause
resume
seek 25%
seek 50%
seek near end
volume
ended
next/previous
```

必须有真实人工听觉确认。

---

# 10. Playback Audio Sanity

只做播放正确性，不做音质营销。

记录：

```text
Audible
Unexpected speed change
Channel loss
Obvious truncation
Obvious clipping/distortion introduced by playback
Unexpected silence
```

如果任何一项异常：

> 阻塞 Alpha，除非已证明是源文件本身问题。

---

# 11. Manifest / Media Gate

验证：

- valid manifest；
- expired manifest；
- refreshed manifest；
- signed URL；
- asset missing；
- unauthorized asset；
- range/seek；
- media mime；
- no signed URL persistence。

检查：

```text
signed URL 不写入 local state
signed URL 不完整写日志
```

---

# 12. Network Fault Gate

人工测试：

### Start offline

```text
launch app while offline
```

### Playback offline

```text
play → disconnect
```

### Recover

```text
restore network
→ retry
→ play
```

要求：

- no crash；
- no infinite spinner；
- no infinite retry；
- no request storm；
- user can recover。

---

# 13. Restart Gate

验证：

### Normal close/reopen

- last track；
- position；
- volume；
- window state。

### Forced kill/reopen

- local state readable；
- no corruption；
- session safe；
- fresh manifest；
- no duplicate playback。

---

# 14. Local State Corruption Gate

人为制造：

```text
invalid JSON
bad schemaVersion
bad volume
negative position
off-screen window
```

必须：

- app opens；
- safe fallback；
- no crash；
- no secret leak。

---

# 15. Rapid Interaction Gate

至少执行：

```text
50 track switches
20 rapid play/pause
rapid next/previous mix
seek during switching
```

确认：

- no overlapping audio；
- no request explosion；
- no obvious listener leak；
- no app freeze；
- last intent wins。

---

# 16. Single Instance Gate

```text
launch app
launch app again
```

要求：

- existing instance focused / restored；
- no second playback engine；
- no duplicate tray；
- no duplicate background process。

---

# 17. Tray / Background Gate

验证：

- minimize；
- close policy；
- tray restore；
- tray quit；
- background playback；
- process exits when user truly quits。

不能留下：

> 音乐停止但后台 zombie 进程一直存在。

---

# 18. Windows Media Controls Gate

验证：

- play；
- pause；
- next；
- previous；
- title；
- artist；
- playback state sync。

如果当前系统 API / Electron version 不支持某项：

必须提供真实 blocker。

不得在 Gate 中临时引入 native addon。

---

# 19. Upgrade Gate

至少验证：

```text
alpha.N
→
alpha.N+1
```

如果没有真实上一版：

构建一个前版本测试 RC。

检查：

- installer upgrade；
- local state；
- schema migration；
- session；
- last track；
- playback；
- shortcut；
- tray；
- version display。

升级后必须能够正常 Play。

---

# 20. Uninstall Gate

验证：

- uninstall；
- app binary removed；
- shortcut removed；
- tray/process gone；
- session secret 按策略清除；
- 不影响 Cloud 用户数据；
- 不删除用户不应被删除的外部文件。

---

# 21. Logging Gate

检查 packaged logs。

确认存在必要：

```text
app version
OS
startup
recovery events
playback error code
update status
```

确认不存在：

```text
token
refresh token
Authorization
service key
DB credential
OSS secret
full signed URL
private key
```

---

# 22. Security Gate

至少检查：

- `contextIsolation = true`
- `nodeIntegration = false`
- sandbox status
- no disabled webSecurity
- no arbitrary navigation
- no raw ipcRenderer exposure
- no remote code loading
- no service key
- no DB access
- no OSS secret
- no signing secret
- update origin controlled
- renderer cannot obtain server secret

任何核心安全失败：

> ALPHA_NO_GO

---

# 23. Installer Security Gate

如果 signed：

检查：

- signature；
- publisher；
- timestamp；
- installer integrity。

如果 unsigned：

标记：

```text
INTERNAL_ALPHA_ONLY
```

不得给出：

```text
PUBLIC_ALPHA_READY
```

---

# 24. Update Gate

如果 auto-update enabled：

必须验证：

```text
check
available
download
ready
install
restart
new version
```

如果未启用：

必须验证：

- disabled state 非 fatal；
- UpdateService 不影响 Play；
- channel / feed / policy 已准备；
- public release blocker 明确。

---

# 25. Compatibility Gate

至少实测当前承诺的平台。

建议：

```text
Windows 11 x64
Windows 10 x64（若仍承诺）
```

对每个平台：

- install；
- launch；
- playback；
- tray；
- media controls；
- uninstall。

如果无法实测某平台：

> 不得写 VERIFIED SUPPORT。

只能写：

```text
UNVERIFIED
```

---

# 26. Resource Sanity

记录 packaged app 在基本使用中的：

- idle memory；
- playing memory；
- CPU idle；
- CPU playing；
- 50-switch 后 memory；
- disk log growth。

不设过度严格性能指标。

但若出现：

- 持续内存暴涨；
- CPU 持续异常；
- 日志无限增长；

则阻塞 Alpha。

---

# 27. Privacy / Data Boundary Gate

确认 Desktop 不持有：

- internal Ear evidence；
- raw processing graph；
- stems；
- private server filesystem path；
- database credentials；
- unnecessary user data dump。

本地持久化符合 MFD-006。

---

# 28. Branding Gate

检查用户可见界面：

- Moodify 名称统一；
- 没有 Electron 默认名称；
- 没有开发 placeholder；
- 没有 debug text；
- 没有 old “Ear public product” 混乱叙事；
- 没有内部技术术语污染首屏。

---

# 29. Scope Gate

确认 Alpha 没有悄悄膨胀：

```text
No:
EQ
DSP panel
WASAPI
ASIO
lyrics
visualizer
community
skin marketplace
recommendation
local music scan
offline library
upload product
```

如果存在无关功能：

评估是否移除 / 隐藏 / 明确 experimental。

---

# 30. Defect Classification

所有发现的问题必须分类：

## P0 — Release Blocker

例如：

- 无法播放；
- 安装失败；
- auth 泄漏；
- service key 泄漏；
- 数据越权；
- crash loop；
- 重复音频；
- update 安全问题；
- installer 严重问题。

## P1 — Alpha Blocker

例如：

- seek 大量失败；
- restart 丢关键状态；
- tray 无法退出；
- upgrade 破坏状态。

## P2 — Known Alpha Issue

不阻塞核心验证，但明显影响体验。

## P3 — Polish

视觉/细节问题。

---

# 31. Release Decision

只有以下情况允许：

## ALPHA_GO

- 0 个 P0；
- 0 个 P1；
- P2 有清单；
- 核心 Gates 全通过。

## CONDITIONAL_ALPHA_GO

- 0 个 P0；
- 某些 P1 被人类明确批准作为受控内部测试限制；
- 发行范围必须限定。

## ALPHA_NO_GO

- 任何未批准 P0；
- 核心播放失败；
- 安全失败；
- auth/权限失败；
- installer 不可用；
- upgrade 破坏核心数据；
- 无法真实验证 Windows 发声。

---

# 32. Final Release Artifact

若 GO：

生成：

```text
Moodify Desktop 0.1.0-alpha.N
├── installer
├── SHA256SUMS
├── BUILD_INFO
├── RELEASE_NOTES
├── TEST_EVIDENCE
├── KNOWN_ISSUES
├── SECURITY_NOTES
└── ROLLBACK.md
```

---

# 33. Release Notes

必须区分：

### Verified

真正测试过。

### Known limitations

真实存在。

### Not included

明确未做。

禁止营销性声明：

- best sound
- bit-perfect
- hi-res guaranteed
- AI always improves music

这些不是本 Gate 的技术结论。

---

# 34. Rollback

必须写：

```text
last known good version
how to uninstall current
how to install previous
local state compatibility
session behavior
```

即使 Alpha，也要有基本回退路径。

---

# 35. 禁止项

MFD-008 严禁：

- 新产品功能开发
- 新 API 设计
- 新 UI redesign
- WASAPI
- native audio
- DSP
- Cloud 重构
- Ear 重构
- 自动公开发布
- 未经授权创建正式 Release
- 修改验收标准掩盖失败
- 用 mock 替代真实播放证据

---

# 36. Definition of Done

本包完成必须：

1. RC frozen；
2. clean build verified；
3. installer verified；
4. SHA256 verified；
5. fresh install verified；
6. first launch verified；
7. auth verified；
8. library/track verified；
9. real playback verified；
10. audible verification complete；
11. seek verified；
12. manifest expiry verified；
13. offline/reconnect verified；
14. restart verified；
15. forced kill verified；
16. corrupted local state verified；
17. rapid interaction verified；
18. single instance verified；
19. tray/background verified；
20. media controls verified or blocker documented；
21. upgrade verified；
22. uninstall verified；
23. logging/security verified；
24. update state verified；
25. compatibility matrix truthful；
26. resource sanity recorded；
27. defects classified；
28. release artifacts complete；
29. rollback written；
30. final GO / CONDITIONAL GO / NO-GO issued。

---

# 37. 最终回报格式

Codex 最终回复只报告：

1. RC identity
2. build result
3. installer result
4. playback result
5. audible verification
6. auth/security result
7. recovery result
8. upgrade/uninstall result
9. compatibility
10. defects by severity
11. signing/update status
12. artifacts
13. release decision
14. exact blockers if NO-GO

最后必须单独给出：

> `MOODIFY DESKTOP 0.1 ALPHA: GO / CONDITIONAL GO / NO-GO`
