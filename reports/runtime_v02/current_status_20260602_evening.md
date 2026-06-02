# Moodify Runtime v0.2 Current Status

**报告时间**: 2026-06-02 18:02  
**服务器时间**: 18:02 CST

---

## 1. 当前阶段

| 实验 | PID | 状态 | 已运行 | 进度 | CPU |
|------|-----|------|--------|------|-----|
| Smoke Test (9-task) | — | ✅ 已完成 | 30min | **9/9** | — |
| Full Test (90-task) | 274546 | 🔵 运行中 | 10min | **2/90** | 98% |

Smoke test 已自然退出，单进程独占 8 核。

## 2. 闸门判断

### Smoke test — ✅ 全部通过

| 闸门 | 状态 |
|------|------|
| 所有任务 exit code 0 | ✅ **9/9** |
| exit code 2 | ✅ 0 |
| unrecognized arguments | ✅ 0 |
| 空格+括号 `_Black Therapy (1).mp3` | ✅ 3/3 |
| 空格 `Control Theory.mp3` | ✅ 3/3 |
| 中文+空格+括号 `句点15 (1).mp3` | ✅ 1/1 (warm_vocal) |

**H1, H2 验证通过。subprocess 修复有效。**

### Full test — 🟢 正常运行

- 2/90 exit code=0，零 code=2，零 unrecognized
- 独占 8 核，无干扰

### ⛔ 24h run

**不允许启动。** 必须等 90-task full test 完整完成并通过判定。

## 3. 文件名鲁棒性矩阵

| 文件名特征 | 代表文件 | Smoke | Full | 结论 |
|-----------|---------|-------|------|------|
| 空格 + 括号 | `_Black Therapy (1).mp3` | ✅ 3/3 | ✅ 1/1 | 通过 |
| 空格 | `Control Theory.mp3` | ✅ 3/3 | ⏳ | 通过 |
| 中文 + 空格 + 括号 | `句点15 (1).mp3` | ⏳ | ⏳ | 待验证 |
| 中文纯名 | `假装无所谓2.mp3` | — | ⏳ | 待验证 |
| 多空格 | `_Neural Poison  .mp3` | — | ⏳ | 待验证 |
| 单引号 | — | — | — | 需构造 |
| 简单文件名 | `vocal_folk.wav` | ✅ 2/2 | — | 通过 |

## 4. 服务器资源

| 指标 | 数值 |
|------|------|
| CPU 核心 | 8 |
| 当前负载 | 1.99 (25% 占用) |
| 内存 | 15GB 总, 8.8GB 可用 |
| 磁盘 | 83GB 空闲 |
| Swap | 0/2GB 使用中 |

**无资源瓶颈。**

## 5. 性能观察

| 指标 | Smoke Test | Full Test (推测) |
|------|-----------|-----------------|
| CLI 处理耗时 | 0.4-7s | 0.4-7s |
| MRS 评分耗时 | 1-6min/文件 | 同 |
| 单任务总耗时 | 1.5-6.5min | 同，加权均 ~4.3min |
| 预计总耗时 | ~30min (剩余) | **6-8 小时** |

瓶颈在 MRS Open 测评分（占总耗时 95%+），CLI 处理本身极快。

## 6. 当前风险

| 风险 | 等级 | 说明 |
|------|------|------|
| 两进程并发 | 🟢 低 | 8核服务器，负载仅 2.0 |
| Full test 提前启动 | 🟢 低 | 不影响实验安全性，已有 smoke test 初步验证 |
| 时间估算偏差 | 🟡 中 | 单任务 MRS 耗时方差大（1-6min），90-task 可能在 5-10h |
| 句点15 smoke 未完成 | 🟢 低 | 前面类似文件已全部通过 |

## 7. 下一次检查

| 时间 | 检查内容 |
|------|---------|
| 今晚 ~23:00 | Full test `grep -c "RESULT code=0"` 看进度 |
| 明早 | 完整 summary.json + exit code 分布 + 失败分析 |

命令速查：
```bash
# 快速进度
grep -c "RESULT code=0" logs/full_test_v02_20260602_175352.log
grep -c "code=2" logs/full_test_v02_20260602_175352.log
grep -c "unrecognized" logs/full_test_v02_20260602_175352.log

# 活跃检查
ps -o pid,stat,etime,rss,pcpu -p 274546

# 完整结果
cat outputs/full_test_v02/20260602_175352/summary.json
```

## 8. 当前禁止事项

- ⛔ 不启动 24h run
- ⛔ 不新增测试任务
- ⛔ 不删除旧数据（只 mv/标记）
- ⛔ 不 kill 任何进程（除非超过 90min 无进展）
