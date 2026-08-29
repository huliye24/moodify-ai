# MFD-008 — Alpha Release Gate

**项目：** Moodify  
**阶段：** Moodify Desktop Phase 1 — Windows Alpha  
**任务包编号：** MFD-008  
**日期：** 2026-08-20  
**执行对象：** Codex  
**性质：** 最终验收 / Release Candidate 审计 / Alpha 发布门  
**优先级：** P0  
**前置任务：** MFD-007 — Windows Productization  
**后续状态：** Moodify Desktop 0.1 Alpha 或返回修复

---

## 1. 本包目的

MFD-008 不允许继续增加功能。

它只回答一个问题：

> **当前 Moodify Desktop 是否已经达到可以被正式称为 “Moodify Desktop 0.1 Alpha” 的最低标准？**

本包必须对前七包建立的系统进行：

```text
事实核验
→ 构建核验
→ 安装核验
→ 播放核验
→ 故障核验
→ 安全核验
→ 升级核验
→ 卸载核验
→ 发行物核验
→ 最终 GO / NO-GO
```

---

## 2. Release Gate 原则

### 不补功能

发现缺陷：

> 记录、分类、阻塞或回退修复。

不要在 Gate 里继续“顺手开发”。

### 不掩盖失败

测试失败就是失败。

不得通过修改验收标准把失败变成通过。

### 真实环境优先

必须有真实 Windows 安装与真实音频播放证据。

### Evidence before release

没有证据，不得标记 PASS。

---

## 3. 本包最终可能得到三个结论

### ALPHA_GO

满足内部 / 受控 Alpha 发布条件。

### CONDITIONAL_ALPHA_GO

存在不影响核心体验的已知问题，但必须明确限制发行范围。

### ALPHA_NO_GO

存在核心播放、安全、安装、认证、恢复或发行阻塞。

---

## 4. 本包不做

- 新 UI
- 新 API
- 新音频算法
- 新 DSP
- WASAPI
- 新功能
- 新推荐
- 新皮肤
- 新社区
- macOS
- Linux
- iOS
- Cloud 重构
- Ear 重构

---

## 5. 核心验收句

只有当以下链路真实成立：

```text
用户取得安装包
→ 安装 Moodify
→ 启动
→ 恢复用户会话
→ 看见可播放曲目
→ Play
→ Windows 发声
→ 切歌 / Seek / Pause
→ 断网不崩
→ 重启可恢复
→ 升级不破坏
→ 卸载正常
```

才有资格进入 Alpha。
