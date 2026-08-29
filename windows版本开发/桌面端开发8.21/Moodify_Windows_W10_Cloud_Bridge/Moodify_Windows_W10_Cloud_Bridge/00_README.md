# Moodify Windows Desktop Completion — W10 Moodify Cloud Bridge 云端入口

**Package ID:** `MFY-WIN-W10-CLOUD-BRIDGE-001`  
**日期：** 2026-08-21  
**阶段：** Windows Desktop Completion / 10 of 12  
**任务类型：** Product Integration / Cloud Bridge  
**CANON_CHANGE：** `NO`  
**VISUAL_REDESIGN：** `FORBIDDEN`  
**前置依赖：** W09 `W10_GATE = PASS`  
**下一包：** W11 — Settings & Audio Environment

---

## 1. W10 的目标

W10 是 Windows 版本第一次真正进入 Moodify 产品差异化的阶段。

W02-W09 已经让 Windows 端成为一个可靠播放器。

W10 要建立：

```text
Local Source
→ Moodify Cloud Request
→ Preparation State
→ Cloud-prepared Track
→ Playback Source Switch
→ PLAY
```

但必须服从当前真实云端能力，而不是把尚未上线的内部研究链路伪装成生产能力。

---

## 2. 产品外部状态必须极简

用户只需要理解：

```text
原始音乐
→ 正在准备…
→ 准备完成
→ ▶ Play
```

不得向普通用户展示：

```text
Ear
Analyze
Stem
Judge
Intervene
Render
Verify
Evidence
Job State Machine
DSP Parameters
```

这些仍然是 Moodify 内部生产系统。

---

## 3. 当前云端现实约束

执行前必须基于真实 W01 / cloud evidence 再次确认，不能仅使用历史文档。

已知历史基线包括：

- 云端曾确认存在网站 / API / worker / Audiolla proxy 等服务；
- 对象存储曾是 P0 缺口；
- 完整 `上传 → 处理 → 返回` 的生产链路曾未验证；
- Audiolla/LALAL.AI 是第三方云端能力，不等于 Moodify 本地 AI inference；
- Moodify Ear 代码存在不等于生产云端正在自动执行；
- 不允许把未验证能力写成“已上线”。

W10 的第一任务不是“强行接上云”，而是：

> 识别今天真实可用的云端入口，并只把已验证的部分接入 Windows。

---

## 4. W10 要做

- Windows Cloud API client reality audit
- Cloud capability matrix
- Local Track → Cloud Request seam
- CloudTrack / CloudPreparation 最小模型
- upload/request contract（仅真实支持时）
- preparation polling / status refresh
- idempotency
- retry/backoff
- timeout/cancel
- authentication boundary
- secure endpoint/config handling
- cloud response validation
- cloud-prepared source attachment
- source selection policy
- fallback to local source
- offline/network-error behavior
- cloud status persistence
- restart-safe preparation state
- minimal UI states
- telemetry/evidence
- tests
- W11 handoff

---

## 5. 本包不做

- 自己实现新的 AI 模型
- 在客户端暴露 Ear
- 在客户端暴露 stem
- 让用户操作内部生产参数
- 假装完整 production pipeline 已上线
- 云端训练控制台
- creator backend
- 用户社区
- recommendation
- skin marketplace
- payment
- account system redesign
- UI redesign

---

## 6. W10 完成后的理想体验

### 已验证云链可用时

```text
用户导入歌曲
→ 选择/触发“用 Moodify 准备”
→ 上传/请求
→ 正在准备…
→ 准备完成
→ Moodify 自动优先播放 cloud-prepared source
```

### 云端不可用时

```text
云端不可用
→ 本地 Track 仍然存在
→ 本地播放仍然可用
→ 不破坏 Queue / Playlist / Library
```

---

## 7. 最重要的边界

### CloudTrack 不能替代 Track authority

推荐：

```text
Track
 ├── local source
 └── cloud preparation mapping
```

而不是：

```text
CloudTrack = 第二个完全独立的 Track 世界
```

### Cloud preparation 不是 Playback authority

Cloud 只提供：

```text
prepared source
```

Playback 仍由 W04 决定怎么播放。

### Cloud unavailable ≠ app unavailable

Windows 本地播放器必须保持可用。

### Never Overclaim

任何状态必须基于真实后端证据。

如果今天真实云端只支持：

```text
upload accepted
```

那么 UI 只能做到：

```text
已提交 / 正在准备
```

不能假装：

```text
准备完成
```
