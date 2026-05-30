# MHP-006 回传单：ChatGPT 调参判断

> 日期：2026-05-30
> 来源：ChatGPT
> 核心结论：方向对，动态过重。warm_vocal 必须调，wide_space/clean_master 建议调。

---

## 调参方案

### warm_vocal
P06 2.0→1.45, P07 15→25, P08 150→220, P09 -24→-16, P13 0.15→0.08, P15 2.0→1.5

### clean_master
P06 1.5→1.20, P07 25→35, P08 200→250, P09 -20→-12, P15 1.5→1.0

### wide_space
P06 1.5→1.25, P07 25→35, P08 300→320, P09 -26→-14, P11 0.35→0.28, P15 2.0→1.5

## 第一轮目标
warm_vocal crest≥3.0, clean_master crest≥3.5, wide_space crest≥3.0

## Limiter
暂不参数化。如果调参后 peak 仍全为 -0.0 dBFS，再开 MHP-006-C。
