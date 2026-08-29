# Release Invariants

## R-01 No New Product Scope
W12 不扩功能，只收口。

## R-02 User Data Is More Important Than Convenience
升级失败也不能静默清空数据。

## R-03 Installer Never Touches Original Music
安装/卸载/升级均不删除用户音频源文件。

## R-04 Upgrade Must Be Tested, Not Assumed
“schema 看起来兼容”不等于升级安全。

## R-05 Migration Is Idempotent
重复启动/重复安装不能重复破坏数据。

## R-06 Production Build Has No Dev Dependency
不可依赖 repo、开发服务器、开发机环境。

## R-07 Release Logging Is Privacy-safe
日志不可成为秘密/隐私泄漏通道。

## R-08 Crash Must Be Diagnosable
Beta 不是“不崩”，而是“崩了能定位且不会循环崩”。

## R-09 Offline Is Core
本地音乐播放器不能因为云端不可用而无法启动。

## R-10 Cloud Claims Follow W10 Evidence
不能宣传未验证能力。

## R-11 Native Integration Must Survive Install Lifecycle
文件关联/启动项/托盘/单实例不能只在 dev 环境可用。

## R-12 No Forced Default Hijack
用户默认播放器选择必须被尊重。

## R-13 Release Artifact Must Be Identifiable
版本、build、commit、hash 都可追踪。

## R-14 Signing Status Must Be Truthful
未签名就写未签名。

## R-15 Update Must Be Verifiable
未来 updater 不能执行未验证下载。

## R-16 P0/P1 Block Beta
严重问题未清零，不准发布。
