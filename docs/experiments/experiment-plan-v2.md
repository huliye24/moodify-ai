# Moodify 大规模实验方案 v2

**版本**: 2.1
**制定**: 2026-05-30
**前提**: 现有实验代码不变；云端 24/7 不关机运行
**特别优化**: 充分利用 32GB RAM（当前仅用 ~6GB，闲置 26GB）

---

## 一、运行模式

```
传统思路：白天快跑 + 夜间批跑
                   ↓
正确思路：加密货币式连续挖矿
         ─────────────────────────────────────
         CPU 永远在跑
         RAM 永远被占用
         实验按优先级排队，无空档期
         ─────────────────────────────────────
```

---

## 二、32GB RAM 专项（最大优化空间）

| 资源 | 当前 | 剩余 | 说明 |
|------|------|------|------|
| 内存 | ~6 GiB | **24 GiB** | 闲置量巨大，是首要优化方向 |

**32GB 才能做或做得更好的事：**

| 场景 | 16GB 限制 | 32GB 优势 |
|------|----------|----------|
| 诊断预热 | 无 | 全部音频预热驻留，查询 <1ms |
| LHS 采样 | N=10000 | N=100000（10x 精度） |
| B 矩阵 | 逐情绪串行 | 8 情绪全放内存并行 |
| 音频缓存 | 逐个加载 | 批量进内存，流水处理 |
| FFT 缓存 | 无 | 全曲频谱驻留，实时交互 |
| 遗传算法 | 100 个体 | 2000 个体，搜索空间大 20x |
| 离线校准 | 100 条 | 10000 条全量贝叶斯优化 |

**新增三个脚本：**

```
scripts/cloud/
├── audio_cache_warmer.py       ← 诊断预热（全部驻留内存）
├── memory_bmatrix_solver.py    ← 全量 LHS 搜索（100k 样本驻留）
└── batch_audio_processor.py    ← 批量音频流水线
```

---

## 三、优先级队列

```
P0 — 核心（永远在跑，8 核独占 + 全内存驻留）
  A1  B矩阵高精度    8情绪×100000样本    8核  20GB  6h  — 完成后循环
  C1  诊断预热       全部音频驻留内存      后台   8GB   常驻

P1 — 验证（与 P0 并行，4 核）
  A2  Monte Carlo  1000次 Bootstrap   4核  4GB   2h
  A3  Sobol 灵敏度 15参数全扫描      4核  4GB   3h

P2 — 补充（P0/P1 完成后自动接力，4 核）
  B1  k=5 交叉验证
  B2  诊断噪声底 500次
  B3  160 组合全流程
  B4  WHS-偏好对齐（需DB>100反馈）

P3 — 自动化调优（数据库积累后触发，2 核）
  A4  在线校准 B 矩阵更新
  A5  自适应 LHS 样本量调整
```

---

## 四、连续流水线设计

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        连续运转循环（永不停止）                           │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │  P0-A1       │  │  P0-C1       │  │  P1 队列      │               │
│  │  8核 20GB    │  │  后台 8GB    │  │  4核         │               │
│  │  B矩阵100k   │  │  诊断预热     │  │  A2 + A3     │               │
│  │  每6h循环    │  │  常驻内存    │  │  并行        │               │
│  └──────────────┘  └──────────────┘  └──────┬───────┘               │
│                                              │                         │
│  ┌──────────────────────────────────────────▼───────────────────────┐  │
│  │  P2 队列（4核）: B1→B2→B3→B4→B1→... 循环                      │  │
│  │  P3 队列（2核）: A4→A5（数据库积累后触发）                     │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  CPU 16核全占  |  RAM ~26GiB / 30GiB  |  零空档期                      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 五、执行脚本

### 5.1 连续调度器（主进程）

```bash
# 启动连续调度（后台运行，重启自动恢复）
nohup python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py \
    --mode continuous > /home/ubuntu/moodify/logs/scheduler.log 2>&1 &

# 查看调度状态
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_monitor.py
```

### 5.2 实验流程控制

```bash
# 暂停所有实验（维护用）
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py --pause

# 恢复实验
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py --resume

# 跳过当前实验，跳到下一个
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py --skip

# 强制停止所有实验
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py --stop
```

---

## 六、24h 实验日志模板

```
═════════════════════════════════════════════════════
  时间         事件              耗时    备注
═════════════════════════════════════════════════════
  00:00  A1 B矩阵100k循环第1次  6h00   开始，RAM=20GB
  00:00  C1 诊断预热启动         常驻   8GB驻留
  06:00  A1 完成，刷新B矩阵     —      κ(B)=3.8
  06:00  A2 MC启动              2h00   开始
  08:00  A2 完成               —       B_std 已更新
  08:00  A3 Sobol启动           3h00   开始
  11:00  A3 完成               —       最重要的3参数
  11:00  B1 交叉验证           30m     开始
  11:30  B1 完成               —       gap=8.2%
  11:30  B2 噪声底500次       15m     开始
  11:45  B2 完成               —       RSD=0.003%
  11:45  B3 160组合            20m     开始
  12:05  B3 完成               —       覆盖20音频×8情绪
  12:05  B1 交叉验证(第2次)   30m     开始（循环）
  ...    持续循环...
═════════════════════════════════════════════════════
  日均实验吞吐量: 约 8-10 个完整实验循环
  RAM 平均占用: ~26 GiB / 30 GiB (87%)
```

---

## 七、资源分配（24h 全满载）

| 进程 | CPU 核 | 内存 | 实验 |
|------|--------|------|------|
| P0-A1 B矩阵全量搜索 | 8核 | 20 GiB | 100k LHS 样本全驻内存 |
| P0-C1 诊断预热 | 后台 | 8 GiB | 全部音频诊断结果驻留 |
| P1 MC + Sobol | 4核 | 8 GiB | 并行 |
| P2 交叉/噪声/覆盖 | 2核 | 4 GiB | 循环 |
| 系统预留 | 2核 | 2 GiB | OS + API |
| **合计** | **16核** | **~26 GiB** | RAM 利用率 87% |

> 32GB RAM 的价值：原来 6GB → 现在 26GB，每 1GB 新增内存都转化为实验吞吐量。

---

## 八、32GB 专项操作流程

### 8.1 开机后第一步：启动诊断预热

```bash
# 启动诊断预热（后台常驻，新文件自动追加）
nohup python /home/ubuntu/moodify/scripts/cloud/audio_cache_warmer.py \
    --watch --dir /home/ubuntu/moodify/inputs > /home/ubuntu/moodify/logs/warmer.log 2>&1 &

# 查看预热状态
python /home/ubuntu/moodify/scripts/cloud/audio_cache_warmer.py --status
```

### 8.2 启动全量 B 矩阵求解

```bash
# 100000 样本高精度模式（内存约 20GB）
nohup python /home/ubuntu/moodify/scripts/cloud/memory_bmatrix_solver.py \
    --n-samples 100000 --workers 8 > /home/ubuntu/moodify/logs/bmatrix_hq.log 2>&1 &

# 快速验证（10000 样本）
python /home/ubuntu/moodify/scripts/cloud/memory_bmatrix_solver.py \
    --n-samples 10000 --dry-run
```

### 8.3 批量音频处理

```bash
# 批量处理音频目录
python /home/ubuntu/moodify/scripts/cloud/batch_audio_processor.py \
    --dir /home/ubuntu/moodify/inputs --emotion GA --workers 8

# 仅扫描报告
python /home/ubuntu/moodify/scripts/cloud/batch_audio_processor.py \
    --scan-only --dir /home/ubuntu/moodify/inputs
```

---

## 九、关机前 / 开机后流程

### 关机前（每次必须执行）

```bash
# 1. 暂停调度器
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py --pause

# 2. 等待当前实验自然结束（最多 10 分钟）
sleep 600

# 3. 同步数据到本地（包含预热缓存、checkpoint）
bash /home/ubuntu/moodify/scripts/cloud/moodify-sync-local.sh

# 4. 关机
sudo shutdown -h now
```

### 开机后（恢复运行）

```bash
# 1. 检查实验状态
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_monitor.py

# 2. 查看上次中断原因
tail -50 /home/ubuntu/moodify/logs/scheduler.log

# 3. 恢复预热（自动从 checkpoint 加载）
python /home/ubuntu/moodify/scripts/cloud/audio_cache_warmer.py --warm

# 4. 恢复 B 矩阵求解（断点续跑）
python /home/ubuntu/moodify/scripts/cloud/memory_bmatrix_solver.py --resume

# 5. 恢复调度器
python /home/ubuntu/moodify/scripts/cloud/moodify_exp_scheduler.py --resume
```

---

## 十、注意事项

- **按量计费**: 关机不收费，但 24/7 跑会产生费用。根据预算决定
- **32GB 利用率**: 目标是 RAM 占用 ~26GB/30GB（87%），CPU 99%，无空档期
- **断点保护**: 每 1000 样本写一次 checkpoint，重启后自动续跑
- **不要手动杀进程**: 用调度器的 `--pause`/`--resume`，防止数据丢失
