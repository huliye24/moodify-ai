# MFD-009 — Alpha Field Validation & Evidence
## Codex 正式执行任务书

**任务编号：** MFD-009  
**执行对象：** Codex  
**执行模式：** Controlled Alpha / Evidence Collection / No Feature Expansion  
**前置条件：** MFD-008 = GO 或被批准的 CONDITIONAL GO

---

# 0. 总目标

你的任务不是继续开发功能。

你的任务是建立一套轻量、可重复、可审计的 Alpha 验证机制，让团队能够从真实使用中获得可靠证据。

目标输出：

```text
Alpha Cohort
+ Device Matrix
+ Reliability Evidence
+ Playback Evidence
+ Listening Evidence
+ Usage Evidence
+ Issue Backlog
+ Go/No-Go for next iteration
```

---

# 1. Alpha Cohort

建立受控测试人群。

建议首批：

```text
5–20 人
```

数量不是硬指标。

重点是：

- 能联系；
- 愿意反馈；
- 使用真实 Windows 设备；
- 有不同耳机 / 音箱 / 声卡环境；
- 不是全部内部开发者。

记录匿名或受控 tester id。

禁止为了数量公开大规模扩散。

---

# 2. Tester Matrix

至少记录：

```text
tester_id
Windows version
device class
CPU/RAM
audio output
headphone/speaker
network type
app version
```

避免收集不必要个人身份信息。

---

# 3. Alpha Build Discipline

所有 tester 必须对应明确：

```text
version
commit
installer SHA256
channel
signed/unsigned
```

不允许：

> 每个人拿到不同的“本地临时包”，最后无法复现问题。

---

# 4. Reliability Evidence

至少收集：

```text
install success
launch success
session restore
track load success
play success
pause/seek
next/previous
restart recovery
network recovery
unexpected exit/crash
upgrade
uninstall
```

每个故障都必须带：

```text
version
tester/device
time
action
result
error code if available
reproducibility
```

---

# 5. Playback Evidence

建立最小播放事件统计。

允许记录：

```text
app_start
track_load_success
track_load_failure
play
pause
seek
next
previous
playback_error
manifest_refresh
session_refresh
app_exit
```

禁止记录：

- signed URL；
- token；
- raw audio；
- private file；
- internal Ear evidence；
-完整个人音乐历史，如果不是必要。

---

# 6. Event Schema

每个技术事件至少：

```text
event_name
event_time
app_version
platform
anonymous_tester_or_install_id
track_id pseudonymous/product id
playback_error_code if any
request_id if safe
```

不要把 telemetry 设计成广告追踪系统。

---

# 7. Telemetry Delivery

优先：

> 轻量、可关闭、可审计。

如果当前 Cloud 已有合适事件入口，可复用。

如果没有：

可以先：

- 本地结构化日志；
- tester 主动上传 support bundle；
- 轻量受控 Alpha endpoint。

不要为了 Alpha 引入大型数据平台。

---

# 8. Support Bundle

建立一个安全的 Alpha support bundle。

包含：

```text
app version
OS
non-sensitive logs
local state schema version
recent playback error codes
build info
```

明确排除：

```text
token
refresh token
signed URL
service key
DB secret
private audio
raw personal data
```

最好支持：

```text
Export Diagnostics
```

但如果 UI 增加会扩大范围，可以仅提供受控开发命令或日志收集脚本。

---

# 9. Listening Evidence

Moodify 的核心承诺是：

> **让音乐更好听。**

因此 Alpha 验证不能只有“软件有没有崩”。

建立最小听感验证。

---

# 10. Listening Test Design

对一部分曲目进行：

```text
Reference
vs
Moodify Playback Version
```

原则：

- 相同歌曲；
- 尽可能匹配响度；
- 不告诉 tester 哪个是 Moodify；
- 随机 A/B 或 A/B/X；
- 不要求专业术语。

---

# 11. Listening Questions

每次只问非常少的问题。

建议：

```text
你更愿意继续听哪一个？
A / B / 无明显区别

哪个听起来更舒服？
A / B / 无明显区别

差异是否明显？
明显 / 轻微 / 无明显差异
```

可选自由文本：

```text
一句话描述差异
```

不要要求普通用户填写：

- LUFS；
- compression；
- transient；
- stereo width；
- phase。

---

# 12. Listening Evidence Integrity

必须避免：

- 只记录“喜欢 Moodify”的反馈；
- 删除负面评价；
- 把响度更大等同于更好；
- 用 2–3 个朋友的反馈宣称普遍提升；
- 把主观反馈写成科学结论。

输出：

```text
Preference Rate
No-difference Rate
Negative Preference Rate
Sample Size
Track Coverage
Device Coverage
```

---

# 13. Track Coverage

Alpha 不需要几百首。

建议先建立一个有差异的测试集：

```text
modern pop
old recording
vocal
dense mix
acoustic
electronic
rock
rap
```

使用真实合法可测试资产。

每类至少有代表样本即可。

---

# 14. Device Coverage

尽可能覆盖：

```text
laptop speakers
wired headphones
Bluetooth headphones
USB DAC / external sound card
powered speakers
```

不是为了第一阶段做设备优化。

而是确认：

> 当前 Moodify playback 在不同设备上没有明显破坏。

---

# 15. User Comprehension

观察：

- 用户是否知道怎么 Play；
- 是否知道怎么切歌；
- 是否因为极简 UI 不知道下一步；
- 是否误解 loading/error；
- 是否会寻找不存在的功能。

记录困惑点。

不要立即加按钮。

---

# 16. Core Usage Questions

Alpha 结束后至少回答：

```text
多少 tester 成功安装？
多少成功播放？
多少遇到阻塞？
多少第二次打开？
平均一次会话听几首？
最常见错误是什么？
最常见困惑是什么？
哪些控制几乎没人用？
```

不要把这些数字包装成增长 KPI。

这是产品诊断。

---

# 17. Second-session Signal

一个非常重要的 Alpha 信号：

> 用户是否愿意第二次打开 Moodify。

建议记录：

```text
first session
second session
7-day return if cohort duration allows
```

不要求做完整留存系统。

---

# 18. Feedback Intake

建立统一格式。

每条 feedback：

```text
feedback_id
tester_id
app_version
category
severity
description
reproduction
screenshot/log ref if safe
```

分类：

```text
BUG
RELIABILITY
PLAYBACK
UX
LISTENING
REQUEST
OTHER
```

---

# 19. Feature Requests

Alpha 用户一定会要求：

- 搜索；
- 歌词；
- 播放列表；
- EQ；
- 本地音乐；
- 皮肤；
- 离线；
- 更多按钮。

规则：

> **只记录，不立即实现。**

所有 feature request 进入：

```text
feature_request_backlog.md
```

MFD-010 再做熵减。

---

# 20. Issue Severity

继续使用：

```text
P0
P1
P2
P3
```

另增加：

```text
F — Feature request
```

Feature request 不是 bug。

---

# 21. Alpha Stop Conditions

出现以下任一情况，应暂停扩大 tester：

```text
security leak
wrong-user authorization
repeatable crash loop
install/uninstall destructive issue
widespread no-audio issue
session credential leak
signed URL leak
data corruption
```

先修。

不要继续采更多数据。

---

# 22. Privacy

必须明确 Alpha telemetry：

- 采什么；
- 不采什么；
- 保存多久；
- 谁能看到；
- tester 如何退出。

如果做远端采集，提供简短 Alpha privacy note。

---

# 23. No Dark Analytics

严禁：

- fingerprinting；
- advertising id；
- unrelated browsing behavior；
- hidden microphone capture；
- raw system inventory beyond troubleshooting need；
-未经说明的个人数据采集。

---

# 24. Daily / Batch Review

不要求每天做大型会议。

建议每完成一批 tester 后生成：

```text
Alpha Batch Report
```

包含：

```text
what worked
what broke
top errors
listening result
UX confusion
feature requests
new unknowns
```

---

# 25. Evidence Storage

推荐目录：

```text
artifacts/alpha_validation/
├── cohort/
├── reliability/
├── playback/
├── listening/
├── feedback/
├── reports/
└── sanitized_support_bundles/
```

不要提交：

- raw tokens；
- private audio；
- sensitive logs。

---

# 26. 最终 Alpha Validation Report

必须回答：

## Reliability
现在最不稳定的地方是什么？

## Product
用户是否理解 Minimal Player？

## Listening
Moodify playback 是否存在可感知偏好？

## Usage
用户是否愿意再次打开？

## Scope
哪些“看起来应该做”的功能其实没有证据？

## Risk
下一阶段最大的工程风险是什么？

---

# 27. 禁止项

本包严禁：

- 大规模功能开发；
- 立即实现所有用户需求；
- 重做 UI；
- 加 EQ；
- 加歌词；
- 加推荐；
- 加社区；
- 加皮肤市场；
- 加 WASAPI；
- 改 Ear 核心；
- 改 Cloud 大架构；
- 为了数据好看过滤负面反馈；
- 采集不必要个人数据。

---

# 28. Definition of Done

必须至少完成：

1. controlled cohort 定义；
2. tester matrix；
3. build identity 一致；
4. reliability evidence；
5. playback evidence；
6. support bundle；
7. listening test；
8. 至少若干真实曲目覆盖；
9. 至少若干真实设备覆盖；
10. UX comprehension 记录；
11. second-session 信号；
12. feature requests 独立记录；
13. defect backlog；
14. privacy note；
15. Alpha Batch Report；
16. final Alpha Validation Report；
17. 下一阶段问题清单；
18. 不在本包扩功能。

---

# 29. 最终回报

Codex 最终只报告：

1. cohort
2. devices
3. builds
4. install/play success
5. top reliability failures
6. top playback failures
7. listening evidence
8. second-session signal
9. UX confusion
10. feature requests
11. P0/P1 issues
12. privacy status
13. evidence paths
14. MFD-010 readiness

最后：

> `MFD-010: GO / CONDITIONAL GO / NO-GO`
