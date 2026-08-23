# Moodify Windows Desktop Completion — W12 Release Hardening 发布工程

**Package ID:** `MFY-WIN-W12-RELEASE-HARDENING-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 12 of 12  
**任务类型：** Release Engineering / Hardening / Distribution  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W11 `W12_GATE = PASS`  
**阶段结果：** Windows Alpha → Windows Beta Candidate

---

## 1. W12 的目标

W12 不是继续加功能。

W12 只回答：

> 现在这个 Windows 版本，是否已经可以被真实用户安装、升级、卸载、长期使用，并且不会轻易破坏用户数据？

本包完成：

```text
Source Tree
→ Build
→ Package
→ Install
→ First Run
→ Upgrade
→ Migrate
→ Run
→ Crash / Recover
→ Uninstall
→ Reinstall
→ Verify Data Safety
→ Release Candidate
```

---

## 2. W12 的原则

### 不再扩功能

W12 禁止以“发布前顺便补一下”为理由继续扩产品范围。

允许的改动：

- 修 bug
- 修崩溃
- 修数据损坏风险
- 修升级风险
- 修性能退化
- 修安全问题
- 修安装/卸载/启动问题
- 修日志/诊断缺口
- 修真实发布 blocker

不允许：

- 新功能
- 新业务 authority
- 新页面大改
- 新社交/推荐
- 新云能力
- 新 DSP/Ear 功能
- UI redesign

---

## 3. W12 要做

- release preflight
- version/build identity
- production build reality
- installer
- uninstaller
- upgrade path
- downgrade policy
- schema migration verification
- settings migration
- recovery snapshot migration
- file association registration
- file association cleanup
- startup registration if supported
- single-instance install behavior
- data/cache path verification
- uninstall data retention policy
- logging
- crash diagnostics
- privacy-safe diagnostics
- performance regression
- security regression
- network/cloud regression
- offline regression
- clean-machine install test
- upgrade-from-previous-build test
- uninstall/reinstall test
- release artifact checksums
- signing seam
- update seam
- release checklist
- Windows Beta release gate

---

## 4. 不做

- 继续设计产品
- 新功能
- 完整商业支付系统
- 新账号体系
- 推荐算法
- 社区
- 皮肤市场
- DSP/EQ
- Ear UI
- creator backend
- 云端架构重建
- 大规模 CI/CD 平台重建
- 复杂自动更新服务，若当前无安全基础

---

## 5. W12 完成后的标准

用户应该可以：

```text
下载 installer
→ 安装 Moodify
→ 导入音乐
→ 使用
→ 安装新版本
→ 原数据仍然存在
→ Playlist 仍然存在
→ Settings 正常迁移
→ Queue/Recovery 不崩
```

以及：

```text
卸载 Moodify
→ 明确知道是否保留用户数据
→ 重新安装
→ 行为符合策略
```

---

## 6. 发布不是“build 成功”

真正的发布闸门是：

```text
Installable
+ Upgrade-safe
+ Data-safe
+ Crash-diagnosable
+ Security-reviewed
+ Performance-regressed
+ Offline-safe
+ Cloud-claims-truthful
+ Reproducible enough
```

只有这些成立，才允许：

```text
WINDOWS_BETA_CANDIDATE = PASS
```
