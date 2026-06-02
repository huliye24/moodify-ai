# Moodify Night Worker

夜间自动计算系统 — 让腾讯云服务器在没有 AI 持续参与、没有人工确认的情况下整晚自动运行 Moodify 重计算任务。

## 快速开始

```bash
# 1. 激活虚拟环境
source .venv/bin/activate

# 2. 干跑检查配置（不实际执行）
python workers/night_worker.py --dry-run

# 3. 启动夜间任务
bash scripts/run_night.sh

# 4. 监控进度
bash scripts/monitor_night.sh          # 快照
bash scripts/monitor_night.sh --watch  # 持续刷新
bash scripts/monitor_night.sh --tail   # 跟踪日志

# 5. 安全停止
bash scripts/stop_night.sh             # 优雅停止
bash scripts/stop_night.sh --force     # 强制停止

# 6. 第二天早上查看结果
ls runs/night_auto/reports/
cat runs/night_auto/reports/night_summary.md
```

## 架构

```text
workers/
├── night_worker.py      ← 主引擎 (Stage 1-6 流水线)
├── job_queue.py         ← 任务队列 (跳过/重试/失败)
├── checkpoint.py        ← 断点续跑 (原子写入)
├── resource_guard.py    ← 资源保护 (CPU/内存/磁盘)
├── report_builder.py    ← 报告生成 (CSV/JSON/Markdown)
└── README.md            ← 本文档

configs/
├── night_jobs.yaml      ← 主任务配置
├── preset_grid.yaml     ← 参数扫描网格 (4类)
└── server_limits.yaml   ← 服务器资源限制

scripts/
├── run_night.sh         ← 后台启动
├── monitor_night.sh     ← 监控
└── stop_night.sh        ← 停止
```

## 六阶段流水线

| 阶段 | 作用 | checkpoint |
|------|------|------------|
| **Stage 1** scan | 扫描/生成输入音频 | — |
| **Stage 2** analyze | 批量分析音频指标 | `analyzed_files.json` |
| **Stage 3** sweep | 参数扫描 + 生成处理版本 | `processed_versions.json` |
| **Stage 4** score | 评分 + 筛选最优 preset | — |
| **Stage 5** bench | 吞吐量基准测试 | — |
| **Stage 6** report | 生成所有报告 | — |

## 断点续跑

如果程序中断（关机/崩溃/手动停止），再次运行时自动：

- ✅ 跳过已分析的音频文件
- ✅ 跳过已处理的参数版本
- ✅ 跳过已失败的 job
- ✅ 从中断处继续

```bash
# 如需重新运行某阶段:
python workers/night_worker.py --reset analyze   # 重跑分析阶段
python workers/night_worker.py --reset sweep     # 重跑参数扫描
python workers/night_worker.py --reset all       # 从头开始
```

## 四类参数扫描

| 类别 | 描述 | 扫描参数 |
|------|------|---------|
| `warm_reality` | 温暖现实 | 人声存在感 + 低频温暖度 + 谐波 |
| `dynamic_recovery` | 动态恢复 | 压缩比 + 触发/释放 + 阈值 |
| `soft_space` | 柔光空间 | 混响深度 + 宽度 + 高频 |
| `anti_fatigue` | 抗疲劳 | 高频衰减 + 瞬态柔和度 |

## 输出文件

```text
runs/night_auto/
├── checkpoints/                          ← 断点续跑状态
│   ├── analyzed_files.json
│   ├── processed_versions.json
│   ├── failed_jobs.json
│   └── stage_status.json
├── output/
│   ├── processed_audio/                  ← 处理后的音频文件
│   ├── metrics/
│   │   ├── audio_metrics.csv             ← 音频指标表
│   │   └── parameter_sweep_results.csv   ← 参数扫描结果
│   ├── figures/                          ← 频谱图
│   └── samples/
├── reports/
│   ├── night_summary.md                  ← 主汇总报告
│   ├── best_presets.md                   ← 最佳 preset 详情
│   ├── error_report.md                   ← 错误报告
│   └── throughput_report.md              ← 吞吐量报告
├── configs/
│   └── best_presets.json                 ← 最优配置 JSON
└── logs/
    ├── night_worker.log                  ← 主日志
    └── night_worker.jsonl                ← 结构化日志
```

## 安全保护

| 保护 | 机制 |
|------|------|
| CPU过载 | 超过80%拒绝新worker, 超过70%降级 |
| 内存不足 | 超过6GB拒绝, 超过4.5GB降级 |
| 磁盘不足 | 低于10GB停止生成, 低于500MB紧急停止 |
| 运行时间 | 上限12小时自动停止 |
| 版本数量 | 上限2000个版本自动停止 |
| 失败跳过 | 每个job只试一次, 失败后记录跳过 |

## CLI 参数

```bash
python workers/night_worker.py \
    --config configs/night_jobs.yaml \   # 配置文件路径
    --dry-run \                           # 仅检查, 不执行
    --reset [analyze|sweep|all] \         # 重置 checkpoint
    --verbose                             # 详细日志
```

## 依赖

Night Worker 复用现有 Moodify Core Package 的所有依赖:
- `numpy`, `scipy`, `librosa`, `soundfile`, `pedalboard`
- 额外的依赖 (已在 pyproject.toml 中): `pyyaml`, `matplotlib`

## 设计原则

1. **不破坏现有代码** — 所有文件在 `workers/` `configs/` `scripts/` 下, 不修改任何现有源文件
2. **幂等运行** — 相同输入多次运行得到相同结果
3. **优雅降级** — 资源不足时降级而非崩溃
4. **透明可见** — 所有状态可查询, 所有结果可审查
5. **零人工干预** — 全自动完成, 早上直接看结果
