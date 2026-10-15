# Moodify Production Learning

本目录保存从真实制作案例中提炼出的、可复用但尚未自动晋升为 Core 规则的生产经验。

权威边界：

- 正式流程以 [`STUDIO_PRODUCTION_PIPELINE_V4.md`](../canon/STUDIO_PRODUCTION_PIPELINE_V4.md) 为准；
- 案例记录是证据与操作经验，不是第二套流程、状态机、DSP 或 Judge；
- MATLAB 是实验与测量环境，不是生产运行时的第二权威；
- 案例参数在完成跨歌曲校准前均为 `UNCALIBRATED_ENGINEERING_DEFAULT`；
- 任何候选都必须保留 `A / B / ORIGINAL` 与人工审听出口。

## 从案例到复用规则

```text
真实案例
  → 保存输入条件、处理图、测量、失败与回退
  → 区分“本曲事实”与“跨歌曲假设”
  → 在下一首歌上复验
  → 多案例证据支持后，才提议进入 Core / Judge 规则
```

## 当前条目

- [2026-10-11：分轨重制与局部保守修复](cases/2026-10-11_STEM_RECONSTRUCTION_CONSERVATIVE_REPAIR.md)
- [下一首歌：分轨重制生产检查表](templates/STEM_RECONSTRUCTION_CHECKLIST.md)

