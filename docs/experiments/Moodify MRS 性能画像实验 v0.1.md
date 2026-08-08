---
title: "Moodify MRS Performance Profiling Experiment"
subtitle: "MRS 性能画像实验计划与战略待办清单"
author: "文川院 / Moodify 工艺库"
date: "2026-06-02"
lang: zh-CN
geometry: margin=2.2cm
fontsize: 11pt
colorlinks: true
linkcolor: black
urlcolor: black
---

# 摘要

本文件定义 **Moodify MRS Performance Profiling Experiment**，用于系统分析 MRS（Moodify Reality Score）在云端批量音频处理中的性能瓶颈、耗时结构、可缓存性、并行化空间与产品化策略。

该实验不是立即修改 MRS 公式，也不是评估音质好坏，而是建立一套可复用的 **MRS 性能画像方法**：通过分阶段采集任务级、文件级、阶段级指标，判断 MRS 为什么会出现 1-6 分钟/文件的耗时波动，并进一步决定是否需要 `quick_mrs` / `full_mrs` 双档、特征缓存、并行评分、按需评分与夜间批处理等工程策略。

核心原则：

> **先测量，再优化；先画像，再改造；先分层，再产品化。**

---

# 1. 战略背景

Moodify Runtime v0.2 的文件名鲁棒性修复验证显示，系统已经从“任务无法进入处理流程”的执行层故障，进入“真实音频处理与 MRS 评分耗时较高”的性能层问题。

这意味着 Moodify 的瓶颈已经发生迁移：

| 阶段 | 主要问题 | 当前状态 |
|---|---|---|
| Runtime v0.1 | 文件名未转义，argparse 拆参失败 | 已暴露并修复 |
| Runtime v0.2 | 真实文件名能否稳定进入处理链路 | 正在 Full Test 验证 |
| MRS Profiling | MRS 评分为何耗时较长，如何降本增效 | 需要启动专题实验 |

MRS 是 Moodify 的核心评分系统，也是后续“AI 音乐真实度跑分”的基础单位。它的工程地位不只是一个附加指标，而是可能成为：

1. 处理前后对比的定量依据；
2. Preset 排名与推荐的基础信号；
3. Night Worker 自动筛选优秀版本的评分轴；
4. Moodify 工艺库长期积累的量化入口；
5. 未来 Benchmark、论文、产品报告和商业展示的核心指标。

因此，MRS 的性能不能只依赖“能跑就行”。必须明确：

- MRS 评分到底慢在哪里；
- 慢是否来自文件时长、WAV 中间文件大小、特征计算、I/O、CPU 或重复计算；
- 哪些特征可以缓存；
- 哪些部分可以并行；
- 哪些场景必须用完整 MRS；
- 哪些场景可以使用快速 MRS；
- 如何在工程效率与评分可信度之间建立分层策略。

---

# 2. 实验定位

## 2.1 实验名称

**Moodify MRS Performance Profiling Experiment**  
中文名：**Moodify MRS 性能画像实验**

## 2.2 实验目标

本实验要验证：

1. MRS 在不同音频文件上的耗时分布；
2. 文件大小、音频时长、采样率、声道数、WAV 中间文件大小与 MRS 耗时之间的关系；
3. MRS 各子阶段的耗时占比；
4. 是否存在重复计算，可否进行特征缓存；
5. 是否可以安全并行评分；
6. MRS 是否应作为可选评分列，而不是每次强制执行；
7. 是否需要设计 `quick_mrs` 与 `full_mrs` 两档评分系统。

## 2.3 本实验不验证

本实验不验证：

- MRS 公式本身是否最终正确；
- 某个 preset 的音质是否更好；
- AI 音乐是否真正接近真实音乐；
- 用户是否认可 MRS 分数；
- Moodify 的商业模式是否成立。

这些属于后续公式验证、听感验证、产品验证与商业验证。本实验只聚焦 **性能画像与工程策略**。

---

# 3. 核心研究问题

| 编号 | 研究问题 | 预期产出 |
|---|---|---|
| RQ1 | MRS 为什么会出现 1-6 分钟/文件的耗时波动？ | 耗时分布图与任务级 profile |
| RQ2 | 不同文件大小是否显著影响 MRS 耗时？ | 文件大小 - 耗时相关性 |
| RQ3 | WAV 中间文件大小是否是主要耗时变量？ | WAV size / duration / MRS time 关系 |
| RQ4 | MRS 中哪些特征可以缓存？ | Feature cache 候选清单 |
| RQ5 | MRS 是否可以并行评分？ | 并行度与吞吐量评估 |
| RQ6 | MRS 是否应设置为可选评分列？ | Runtime 配置建议 |
| RQ7 | 是否需要 `quick_mrs` / `full_mrs` 双档？ | 双档评分设计方案 |

---

# 4. 实验假设

| 编号 | 假设 | 验证方式 |
|---|---|---|
| H1 | MRS 耗时主要来自特征计算，而不是 CLI 音频处理本体 | 拆分 process_time 与 mrs_time |
| H2 | WAV 中间文件大小与 MRS 耗时显著正相关 | 计算 wav_size_mb 与 mrs_time 的相关性 |
| H3 | 音频时长比原始文件大小更能解释 MRS 耗时 | 对比 duration_sec、input_size_mb、wav_size_mb |
| H4 | 多个 preset 对同一输入音频会重复计算部分相同特征 | 检查输入级特征与输出级特征的复用可能 |
| H5 | 8 核服务器可并行运行多个 MRS 任务，但存在 I/O 与内存上限 | 测试 1/2/4/6 worker 吞吐量 |
| H6 | Runtime 应支持 `--scoring none/quick/full` 或配置项 | 对比不同评分模式的总耗时 |
| H7 | `quick_mrs` 可用于日常筛选，`full_mrs` 用于正式报告与 Benchmark | 比较速度、稳定性与分数一致性 |

---

# 5. 实验设计总览

本实验采用“推理闸门实验法”的结构，不直接进行大规模优化，而是先完成性能测量、阶段拆分和瓶颈判断。

```text
Gate 0: 实验定义
Gate 1: 代码与日志预检
Gate 2: 1-task 精细 Profile
Gate 3: 9-task 小样本 Profile
Gate 4: 30-task 分布 Profile
Gate 5: 并行与缓存可行性实验
Gate 6: quick_mrs / full_mrs 方案设计
Gate 7: Runtime 产品化决策
```

每一道门都必须输出明确报告。没有完成上一道门，不进入下一道门。

---

# 6. 指标体系

## 6.1 任务级指标

每个任务必须记录：

| 字段 | 含义 |
|---|---|
| task_id | 任务唯一 ID |
| input_path | 输入音频路径 |
| input_filename | 输入文件名 |
| preset | 使用的 preset |
| input_size_mb | 原始输入文件大小 |
| input_duration_sec | 输入音频时长 |
| input_sample_rate | 采样率 |
| input_channels | 声道数 |
| output_wav_path | 处理后的 WAV 路径 |
| output_wav_size_mb | 中间/输出 WAV 大小 |
| process_time_sec | CLI 处理耗时 |
| mrs_time_sec | MRS 评分耗时 |
| total_time_sec | 单任务总耗时 |
| exit_code | 进程退出码 |
| error_type | 错误类型 |
| mrs_score | 最终 MRS 分数 |
| mrs_mode | none / quick / full |

## 6.2 阶段级指标

MRS 内部应尽量拆分：

| 阶段 | 说明 |
|---|---|
| load_audio_time | 加载音频耗时 |
| resample_time | 重采样耗时 |
| spectral_feature_time | 频谱特征耗时 |
| dynamic_feature_time | 动态与瞬态特征耗时 |
| space_feature_time | 空间/声场特征耗时 |
| texture_feature_time | 质感特征耗时 |
| penalty_time | 惩罚项计算耗时 |
| aggregation_time | 最终聚合耗时 |
| report_write_time | 报告写入耗时 |

## 6.3 系统级指标

| 指标 | 用途 |
|---|---|
| CPU 占用 | 判断是否 CPU-bound |
| 内存峰值 | 判断是否 memory-bound |
| 磁盘读写 | 判断是否 I/O-bound |
| 并发任务数 | 判断并行上限 |
| 每小时任务吞吐量 | 估算 6h / 24h run 产能 |
| 成功率 | 判断系统稳定性 |
| 重试率 | 判断是否存在确定性失败 |

---

# 7. 分阶段实验方案

## 7.1 Gate 0 - 实验定义

目标：确认实验边界，不在 Full Test 运行期间修改正在运行的生产链路。

执行原则：

- 当前 Runtime Full Test 运行中时，不修改主代码；
- 本实验先写文档、脚本草案和指标规范；
- 等 Full Test 完成后，再启动 MRS Profiling；
- Profiling 使用独立输出目录，不污染正式 run。

产物：

```text
reports/mrs_performance_profiling/plan.md
```

通过标准：

- 实验目标、指标、阶段、停止条件明确；
- 不与当前 Full Test 冲突。

---

## 7.2 Gate 1 - 代码与日志预检

目标：找到 MRS 入口、耗时日志位置、summary 写入位置。

预检内容：

```bash
cd /home/ubuntu/moodify-o3is

grep -R "MRS\|mrs\|scoring\|Reality" -n moodify_runtime workers experiments configs | head -200
find . -name '*mrs*' -o -name '*score*' | head -100
```

需要回答：

1. MRS 当前由哪个文件调用？
2. MRS 当前是否每个任务强制执行？
3. MRS 是否已经有 v0.2 / v0.3.1 / open benchmark 多版本？
4. MRS 结果写入哪个 summary？
5. 是否已有计时日志？
6. 是否能在不改公式的前提下加入 timing wrapper？

产物：

```text
reports/mrs_performance_profiling/preflight.md
```

通过标准：

- 找到 MRS 调用链；
- 能安全加入 profiling 计时点；
- 不改变 MRS 分数计算逻辑。

---

## 7.3 Gate 2 - 1-task 精细 Profile

目标：用一个任务精确拆分耗时结构。

样本选择：

- 1 个中等长度音频；
- 1 个 preset；
- 使用 `full_mrs`。

记录：

```text
process_time_sec
mrs_time_sec
load_audio_time
feature_time
aggregation_time
report_write_time
output_wav_size_mb
```

通过标准：

- 生成完整 profile；
- MRS 阶段耗时可以被拆开；
- 不影响原始输出结果。

产物：

```text
reports/mrs_performance_profiling/gate2_one_task_profile.md
metrics/mrs_profile_one_task.csv
```

---

## 7.4 Gate 3 - 9-task 小样本 Profile

目标：观察不同文件名、不同 preset 下的 MRS 耗时波动。

建议配置：

```text
3 个音频 × 3 个 preset = 9 tasks
```

样本覆盖：

1. 小文件；
2. 中等文件；
3. 大文件或长音频。

通过标准：

- 9/9 完成；
- 每个任务都有 profile 行；
- 能初步估计 P50 / P80 / P95 MRS 耗时；
- 能判断是否存在极端慢任务。

产物：

```text
metrics/mrs_profile_9task.csv
reports/mrs_performance_profiling/gate3_9task_summary.md
```

---

## 7.5 Gate 4 - 30-task 分布 Profile

目标：建立 MRS 耗时分布，并分析文件变量与耗时关系。

规模：

```text
10 首音频 × 3 preset = 30 tasks
```

分析内容：

- mrs_time_sec 分布；
- input_size_mb 与 mrs_time_sec 相关性；
- output_wav_size_mb 与 mrs_time_sec 相关性；
- duration_sec 与 mrs_time_sec 相关性；
- preset 对耗时的影响；
- 是否有异常慢任务。

通过标准：

- 至少 30 条有效 profile；
- 找到主要耗时解释变量；
- 能给出 90-task 与 24h run 的吞吐量估算。

产物：

```text
metrics/mrs_profile_30task.csv
reports/mrs_performance_profiling/gate4_distribution_summary.md
```

---

## 7.6 Gate 5 - 缓存可行性实验

目标：判断 MRS 是否存在可复用特征。

核心问题：

同一首输入音频经过 3 个 preset 后，是否有部分特征可以共享？

可能分层：

| 特征层 | 是否可能缓存 | 说明 |
|---|---|---|
| 输入音频基础信息 | 高 | 时长、采样率、声道数、输入响度等 |
| 输入频谱特征 | 中 | 如果评分比较“处理前后差异”，输入侧可缓存 |
| 输出频谱特征 | 低/中 | 每个 preset 输出不同，需要分别计算 |
| 惩罚项 | 低 | 依赖输出结果 |
| 聚合分数 | 低 | 依赖完整特征 |

缓存实验：

```text
同一输入音频 × 3 preset
比较：无缓存耗时 vs 输入侧特征缓存耗时
```

通过标准：

- 缓存不改变最终分数；
- 至少节省 10%-20% 总 MRS 时间，才值得工程化；
- 缓存文件可追踪、可失效、可复现。

产物：

```text
reports/mrs_performance_profiling/cache_feasibility.md
```

---

## 7.7 Gate 6 - 并行评分实验

目标：测试 8 核服务器下 MRS 并行运行的安全并发数。

并行度：

```text
workers = 1, 2, 4, 6
```

指标：

| 指标 | 判断 |
|---|---|
| tasks/hour | 吞吐量是否提升 |
| CPU load | 是否接近合理上限 |
| memory peak | 是否超出安全范围 |
| failure rate | 并行是否引发失败 |
| disk I/O | 是否产生 I/O 瓶颈 |

通过标准：

- workers=2 或 4 时吞吐量明显提升；
- 无失败率上升；
- 内存与磁盘 I/O 可控；
- 能给出推荐并行度。

产物：

```text
reports/mrs_performance_profiling/parallel_scaling.md
```

---

## 7.8 Gate 7 - quick_mrs / full_mrs 双档设计

目标：判断是否需要双档评分。

建议定义：

| 模式 | 用途 | 特点 |
|---|---|---|
| none | 快速处理，不评分 | 用于纯音频导出 |
| quick_mrs | 日常筛选、队列排序 | 快速、近似、低成本 |
| full_mrs | 正式报告、Benchmark、论文实验 | 完整、稳定、可信 |

初步设计：

```text
quick_mrs:
- 使用较少特征
- 降低采样或帧密度
- 只计算关键频谱、动态、响度、基础惩罚
- 目标耗时：full_mrs 的 10%-30%

full_mrs:
- 保留完整六维真实度特征
- 用于正式报告和 Benchmark
- 目标：可信度优先，速度次之
```

通过标准：

- quick_mrs 与 full_mrs 排名相关性达到可接受水平；
- quick_mrs 能显著降低耗时；
- Runtime 配置清晰；
- 报告中明确标记评分模式，避免混淆。

产物：

```text
reports/mrs_performance_profiling/quick_full_mrs_design.md
```

---

# 8. 分析方法

## 8.1 耗时分解

将单任务耗时拆为：

```text
total_time = process_time + mrs_time + report_time + overhead
```

重点判断：

```text
mrs_ratio = mrs_time / total_time
```

如果 `mrs_ratio > 80%`，说明 MRS 是主瓶颈。

## 8.2 相关性分析

分析以下关系：

```text
input_size_mb      -> mrs_time_sec
output_wav_size_mb -> mrs_time_sec
duration_sec       -> mrs_time_sec
preset             -> mrs_time_sec
```

优先使用 Spearman 相关，因为音频文件大小与耗时关系可能非线性。

## 8.3 异常任务分析

定义异常慢任务：

```text
mrs_time_sec > P95
```

或：

```text
mrs_time_sec > median_mrs_time * 2.5
```

异常任务需要单独记录文件名、时长、WAV 大小、preset 与日志摘要。

---

# 9. 决策规则

## 9.1 是否优化 MRS

满足任一条件，进入 MRS 优化：

```text
1. MRS 占总任务耗时 > 80%
2. 90-task full test 中 MRS 总耗时 > 4 小时
3. 单任务 MRS P80 > 3 分钟
4. 24h run 预计吞吐量因 MRS 降低超过 50%
```

## 9.2 是否开发特征缓存

满足以下条件才开发：

```text
1. 可缓存特征占 MRS 耗时 ≥ 20%
2. 缓存不改变分数
3. 缓存失效规则清晰
4. 缓存文件不会造成管理混乱
```

## 9.3 是否并行评分

满足以下条件才并行：

```text
1. workers=2 或 4 时吞吐量提升明显
2. 内存峰值安全
3. 磁盘 I/O 未成为瓶颈
4. 失败率不升高
```

## 9.4 是否推出 quick_mrs

满足以下条件才进入实现：

```text
1. full_mrs 明显影响批处理效率
2. quick_mrs 可以达到 full_mrs 排名相关性 Spearman ≥ 0.75
3. quick_mrs 耗时 ≤ full_mrs 的 30%
4. 产品上存在快速筛选需求
```

---

# 10. 待办事项清单

## 10.1 P0 - 必须做

| 编号 | 待办 | 产物 |
|---|---|---|
| P0-1 | 等待 Runtime v0.2 Full Test 完成，不中途改代码 | full_test_summary.md |
| P0-2 | 定位 MRS 调用链与入口文件 | preflight.md |
| P0-3 | 增加 MRS timing wrapper，不改变公式 | profile instrumentation patch |
| P0-4 | 运行 1-task profile | one_task_profile.csv |
| P0-5 | 运行 9-task profile | mrs_profile_9task.csv |

## 10.2 P1 - 应该做

| 编号 | 待办 | 产物 |
|---|---|---|
| P1-1 | 运行 30-task 分布 profile | mrs_profile_30task.csv |
| P1-2 | 分析文件大小、WAV 大小、时长与耗时关系 | distribution_summary.md |
| P1-3 | 识别异常慢任务 | slow_task_report.md |
| P1-4 | 评估 feature cache 候选项 | cache_feasibility.md |
| P1-5 | 评估并行 worker=1/2/4 | parallel_scaling.md |

## 10.3 P2 - 战略布局

| 编号 | 待办 | 产物 |
|---|---|---|
| P2-1 | 设计 `--scoring none/quick/full` 配置 | runtime scoring spec |
| P2-2 | 设计 `quick_mrs` 指标子集 | quick_mrs_design.md |
| P2-3 | 验证 quick/full 排名一致性 | quick_full_correlation.md |
| P2-4 | 将 MRS profile 接入 Night Worker 报告 | night_worker_mrs_report_spec |
| P2-5 | 建立 MRS 性能基准版本号 | MRS Performance Benchmark v0.1 |

---

# 11. 推荐目录结构

```text
reports/mrs_performance_profiling/
  plan.md
  preflight.md
  gate2_one_task_profile.md
  gate3_9task_summary.md
  gate4_distribution_summary.md
  cache_feasibility.md
  parallel_scaling.md
  quick_full_mrs_design.md
  final_decision.md

metrics/
  mrs_profile_one_task.csv
  mrs_profile_9task.csv
  mrs_profile_30task.csv
  mrs_parallel_scaling.csv

outputs/mrs_profile_runs/
  one_task_YYYYMMDD_HHMMSS/
  nine_task_YYYYMMDD_HHMMSS/
  thirty_task_YYYYMMDD_HHMMSS/

logs/
  mrs_profile_one_task_YYYYMMDD_HHMMSS.log
  mrs_profile_9task_YYYYMMDD_HHMMSS.log
  mrs_profile_30task_YYYYMMDD_HHMMSS.log
```

---

# 12. 给 Claude 的执行约束

执行该实验时，Claude 必须遵守：

1. 不在 Runtime Full Test 正在运行时修改主代码；
2. 不启动 24h run；
3. 不删除旧数据，只允许移动或标记；
4. 不直接优化公式，先完成 profiling；
5. 所有长任务使用后台运行；
6. 所有实验必须输出日志、CSV、summary；
7. 每一阶段完成后再进入下一阶段；
8. 每次启动前必须给出预计耗时和下次检查时间；
9. 每次失败必须分类为 runtime、data、performance、dependency、design；
10. 所有结论必须进入工艺库报告。

---

# 13. 预期战略结果

完成本实验后，Moodify 将获得第一版 MRS 性能地图：

```text
MRS 耗时结构
MRS 主要瓶颈
MRS 与文件大小/时长/WAV 大小的关系
MRS 可缓存特征列表
MRS 推荐并行度
MRS 是否需要 quick/full 双档
Runtime 是否应默认关闭或启用 MRS
Night Worker 如何使用 MRS 排名
```

这会直接影响 Moodify 后续工程路线：

| 方向 | 决策价值 |
|---|---|
| 云端批处理 | 估算每日可处理歌曲数 |
| Night Worker | 判断是否夜间跑 full_mrs |
| 产品体验 | 判断用户是否等待评分 |
| 工艺库 | 建立评分数据与参数沉淀 |
| Benchmark | 形成可公开展示的性能指标 |
| 成本控制 | 降低 CPU 时间浪费 |

---

# 14. 结论

MRS 不只是 Moodify 的评分模块，而是 Moodify 将“声音真实度”变成可度量、可比较、可积累工艺资产的核心接口。

当前 Runtime v0.2 已经证明系统可以进入真实做功阶段。下一步的战略重点，不应是盲目扩大 24h run，而是建立 MRS 的性能画像：弄清楚它为什么慢、慢在哪里、哪些部分必须保留、哪些部分可以缓存、哪些场景需要完整评分、哪些场景只需要快速评分。

最终目标不是简单地“让 MRS 变快”，而是建立一套分层评分体系：

```text
none       -> 只处理音频，不评分
quick_mrs  -> 日常筛选、快速排序、低成本运行
full_mrs   -> 正式报告、Benchmark、论文实验、工艺库沉淀
```

这将使 Moodify 从“能处理音频”进一步升级为“能以工程化方式积累声音真实度数据”的系统。

---

# 15. 方法论句子

> **MRS 性能画像实验的目的，不是急着优化，而是先让系统看见自己的耗时结构。只有看见结构，才能决定缓存、并行、降级、分层和产品化。**

