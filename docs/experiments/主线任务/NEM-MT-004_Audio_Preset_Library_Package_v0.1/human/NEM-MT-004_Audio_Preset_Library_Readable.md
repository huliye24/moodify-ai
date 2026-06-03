# NEM-MT-004｜音频处理工艺库

**节点类型**：NEM｜Node Evolution Molecule｜节点进化分子  
**所属工程链**：Moodify 主线工程链  
**节点主题**：MRS 性能可用之后，建立可复用声音处理 preset 工艺库  
**计划周期**：2026.7 - 2026.8  
**前置依赖**：Runtime 可稳定运行；MRS 初步可用；MRS 性能瓶颈进入可控状态  
**节点目标**：把一次性的音频处理实验沉淀为可复用、可评分、可版本化、可迭代的声音处理工艺库。

---

## 1. 一句话定义

**MT-004 是 Moodify 从“能处理音频”走向“拥有技术护城河”的节点。**

MT-001 让系统能在云端稳定运行；MT-002 让 MRS 成为 AI 音乐真实度跑分单位；MT-003 让 MRS 可以批量生产化运行；MT-004 则开始把通过 Runtime 和 MRS 验证过的有效处理方法，沉淀成可复用的声音处理 preset 工艺库。

也就是说，MT-004 的本质不是“多写几个预设”，而是建立一套：

```text
实验参数 -> MRS 评分 -> 效果复盘 -> preset 封装 -> 版本管理 -> 工艺库沉淀
```

的工程闭环。

---

## 2. 为什么 MT-004 重要

Moodify 的护城河不只来自代码，而来自长期实验沉淀下来的工艺资产。

AI 音乐后处理的核心难点在于：

1. 不同 AI 音乐问题不同；
2. 同一个 preset 不能盲目套用所有音频；
3. 声音质量提升需要可复盘的参数链；
4. 有效参数必须被保存、命名、分类、评分和版本化；
5. 只有经过反复验证的 preset，才可以成为产品能力。

因此，MT-004 是 Moodify 技术纵深的开始。

如果没有工艺库，Moodify 只是一个能跑脚本的工具。  
如果有了工艺库，Moodify 就开始变成一个会积累经验的声音工程系统。

---

## 3. 节点核心产物

MT-004 的核心产物不是单个音频结果，而是以下资产：

| 产物 | 作用 |
|---|---|
| Preset Taxonomy | 定义声音处理 preset 的分类体系 |
| Preset Spec | 定义每个 preset 的标准描述格式 |
| Preset Registry | 记录所有 preset 的索引、版本、状态和适用场景 |
| Processing Chain | 记录 EQ、动态、空间、瞬态、质感等处理链 |
| MRS Evaluation Record | 记录 preset 使用前后的跑分变化 |
| A/B Test Report | 用于人工听感 sanity check，不作为唯一标准 |
| Quality Gate | 判断 preset 能否从实验进入候选、稳定、采纳 |
| Versioning Rule | 避免 preset 参数混乱、无法复现 |

---

## 4. Preset 的成熟度等级

MT-004 中的 preset 不应一开始就称为“正式工艺”。它需要经过成熟度分层。

| 等级 | 名称 | 含义 |
|---|---|---|
| L0 | IDEA | 只是一个处理想法，未实验 |
| L1 | EXPERIMENTAL | 已经实现，样本较少，效果不稳定 |
| L2 | CANDIDATE | 在多个样本中有效，具备候选价值 |
| L3 | STABLE | 效果稳定，可进入批量处理 |
| L4 | ADOPTED | 被采纳为 Moodify 正式工艺资产 |
| L5 | DEPRECATED | 已被替代或不再推荐使用 |

这一分层可以防止 Moodify 把偶然有效的参数误认为长期有效的工艺。

---

## 5. Preset 分类体系

MT-004 初期可以建立以下分类：

```text
01_spectral_balance        频谱平衡类
02_transient_repair        瞬态修复类
03_dynamic_recovery        动态恢复类
04_vocal_texture           人声质感类
05_spatial_reality         空间真实度类
06_plastic_reduction       塑料感降低类
07_mastering_polish        母带抛光类
08_genre_specific          风格/类型适配类
09_emotion_specific        情绪表达类
10_reality_enhancement     真实度增强类
```

这套分类不是最终答案，而是 Moodify 工艺库的第一版骨架。

---

## 6. 与 MRS 的关系

MT-004 必须依赖 MRS，但不能被 MRS 单独绑架。

建议判断规则：

```text
MRS 提供主量化指标；
波形、频谱、动态、空间指标提供辅助解释；
人工听感只做 sanity check；
最终采纳需要跨样本稳定性。
```

一个 preset 不能因为某一次 MRS 上升就被采纳。它必须证明：

1. 在多个样本上有效；
2. 不靠响度作弊提高分数；
3. 不破坏高质量原始音频；
4. 对目标问题有明确改善；
5. 参数链可复现；
6. 能进入 Runtime 批量执行。

---

## 7. 节点执行路线

MT-004 建议分为 6 个 Gate 推进：

| Gate | 名称 | 目标 |
|---|---|---|
| Gate 0 | 节点建档 | 建立节点说明、目录、规则和模板 |
| Gate 1 | Preset 体系建立 | 完成分类、命名、规格和注册表 |
| Gate 2 | 初始实验 preset | 建立第一批实验 preset |
| Gate 3 | MRS 关联评估 | 每个 preset 都能记录前后 MRS 变化 |
| Gate 4 | Runtime 接入 | preset 可被 Runtime 调用并批量执行 |
| Gate 5 | 工艺库采纳 | 形成第一批 ADOPTED 工艺资产 |

---

## 8. 初期应优先沉淀的 preset 类型

建议从 AI 音乐最常见的问题开始，而不是一开始追求复杂风格。

优先级如下：

1. 降低刺耳高频；
2. 增加中频质感；
3. 修复瞬态发软；
4. 改善空间贴片感；
5. 降低塑料感；
6. 避免响度作弊；
7. 提升动态呼吸感；
8. 保护高质量输入不被过度处理。

这比先做“赛博朋克 preset”“伤感 preset”更重要，因为基础声音问题才是工艺库的地基。

---

## 9. 节点完成标准

MT-004 完成，不是因为写了很多 preset，而是因为 Moodify 具备了可持续积累工艺的能力。

最低完成标准：

```text
1. 已建立 preset 分类体系；
2. 已建立 preset 标准格式；
3. 已建立 preset registry；
4. 至少 5 个 experimental preset；
5. 至少 3 个 candidate preset；
6. 至少 1 个 stable preset；
7. 每个 preset 都有 MRS 前后对比记录；
8. 每个 preset 都可以被 Runtime 调用；
9. 每个 preset 都有版本号和适用范围；
10. 形成第一版工艺库报告。
```

理想完成标准：

```text
形成 10 - 20 个可复用 preset，
其中 3 - 5 个达到 stable，
1 - 3 个达到 adopted，
并成为 Moodify 后续产品化功能的基础。
```

---

## 10. 节点结论

MT-004 是 Moodify 技术护城河开始显形的节点。

它把一次性的处理结果转化为可复用的工艺资产；  
把零散实验转化为 preset library；  
把声音经验转化为工程系统；  
把 AI 音乐后处理从“临时调参”推进到“长期工艺积累”。

从这个节点开始，Moodify 不再只是运行代码和计算 MRS，而是开始积累自己的声音工程经验。
