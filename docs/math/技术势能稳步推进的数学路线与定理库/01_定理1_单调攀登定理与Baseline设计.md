# 定理 1：单调攀登定理与 Baseline 设计

**来源**: 技术势能稳步推进的数学路线与定理库 §3 定理1
**层级**: 内部工作定理 — 工程推进的元规则
**状态**: 待实验验证

---

## 0. 定理陈述

### 0.1 自然语言

一次工程推进只有在不降低已有稳定能力的前提下，增加了新的可验证能力，才算真正上升。

### 0.2 形式化

```
Step_t → Step_{t+1}

若:
  Baseline(Step_{t+1}) ≥ Baseline(Step_t)
且:
  NewCapability(Step_{t+1}) 被验证
则:
  Height(Step_{t+1}) > Height(Step_t)
```

### 0.3 逆命题

若新增功能导致旧基准退化，即使新功能正确，技术势能也可能下降。

---

## 1. 推理展开

### 1.1 为什么需要这个定理

软件工程的常态是「加功能 → 引入 bug → 修 bug → 加功能」。这形成了一个振荡而非单调上升。

Moodify 的特殊性在于：(a) 核心管线涉及不可逆的音频处理，(b) LLM 推理有随机性，(c) RAG 检索质量随时间变化。这三个因素叠加，意味着「退化」可能不被立即发现——用户听到的音频质量下降可能几天后才被注意到。

单调攀登定理强制一个约束：**任何变更必须通过旧基准测试，才允许合并。**

### 1.2 Baseline 的构成

Baseline 不是「跑一遍不出错」。它必须覆盖：

```
Baseline = {
  Correctness:  确定性组件的行为不变 (诊断/DSP/状态转移)
  Fallback:     LLM 不可用时的降级路径不退化
  Performance:  处理时间不劣化 (诊断 < 5s, DSP < 3s, 搜索 < 2s)
  Quality:      已知测试音频的 WHS/EDS 不下降
  Safety:       边界输入不产生异常输出
}
```

### 1.3 哪些能力算「稳定能力」

稳定能力的判断标准：**如果一个能力在连续 3 个版本中没有被修改、且通过了所有测试，它进入稳定集合。**

进入稳定集合后：
- 修改它需要额外的理由和 review
- 每次变更必须更新对应的 baseline 测试
- 它成为后续能力的「地基」

### 1.4 新功能导致老功能退化时的处理

退化分为三级：

| 级别 | 定义 | 处理 |
|------|------|------|
| 硬退化 | 确定性组件输出改变或 fallback 路径崩溃 | 拒绝合并 |
| 软退化 | WHS/EDS 在某些测试音频上下降但可解释 | 记录 + 标记 research-mode |
| 未验证 | 新功能没有覆盖某些旧测试用例 | 补充测试后再审 |

---

## 2. 数学细节

### 2.1 能力高度函数

```
Height(S) = Σ w_i * Capability_i(S)
```

其中 `Capability_i` 是二值或连续指标（如「RAG 可用」「诊断时间 < 5s」），`w_i` 是权重。

单调性要求：

```
∀i: Capability_i(S_{t+1}) ≥ Capability_i(S_t) - ε_i
Σ w_i * max(0, Capability_i(S_{t+1}) - Capability_i(S_t)) > 0
```

即：**不能有任何能力的显著退化（超过容忍度 ε），且至少有一项能力在提升。**

### 2.2 复杂度债务的测量

```
C(S) = LinesOfCode + CyclomaticComplexity + ExternalDependencies + UndocumentedAPIs
```

技术势能上升的条件（结合母文件的势能函数）：

```
P_{t+1} > P_t
⇔
(V_{t+1} * Rb_{t+1} * Re_{t+1} * D_{t+1} * E_{t+1} / C_{t+1}) >
(V_t * Rb_t * Re_t * D_t * E_t / C_t)
```

---

## 3. 工程含义

### 3.1 对 Moodify 的具体约束

```
RAG 不能破坏无 API key 的处理流程。
  → Baseline 必须包含 DEEPSEEK_API_KEY="" 的完整流程测试

LLM 不能破坏确定性 fallback。
  → Baseline 必须包含 LLM 返回 None 时的行为测试

搜索不能破坏工艺卡保底。
  → Baseline 必须包含搜索失败时回退到 get_recommended_params 的测试

新指标不能破坏人耳最终仲裁。
  → 任何新指标加入 ranking 前，必须先通过人耳校准实验
```

### 3.2 每次 PR 的检查清单

```
[ ] smoke_test.py 通过
[ ] pytest 全部通过
[ ] 3 首测试音频的 WHS_after >= WHS_before
[ ] DEEPSEEK_API_KEY="" 时 fallback 路径正常
[ ] 新增代码有对应的 fallback 处理
[ ] 处理时间无退化 (记录并对比上次的时间)
```

---

## 4. 留给后续 AI 的题目 (A1)

**题目 A1：设计 Moodify Baseline Suite。**

输入：当前代码库
输出：
1. 自动化测试脚本集合（CLI 测试 + API 测试 + 音频质量测试）
2. 3-5 首标准化测试音频（覆盖不同风格、不同 AI 生成器、不同缺陷模式）
3. 基准指标记录格式（JSON schema）
4. 退化检测规则（什么算「显著退化」）
5. CI 集成方案

---

## 5. 理论参考

1. Beck, K. (2003). *Test-Driven Development: By Example*. Addison-Wesley.
   — Baseline 测试的工程哲学基础。

2. Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall.
   — 在已有代码上安全变更的策略。

3. Lehman, M. M. (1980). "Programs, Life Cycles, and Laws of Software Evolution." *Proceedings of the IEEE*, 68(9), 1060-1076.
   — 软件演化的 Lehman 定律，特别是「持续增长」和「复杂度增加」两条。

4. 母文件 §1-§2：技术势能函数的定义。

---

*Moodify 定理库 · 定理 1 · v1.0*
