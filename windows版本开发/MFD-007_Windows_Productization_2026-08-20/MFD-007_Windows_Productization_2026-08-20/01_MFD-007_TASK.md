# MFD-007 — Windows Productization
## Codex 正式执行任务书

**任务编号：** MFD-007  
**执行对象：** Codex  
**执行模式：** Windows 产品化 / OS 集成 / Release Engineering  
**前置条件：** MFD-006 = GO

---

# 0. 核心目标

本包不继续“加功能”。

本包负责把已有 Moodify Minimal Player：

> **封装成一个真实 Windows 应用。**

工程输出应该从：

```text
npm run dev
```

进入：

```text
Install
→ Launch
→ Use
→ Update-ready
→ Uninstall
```

---

# 1. Preflight

开始前确认：

- MFD-006 = GO；
- Desktop repo clean；
- playback stable；
- local state stable；
- session persistence stable；
- package baseline stable；
- current Electron Forge config；
- current maker；
- app name；
- package id；
- version；
- icon assets；
- license；
- release repository / artifact destination；
- 是否已有 Windows code-signing credential。

记录：

```text
branch
SHA
Node
Electron
Forge
Windows version
maker
arch
```

---

# 2. Application Identity

建立稳定、以后不轻易修改的 Windows 产品身份。

至少确认：

```text
Product Name: Moodify
Desktop Product: Moodify Desktop
Executable: Moodify.exe
Package ID: stable reverse-domain or approved identifier
Publisher: company/approved publisher identity
Version: SemVer
```

不要让：

```text
moodify-desktop-dev.exe
electron.exe
my-new-app.exe
```

进入 Alpha 发布物。

---

# 3. Versioning

统一采用明确版本策略。

推荐：

```text
0.1.0-alpha.1
0.1.0-alpha.2
...
0.1.0
```

要求：

- package version 是唯一版本源；
- UI / logs / release artifacts 读取同一版本；
- 不手工维护多份不同版本号；
- build metadata 可记录 commit SHA；
- release note 与 artifact 对应。

---

# 4. Windows Installer

基于 MFD-002 已选打包主线。

如使用 Electron Forge + Squirrel.Windows：

至少配置：

- app name；
- exe；
- installer name；
- icon；
- authors / publisher metadata；
- shortcut behavior；
- install/uninstall behavior；
- package output；
- architecture。

不得同时加入：

```text
Squirrel
+
NSIS
+
WiX
+
MSIX
```

四套竞争 installer。

一个 Alpha 只保留一条主线。

---

# 5. Squirrel Lifecycle

如果使用 Squirrel.Windows：

必须正确处理安装生命周期事件，包括：

```text
install
updated
uninstall
obsolete
first run
```

确保：

- shortcut 行为正确；
- update lifecycle 不被普通 app startup 干扰；
- uninstall 不留下错误启动项；
- first-run update check 不与安装锁冲突。

不要把 Squirrel 启动参数当正常产品参数。

---

# 6. Shortcut / Start Menu

验证：

- Start Menu entry；
- desktop shortcut 是否符合产品决策；
- shortcut target 正确；
- upgrade 后 shortcut 仍可用；
- uninstall 后清理。

不要擅自创建大量 shortcut。

---

# 7. App Icon

需要形成 Windows 基础 icon asset。

要求：

- `.ico`；
- 多尺寸；
- tray icon 可单独准备；
- installer / executable / taskbar 一致；
- 不使用开发默认 Electron icon。

如果当前 Logo 资产不符合 Windows icon 技术要求：

> 只做技术适配，不擅自重新设计品牌 Logo。

---

# 8. Single Instance

MFD-002 如果已经存在 single-instance guard：

在 packaged build 再验证。

要求：

```text
launch Moodify
launch Moodify again
→ existing instance focused
→ no second playback instance
```

禁止出现：

> 两个 Moodify 同时播放两首歌。

---

# 9. Tray

本包允许第一次加入 tray。

目标：

- Moodify icon；
- Restore / Show；
- Play / Pause 可选；
- Quit。

保持极简。

不要加入：

- 复杂菜单；
- library；
- DSP；
- settings tree；
- marketing links。

---

# 10. Close / Minimize Policy

明确产品行为。

推荐 Alpha：

```text
Minimize
→ background playback continues

Window close (X)
→ follow explicit product policy
```

必须避免用户无法理解“窗口关了但声音还在”。

若选择：

```text
X → minimize to tray
```

需要：

- 第一次行为提示，或
- UI/托盘行为足够明确。

若选择：

```text
X → quit
```

则声音必须停止。

只能有一套一致行为。

---

# 11. Background Playback

验证：

- window minimized；
- window hidden to tray；
- screen locked（如可测）；
- another app focused。

Moodify 应继续播放，除非系统自身暂停媒体。

不要为了后台播放创建隐藏第二播放器。

---

# 12. Windows Media Controls

本包允许接入 Windows 媒体控制。

优先评估当前 Electron / Chromium 可用的标准媒体会话能力。

需要让系统识别：

```text
Track title
Artist
Playback state
Play
Pause
Next
Previous
```

如果 Media Session API 足够：

> 优先标准能力。

不要为了媒体键直接引入 native C++。

---

# 13. Media Key Behavior

验证：

- keyboard hardware play/pause；
- next；
- previous；
- Windows media overlay / system surface（如当前系统显示）；
- 状态和 Moodify UI 同步。

严禁形成第二套播放状态。

系统媒体动作最终仍调用现有 Playback intent / PlaybackEngine。

---

# 14. Packaged Logging

开发日志与发布日志分开。

Packaged Alpha 至少需要：

- app start；
- app version；
- OS；
- fatal error；
- playback-domain error code；
- update-domain status；
- local-state migration outcome。

日志位置必须明确。

禁止：

- token；
- refresh token；
- full signed URL；
- authorization header；
- service key；
- private audio path；
- raw user private metadata。

需要：

- log rotation / size bound，或
- 明确简单上限策略。

---

# 15. Crash-safe Startup

验证 packaged build：

- corrupted local state；
- expired token；
- network unavailable；
- stale manifest；
- missing optional asset；
- tray initialization failure；
- update service unavailable。

任何一个都不应该让 App 启动即白屏退出。

---

# 16. Update Architecture

本包要建立更新边界，但不强制立刻公开启用自动更新。

目标抽象：

```text
UpdateService
├── check
├── available
├── download
├── ready
├── install
└── error
```

如使用 Squirrel.Windows：

优先利用 Electron `autoUpdater` / Forge 对应机制。

---

# 17. Update Channel

至少定义：

```text
internal-alpha
public-alpha
stable (future)
```

MFD-007 不需要全部部署。

但更新 feed / artifact 必须不能混淆。

不要让 internal alpha 自动升级到 public/stable，反之亦然。

---

# 18. Auto-update 启用 Gate

如果当前没有可靠：

- code signing；
- update artifact host；
- HTTPS；
- release metadata；
- rollback plan；

则：

> UpdateService 可以实现与测试，但默认关闭真实自动更新。

使用 feature/config gate，例如：

```text
UPDATE_ENABLED=false
```

但不要把逻辑写死成永远关闭。

---

# 19. Update Feed Security

要求：

- HTTPS；
- allowlisted update origin；
- 不允许 renderer 任意更改 feed URL；
- 不从用户输入读取 update server；
- release metadata 可追踪；
- 不把 infrastructure secret 打进客户端。

---

# 20. First-run Update Timing

如使用 Squirrel.Windows：

注意安装后首次启动期间可能存在安装器文件锁。

不得：

```text
app starts
→ immediately update check
→ fail
→ treat as fatal
```

应通过：

- first-run flag 判断，或
- 合理延迟。

Update failure 永远不应阻塞播放主体验。

---

# 21. Code Signing

本包必须建立 code-signing readiness。

分两种状态：

## SIGNING_AVAILABLE

则：

- 配置 Forge signing；
- secret 只在 CI / signing environment；
- 签名 exe / installer；
- 验证签名。

## SIGNING_NOT_AVAILABLE

则：

- internal Alpha 可以继续生成 unsigned artifact；
- 明确 `UNSIGNED_INTERNAL_ALPHA`；
- public external release gate = BLOCKED；
- 不把 certificate/private key 放仓库；
- 记录后续获取签名能力需要的人类动作。

---

# 22. Signing Secret Discipline

严禁提交：

- `.pfx`
- private key
- password
- signing token
- cloud signing credential

仓库中只能有：

- config schema
- environment variable names
- docs

---

# 23. Build Reproducibility

建立：

```text
clean checkout
→ install
→ verify
→ make/package
→ artifact
```

要求：

- lockfile；
- Node version；
- package manager；
- deterministic command；
- artifact naming；
- version embedding。

推荐 artifact naming：

```text
Moodify-Desktop-0.1.0-alpha.1-win-x64-setup.exe
```

根据 maker 实际格式调整。

---

# 24. Release Artifacts

至少产生：

```text
installer
checksums
release-notes
build-info
```

`build-info` 建议：

```text
version
commit
build date
Node
Electron
Forge
arch
signed yes/no
channel
```

---

# 25. Checksums

至少生成：

```text
SHA256
```

用于：

- artifact integrity；
- release evidence。

不要把 checksum 当代码签名替代品。

---

# 26. CI Release Boundary

如果使用 GitHub Actions：

至少区分：

```text
CI verify
Package
Release
```

发布行为不能在普通 PR 自动发生。

要求：

- release trigger 明确；
- signing secrets 只进入 release job；
- artifact retention；
- no production release from untrusted PR context。

本包不要求自动 push release，除非人类另行授权。

---

# 27. Publishing

本包可以配置发布能力。

但：

> **不要未经明确授权自动发布 GitHub Release、上传生产更新服务器、推送公开安装包。**

完成“可发布工程”与“实际公开发布”是两件事。

---

# 28. Uninstall

真实验证：

- app 可卸载；
- binary 移除；
- shortcut 移除；
- update hooks 清理。

用户本地偏好 / session 是否删除必须明确。

Alpha 推荐：

> session secret 应安全删除。

对非敏感 preferences 可以根据产品策略保留或删除，但必须记录。

---

# 29. Clean Install / Upgrade

至少测试：

```text
clean install
launch
use
quit

install alpha.2 over alpha.1
launch
local state migration
session behavior
playback
```

如果还没有真实第二版本：

使用测试版本号构建模拟升级。

不要跳过 upgrade path。

---

# 30. Windows Compatibility

Phase 1 至少验证：

```text
Windows 11 x64
Windows 10 x64（如果项目仍承诺支持）
```

如果实际 Electron 当前版本或产品决定不支持某版本：

> 用真实兼容性结论修正矩阵，不要伪造支持。

MFD-008 会做最终 release gate。

---

# 31. Security Audit

Packaged app 至少确认：

- no source-level secret；
- no `.env` secret bundled；
- no service key；
- no DB credential；
- no signing key；
- no development server URL；
- no arbitrary remote content；
- no disabled webSecurity；
- preload boundary retained；
- update origin controlled。

---

# 32. 禁止项

严禁：

- WASAPI
- ASIO
- native audio addon
- DSP
- EQ
- new playback pipeline
- offline full library
- background mass audio download
- local music scanner
- upload workflow
- recommendation
- social
- skin marketplace
- macOS package
- Linux package
- Microsoft Store submission
- public release without human authorization
- signing private key commit
- production update publishing without authorization

---

# 33. Definition of Done

必须全部满足：

1. stable app identity；
2. stable package id；
3. SemVer versioning；
4. Windows installer successfully built；
5. correct app icon；
6. Start Menu / shortcut verified；
7. single instance verified；
8. tray works；
9. background playback works；
10. close/minimize behavior consistent；
11. Windows media control works or has evidence-based blocker；
12. packaged logging works；
13. logs redact sensitive data；
14. crash-safe startup verified；
15. UpdateService boundary exists；
16. update channel defined；
17. update feed security defined；
18. first-run update behavior handled；
19. signing readiness assessed；
20. signed build if credential exists, otherwise unsigned clearly marked internal-only；
21. clean build reproducible；
22. SHA256 generated；
23. release notes/build info generated；
24. clean install verified；
25. uninstall verified；
26. upgrade path verified；
27. security audit passed；
28. no public publishing without authorization；
29. evidence complete。

---

# 34. 最终回报

Codex 最终只报告：

1. app identity
2. installer/maker
3. build artifacts
4. tray/background behavior
5. Windows media controls
6. packaged logs
7. update architecture
8. signing status
9. clean install/uninstall
10. upgrade test
11. security audit
12. checksums
13. known blockers
14. diff summary
15. MFD-008 readiness

最后：

> `MFD-008: GO / CONDITIONAL GO / NO-GO`
