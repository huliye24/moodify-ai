# Codex 执行任务书 — MFY-WIN-W12-RELEASE-HARDENING-001

## 0. 执行模式

```text
PACKAGE = W12
FOCUS = RELEASE_HARDENING
CANON_CHANGE = NO
VISUAL_REDESIGN = FORBIDDEN
ADD_MAJOR_FEATURE = NO
```

W12 是收口包。

---

## 1. Phase 0 — Preflight

读取：

```text
artifacts/windows/w11/W11_IMPLEMENTATION_REPORT.md
artifacts/windows/w11/W12_HANDOFF.md

artifacts/windows/w08/W08_IMPLEMENTATION_REPORT.md
artifacts/windows/w09/W09_IMPLEMENTATION_REPORT.md
artifacts/windows/w10/W10_IMPLEMENTATION_REPORT.md
```

输出：

`artifacts/windows/w12/preflight.md`

至少：

```text
W11_STATUS =
W12_GATE =
APP_VERSION_REALITY =
BUILD_TOOLCHAIN =
PACKAGING_TOOLCHAIN =
INSTALLER_REALITY =
UNINSTALLER_REALITY =
SIGNING_REALITY =
UPDATE_REALITY =
DATA_LOCATIONS =
CACHE_LOCATIONS =
DB_SCHEMA_VERSION =
SETTINGS_SCHEMA_VERSION =
RECOVERY_SCHEMA_VERSION =
FILE_ASSOCIATION_NEEDS =
STARTUP_REGISTRATION_NEEDS =
LOGGING_REALITY =
CRASH_DIAGNOSTIC_REALITY =
```

若 `W12_GATE != PASS`，停止。

---

## 2. Phase 1 — Freeze Release Scope

建立：

`artifacts/windows/w12/release-scope-freeze.md`

明确：

### IN
- bug fix
- blocker fix
- migration fix
- performance fix
- security fix
- packaging fix
- installation fix
- crash fix
- diagnostics fix

### OUT
- new product features
- visual redesign
- new cloud feature
- new authority
- new DSP/Ear UI
- new community/recommendation

任何新增需求必须标：

```text
DEFER_TO_NEXT_RELEASE
```

---

## 3. Phase 2 — Version / Build Identity

建立统一版本来源。

推荐至少：

```text
product_version
build_number
git_commit
build_channel
build_time
```

用户可见只需要：

```text
Moodify x.y.z
```

内部日志可记录：

```text
x.y.z + build + commit
```

禁止多个 package/config 文件各自维护不一致版本。

输出：

`artifacts/windows/w12/versioning-policy.md`

---

## 4. Phase 3 — Production Build

确认真实 production build：

- no dev server dependency
- no debug-only bridge
- no localhost hidden dependency
- no source-map secret leakage
- no test credential
- no hardcoded service-key
- no developer-only feature accidentally enabled
- no missing production asset
- no absolute developer machine path

输出：

`artifacts/windows/w12/production-build-audit.md`

---

## 5. Phase 4 — Installer

基于真实 runtime/packaging toolchain 建 installer。

Installer 至少处理：

```text
install app binaries
install app identity/icon
create uninstall entry
optional Start Menu entry
optional desktop shortcut
file association registration if approved
startup registration only if user setting + supported
```

### Installer Must Not

- clear old data
- force file default ownership
- install service secrets
- silently add startup if user did not choose it
- write broad machine-wide permissions unnecessarily

### Install Scope

明确：

```text
per-user
or
per-machine
```

优先按当前产品最安全、最低权限方式。

---

## 6. Phase 5 — Uninstaller

必须定义用户数据策略。

推荐分离：

```text
Application Files
User Data
Cache
Original Music
```

### Default Uninstall

推荐：

```text
remove app binaries
remove registered integrations
remove cache optionally
preserve user Library/Playlist data unless user explicitly chooses removal
never touch original music files
```

如果当前 installer 无交互能力，必须明确固定策略。

输出：

`artifacts/windows/w12/uninstall-data-policy.md`

---

## 7. Phase 6 — Upgrade

至少测试：

```text
old build
→ install new build over old
→ launch
→ migrations
→ data intact
```

必须覆盖：

- Library DB
- Playlist
- Favorite
- History
- Settings
- Recovery snapshot
- Queue snapshot
- cloud preparation mapping
- native integration registrations

### Upgrade Must Be Idempotent

重复安装同版本 / 再次启动不能重复迁移破坏数据。

---

## 8. Phase 7 — Migration Matrix

建立：

`artifacts/windows/w12/migration-matrix.md`

至少包含：

```text
component
old_version
new_version
migration
rollback/fallback
verification
```

覆盖：

- Library schema
- Playlist schema
- Favorite/History
- Queue/Recovery
- Settings
- CloudPreparation
- file association registration
- startup registration
- cache metadata if any

### P0

任何 migration 失败：

```text
do not silently wipe user data
```

---

## 9. Phase 8 — Downgrade Policy

必须明确：

```text
SUPPORTED
UNSUPPORTED_BUT_SAFE
BLOCKED
```

如果新版本 schema 不兼容旧版本：

推荐：

```text
downgrade not supported
```

但旧版本启动时应尽量检测并拒绝，而不是错误读取后损坏数据。

输出：

`artifacts/windows/w12/downgrade-policy.md`

---

## 10. Phase 9 — File Associations

如果 W09 已准备 association seam：

W12 实施 installer-level registration。

规则：

- 只注册真实支持格式
- 出现在 Open With
- 不强制抢默认
- uninstall 清理 association registration
- upgrade 不重复污染
- user later changed default → respect

测试：

- install
- open with
- uninstall
- reinstall
- upgrade

---

## 11. Phase 10 — Startup Registration

只有：

- W09/W11 capability supported
- user setting ON

才注册 startup。

默认 OFF。

升级不得把 OFF 变 ON。

卸载必须清理 startup entry。

---

## 12. Phase 11 — Data Location Audit

输出：

`artifacts/windows/w12/data-location-map.md`

至少列：

```text
app binaries
Library DB
Playlist/Favorite/History
Settings
Recovery
Queue snapshot
Logs
Crash diagnostics
Cache
Cloud temporary assets
Prepared cache
```

必须验证：
- 路径稳定
- 用户权限正确
- 不写 Program Files 等不可写目录
- 不依赖 repo cwd
- 不依赖开发机绝对路径

---

## 13. Phase 12 — Logging

建立 production logging 最小标准。

至少：

```text
startup
shutdown
version/build
migration
player fatal error
database error
cloud request failure summary
native integration failure
recovery failure
unexpected exception
```

### Log Level

推荐：

```text
INFO
WARN
ERROR
```

不要默认 debug flood。

### Privacy

不要记录：
- token
- password
- service-key
- signed URL
- private audio content
- unnecessary full filesystem path
- raw user metadata unless diagnostic necessity

输出：

`artifacts/windows/w12/logging-policy.md`

---

## 14. Phase 13 — Crash Diagnostics

建立最小 crash evidence：

```text
app version
build
OS version
runtime version
exception type
stack trace
last safe subsystem markers
```

不要自动上传，除非已有明确合规/用户授权体系。

W12 只要求：

```text
local diagnosable crash artifact
```

或真实已存在的安全 crash solution。

输出：

`artifacts/windows/w12/crash-diagnostics-policy.md`

---

## 15. Phase 14 — Crash Loop Protection

如果启动连续崩溃：

必须避免：

```text
launch
→ restore bad session
→ crash
→ launch
→ restore same bad session
→ crash forever
```

推荐：

```text
detect repeated startup failure
→ disable session restore once
→ safe mode startup
```

这里的 safe mode 只指：

```text
skip transient session restore
```

不是 developer mode。

不能清 Library。

---

## 16. Phase 15 — Performance Regression

建立 release baseline：

至少：

```text
cold start
warm start
1000 Track library render
5000 Track search
playlist open
play start latency
next-track latency
queue reorder
settings open
memory after 30 min playback
```

不追求实验室极限，但要识别明显回退。

输出：

`artifacts/windows/w12/performance-regression.md`

---

## 17. Phase 16 — Stability Soak

至少执行合理 soak：

```text
continuous playback
queue advance
track switching
pause/resume
background/minimize
network online/offline
cloud status refresh if enabled
```

建议：

```text
2–4 hours automated/manual soak
```

若时间环境不允许，记录实际完成时长。

关注：
- memory growth
- duplicate listeners
- stuck playback
- queue drift
- log flood
- CPU runaway

输出：

`artifacts/windows/w12/soak-test-report.md`

---

## 18. Phase 17 — Security Regression

必须重新检查：

- client secrets
- native IPC
- shell execution
- open-file paths
- single-instance payload
- cloud auth
- signed URLs
- log leakage
- installer permissions
- writable executable directories
- unsafe update seam
- temp files

输出：

`artifacts/windows/w12/security-regression.md`

### Release Blocker

发现以下任一：

```text
service/admin secret in client
arbitrary command execution
untrusted update execution
data wipe risk
```

必须：

```text
RELEASE_BLOCKED
```

---

## 19. Phase 18 — Offline Regression

断网情况下必须证明：

```text
launch
Library
Playlist
local Playback
Queue
Settings
Recovery
```

仍可用。

Cloud UI：

```text
network unavailable
```

不得卡死应用启动。

---

## 20. Phase 19 — Cloud Claims Audit

读取 W10 实际结果。

对发布 UI/文案/README 检查：

```text
What is actually verified?
What is partial?
What is unavailable?
```

禁止 installer/website/build metadata 暗示不存在的完整 AI pipeline。

输出：

`artifacts/windows/w12/cloud-claims-audit.md`

---

## 21. Phase 20 — Clean Machine Install Test

至少在干净/近似干净环境验证：

```text
no dev dependencies
no repo
no Node/Python assumption unless bundled
no local env vars required
no manual npm install
```

测试：

```text
install
launch
import
play
restart
uninstall
```

如果无法获得 VM/clean machine：
必须做最接近的隔离测试并记录局限。

---

## 22. Phase 21 — Upgrade Test

至少：

```text
previous Alpha build
→ create Library/Playlist/Settings
→ install candidate
→ migrate
→ verify
```

要求数据对比：

- Track count
- Playlist count
- PlaylistItem count
- Favorites
- History
- Settings
- Queue/recovery
- cloud preparation refs if present

---

## 23. Phase 22 — Uninstall / Reinstall Test

必须验证：

### Policy A: preserve user data

```text
install
→ use app
→ uninstall
→ reinstall
→ data returns
```

或者如果产品明确选择删除：
必须通过用户确认和文档。

无论哪种：
原始音乐永远不能被卸载器删除。

---

## 24. Phase 23 — Release Artifact Integrity

生成：

```text
installer artifact
version
size
SHA256
build commit
build channel
```

输出：

`artifacts/windows/w12/release-artifact-manifest.json`

不得把 secret 打进 manifest。

---

## 25. Phase 24 — Code Signing Seam

如果已有 Windows code signing certificate：
接入并验证。

如果没有：

```text
SIGNING = NOT_CONFIGURED
```

但必须：
- 记录未来签名步骤
- 不伪造“已签名”
- 明确 SmartScreen 风险
- packaging 不依赖虚假证书

输出：

`artifacts/windows/w12/signing-status.md`

---

## 26. Phase 25 — Update Seam

如果已有安全 updater：
审计并接入。

如果没有：
W12 只定义：

```text
update manifest contract
download verification
signature/hash verification
rollback expectation
```

不要临时造一个“下载 exe 后直接执行”的不安全 updater。

输出：

`artifacts/windows/w12/update-seam.md`

---

## 27. Phase 26 — Release Channel

至少定义：

```text
ALPHA
BETA
STABLE
```

本包目标：

```text
BETA_CANDIDATE
```

版本 UI/日志/installer 文件名必须一致。

---

## 28. Phase 27 — Release Checklist

建立：

`artifacts/windows/w12/RELEASE_CHECKLIST.md`

至少包含：

- build
- tests
- installer
- migration
- uninstall
- security
- performance
- offline
- cloud claims
- signing
- checksums
- known issues
- rollback
- release notes

---

## 29. Phase 28 — Known Issues

建立：

`artifacts/windows/w12/KNOWN_ISSUES.md`

只记录真实已知问题。

分类：

```text
P0 BLOCKER
P1 MUST FIX BEFORE BETA
P2 ACCEPTED BETA LIMITATION
P3 FOLLOW-UP
```

P0/P1 未清零不能进入 Beta。

---

## 30. Phase 29 — Final Beta Gate

最终输出：

```text
WINDOWS_BETA_CANDIDATE = PASS | BLOCKED
```

PASS 需要：

```text
W12_STATUS = PASS
P0 = 0
P1 = 0
INSTALLER = PASS
UPGRADE = PASS
UNINSTALL = PASS
DATA_SAFETY = PASS
SECURITY = PASS
OFFLINE = PASS
PERFORMANCE = PASS
CLOUD_CLAIMS = PASS
```

签名若未配置，可以是已知 Beta 限制，是否阻塞取决于真实分发方式，但必须明确风险。

---

## 31. Required Outputs

写入：

`artifacts/windows/w12/`

至少：

1. `W12_IMPLEMENTATION_REPORT.md`
2. `preflight.md`
3. `release-scope-freeze.md`
4. `versioning-policy.md`
5. `production-build-audit.md`
6. `installer-contract.md`
7. `uninstall-data-policy.md`
8. `migration-matrix.md`
9. `downgrade-policy.md`
10. `data-location-map.md`
11. `logging-policy.md`
12. `crash-diagnostics-policy.md`
13. `performance-regression.md`
14. `soak-test-report.md`
15. `security-regression.md`
16. `offline-regression.md`
17. `cloud-claims-audit.md`
18. `clean-machine-test.md`
19. `upgrade-test.md`
20. `uninstall-reinstall-test.md`
21. `signing-status.md`
22. `update-seam.md`
23. `release-artifact-manifest.json`
24. `KNOWN_ISSUES.md`
25. `RELEASE_CHECKLIST.md`
26. `evidence-manifest.json`
27. `WINDOWS_BETA_GATE.md`

---

## 32. Final Status

必须以：

```text
W12_STATUS = PASS | BLOCKED
WINDOWS_BETA_CANDIDATE = PASS | BLOCKED
CANON_CHANGE = NO
VISUAL_REDESIGN = NO
```

结束。
