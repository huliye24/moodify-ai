# MFD-010 — Alpha Entropy Reduction & Fix Prioritization
## Codex 正式执行任务书

**任务编号：** MFD-010  
**执行对象：** Codex  
**执行模式：** Evidence Synthesis / Deduplication / Root Cause / Prioritization  
**前置条件：** MFD-009 = GO

---

# 0. 总目标

不要马上修 Bug。

不要开始实现 Feature Request。

本包只做：

> **把 Alpha 证据变成工程决策。**

---

# 1. 输入

必须读取 MFD-009 的真实输出，包括：

```text
top_10_defects
top_10_feature_requests
top_ux_confusions
top_playback_failures
listening_summary
device_failure_patterns
second_session_signal
privacy_findings
unknowns
Alpha Batch Reports
support bundle summaries
telemetry summaries
```

如果某类证据不存在：

标记：

```text
NO_EVIDENCE
```

不要猜。

---

# 2. Evidence Normalization

把不同来源统一成一个结构：

```text
EvidenceItem {
  id
  source
  category
  version
  environment
  frequency
  severity
  reproducibility
  user_impact
  core_flow_impact
  evidence_strength
  notes
}
```

---

# 3. Deduplication

典型情况：

```text
“播放偶尔失败”
“点 Play 没声音”
“切歌后卡住”
“歌加载不出来”
```

可能其实来自同一个根因：

```text
PlaybackManifest expiry / race
```

必须合并。

不要把同一个根因拆成 15 个 Issue，让 backlog 看起来很大。

---

# 4. Root Cause Grouping

按根因优先，而不是按表面现象。

建议分类：

```text
AUTH
PLAYER_API
MANIFEST
MEDIA_DELIVERY
PLAYBACK_ENGINE
LOCAL_STATE
RACE_CONDITION
WINDOWS_INTEGRATION
INSTALLER
UPDATE
DEVICE_COMPATIBILITY
UX_COMPREHENSION
LISTENING_RESULT
UNKNOWN
```

每个 root cause group 要列：

- symptoms；
- evidence；
- affected testers；
- affected versions；
- suspected root cause；
- confidence；
- missing evidence。

---

# 5. Evidence Strength

使用统一等级：

```text
E0 — anecdote only
E1 — single reproducible case
E2 — multiple independent cases
E3 — telemetry + reproduction
E4 — strong repeated evidence across devices/users
```

Feature Request 也需要 evidence strength。

---

# 6. Core Flow Impact

使用：

```text
C0 — irrelevant to core Play
C1 — cosmetic
C2 — friction
C3 — damages repeat use
C4 — blocks Play
C5 — security/data authority risk
```

修复优先级不能只看“用户抱怨大声不大声”。

---

# 7. Product Fit

每个 feature request 必须判断：

```text
CORE
SUPPORTING
DISTRACTING
CONTRADICTS_PRODUCT
UNKNOWN
```

例如：

### Play / reliability
大概率 CORE。

### 歌词
可能 SUPPORTING 或 DEFER。

### 复杂 EQ
当前很可能 CONTRADICTS_PRODUCT，因为 Moodify 的核心是替用户隐藏复杂参数。

### 皮肤
可能符合长期审美经济，但不一定属于当前 Alpha 工程主线。

---

# 8. Complexity Cost

给每项工作估算：

```text
S — very small
M — medium
L — large
XL — architecture-level
```

不要求精确工时。

目的：

> 防止一个小问题诱发大系统。

---

# 9. Entropy Cost

新增功能还要评估：

```text
LOW
MEDIUM
HIGH
VERY_HIGH
```

Entropy Cost 表示它会增加多少：

- UI surface
- state
- API
- persistence
- testing
- user choices
- documentation
- support burden

---

# 10. Decision States

每一项只能进入：

```text
FIX_NOW
FIX_NEXT
OBSERVE
EXPERIMENT
DEFER
REJECT
NEEDS_MORE_EVIDENCE
```

不要留下模糊状态：

```text
maybe
later?
consider
```

---

# 11. FIX_NOW 标准

只能进入 FIX_NOW，如果满足：

- P0 / P1；
- 或 C4/C5；
- 或高频 C3；
- 或直接阻碍核心 Alpha 验证；
- 有足够证据。

FIX_NOW 数量应尽量少。

---

# 12. FIX_NEXT

适用于：

- 已确认问题；
- 不阻塞 Alpha；
- 对重复使用有明显影响；
- 修复成本合理；
- 不引入大复杂度。

---

# 13. OBSERVE

适用于：

- 只有少量报告；
- 无法复现；
- 影响轻；
- 可能是设备/网络偶发。

要求定义：

> 下一轮需要什么证据才升级。

---

# 14. EXPERIMENT

适用于：

- 听感问题；
- 设备差异；
- 新播放策略；
- 不确定是否值得产品化的机制。

Experiment 不等于 feature implementation。

---

# 15. DEFER

适用于：

- 有价值；
- 但不属于当前阶段；
- 例如长期皮肤系统、macOS、Linux、iOS 等。

必须写：

```text
why defer
what future trigger
```

---

# 16. REJECT

需要真正允许拒绝需求。

例如：

- 会破坏 Play 极简；
- 让用户承担专业音频参数；
- 与当前产品原则冲突；
- 无证据；
- 成本远高于价值。

REJECT 不是永久禁止。

它表示：

> 当前证据下不进入工程。

---

# 17. Listening Evidence Analysis

把 MFD-009 的听感证据独立处理。

至少分析：

```text
Moodify preference rate
Reference preference rate
No-preference rate
track category differences
device differences
tester differences
```

不要只看总体平均。

可能出现：

```text
old recording → strong positive
modern mastered pop → no difference
Bluetooth → weak difference
USB DAC → stronger difference
```

这类 pattern 比一个总百分比更重要。

---

# 18. Listening Decision

每个听感 pattern 进入：

```text
VALIDATED_DIRECTION
PROMISING
INCONCLUSIVE
NEGATIVE
```

只有：

```text
VALIDATED_DIRECTION
PROMISING
```

才值得进入后续处理研究。

---

# 19. Second-session Analysis

判断用户不再打开可能来自：

```text
product has no value
install friction
content too small
playback bug
unclear UI
tester forgot
Alpha cohort artificial
```

不能简单把：

> second session 低

直接解释成：

> 产品失败。

需要根因。

---

# 20. UX Confusion Analysis

对于每个困惑：

问：

> 是 UI 真有问题，还是用户在寻找一个我们故意不提供的传统播放器功能？

这两者完全不同。

例如：

```text
“EQ 在哪里？”
```

可能不是 UI bug。

而是：

> Moodify 产品模型与传统播放器预期冲突。

这种情况可能需要品牌/文案，而不是加 EQ。

---

# 21. Feature Request Compression

把 feature requests 压缩成主题：

```text
Library
Discovery
Control
Personalization
Offline
Audio Control
Social
Visual
Platform
```

然后每个主题给：

```text
request_count
product_fit
core_impact
entropy_cost
decision
```

---

# 22. Device Failure Matrix

建立：

| Environment | Success | Failure | Dominant issue | Confidence |
|---|---:|---:|---|---|

重点找：

- Windows version；
- Bluetooth；
- USB DAC；
- laptop speaker；
- high-DPI；
- multiple monitor；
- network。

不要仅记录品牌型号。

---

# 23. Top Root Causes

最终必须形成：

```text
Top 3
Top 5
Top 10
```

但真正进入工程的建议最多优先处理：

> Top 3–5。

不要一次修 30 个问题。

---

# 24. Fix Package Design

如果存在需要立即修复的问题：

本包只负责设计：

```text
MFD-FIX-001
MFD-FIX-002
...
```

每个 Fix 包应该：

- 单根因；
- 小范围；
- 有复现；
- 有验收；
- 有 rollback。

不要在 MFD-010 直接实现。

---

# 25. Phase 2 Feature Gate

只有 feature request 满足以下条件之一，才允许进入 Phase 2 候选：

### A
直接强化：

> Play / better listening.

### B
显著提高第二次使用。

### C
解决高频核心 friction。

### D
建立长期战略能力且复杂度可控。

否则：

> 不进入 Phase 2。

---

# 26. Phase 2 不是默认发生

MFD-010 最终可以给出：

```text
NO_PHASE_2_YET
```

如果证据显示：

> 现在最重要的是修稳定性和增加听感样本，而不是扩功能。

这是合法且可能最优的结论。

---

# 27. Final Priority Model

建议优先级公式只作为辅助：

```text
Priority ≈
(Core Impact × Evidence Strength × Frequency × Product Fit)
/
(Complexity + Entropy Cost)
```

不要机械算分。

最终需要工程判断。

---

# 28. 必须删除的东西

MFD-010 还需要主动找：

- duplicate backlog；
- stale issues；
- obsolete feature ideas；
- old product assumptions；
- dev-only workaround；
- debug flags；
- Alpha-specific temporary code。

但：

> 只生成 cleanup candidates。

不要在本包大规模删除。

---

# 29. Decision Report

最终必须形成：

```text
WHAT TO FIX
WHAT TO STUDY
WHAT TO WATCH
WHAT TO DEFER
WHAT TO REJECT
WHAT TO REMOVE
```

这是 MFD-010 的核心产物。

---

# 30. 禁止项

严禁：

- 直接修大量问题；
- 直接实现 feature request；
- 用票数决定 roadmap；
- 只听最活跃 tester；
- 忽略负面听感；
- 把每个问题都变成 P1；
- 为了 Phase 2 而强行创造 Phase 2；
- 用估计替代证据；
- 合并不相关根因；
- 删除历史证据。

---

# 31. Definition of Done

必须完成：

1. Evidence normalized；
2. Issues deduplicated；
3. Root cause groups；
4. Evidence strength；
5. Core impact；
6. Product fit；
7. Complexity；
8. Entropy cost；
9. Decision state；
10. Listening pattern analysis；
11. Second-session analysis；
12. UX confusion analysis；
13. Feature request themes；
14. Device failure matrix；
15. Top 3/5/10 root causes；
16. FIX_NOW list；
17. FIX_NEXT list；
18. OBSERVE / EXPERIMENT list；
19. DEFER list；
20. REJECT list；
21. cleanup candidates；
22. MFD-FIX package proposals if needed；
23. Phase 2 recommendation；
24. Final Decision Report。

---

# 32. 最终回报

Codex 最终只报告：

1. evidence volume
2. deduplication result
3. top root causes
4. FIX_NOW
5. FIX_NEXT
6. experiments
7. listening patterns
8. feature requests accepted/deferred/rejected
9. device patterns
10. cleanup candidates
11. proposed MFD-FIX packages
12. Phase 2 recommendation
13. remaining unknowns

最后明确：

> `NEXT: FIX / MORE_ALPHA / PHASE_2_DEFINITION / HOLD`
