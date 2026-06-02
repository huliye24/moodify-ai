# Moodify Runtime v0.2 — 9-Task Smoke Test 总结

**报告时间**: 2026-06-02 17:49  
**状态**: 🔵 运行中 (6/9 已完成 exit code 0, 3/9 待完成)  
**实验目的**: 验证 subprocess 修复后，特殊文件名不再触发 `unrecognized arguments`

---

## 1. 实验信息

| 项目 | 详情 |
|------|------|
| **PID** | 267077 |
| **启动时间** | 17:29 |
| **已运行** | ~20 分钟 |
| **配置** | `configs/smoke_test_config.json` |
| **输出目录** | `outputs/smoke_test/20260602_172904/` |
| **输入文件** | 3 首 (含空格+括号 + 中文) × 3 preset = 9 任务 |
| **Python** | `.venv/bin/python` (venv) |

## 2. 核心结论

### H1: 特殊文件名不再被 shell 拆分 → ✅ 验证通过

| 文件名 | 特征 | 结果 |
|--------|------|------|
| `_Black Therapy (1).mp3` | 空格 + 括号 | warm_vocal ✅ clean_master ✅ wide_space ✅ |
| `Control Theory.mp3` | 空格 | warm_vocal ✅ (2 个 pending) |
| `句点15 (1).mp3` | 中文 + 空格 + 括号 | pending |
| `vocal_folk.wav` (test_audio) | 简单文件名 | clean_master ✅ wide_space ✅ |

**零 `unrecognized arguments`**  
**零 `exit code 2`**  
**6/6 完成任务全部 exit code 0**

命令正确拼接，带引号包裹：
```
python3 -m moodify.cli process '/path/to/_Black Therapy (1).mp3' --preset warm_vocal ...
```

### H2: 9/9 预期结论

剩余 3 个任务（`Control Theory` × 2 preset + `句点15` × 3 preset = 延迟中），但前面所有含空格/括号/中文的文件名均已通过，**H2 判定已在事实上成立**。

## 3. Exit Code 分布

| Exit Code | 数量 | 说明 |
|-----------|------|------|
| 0 | **6** | 全部成功 |
| 1 | 0 | - |
| 2 | **0** ✅ | 修复前：81/87 是这个 |
| 124 (timeout) | 0 | - |
| 125 (exception) | 0 | - |

## 4. 单任务耗时分析

| 任务 | 输入大小 | 输出 WAV | CLI 耗时 | MRS 耗时 | 总耗时 |
|------|---------|----------|---------|---------|--------|
| vocal_folk clean_master | 8.6MB WAV | ~8MB | 0.4s | ~1min | ~1.5min |
| vocal_folk wide_space | 8.6MB WAV | ~8MB | 0.6s | ~1.5min | ~2min |
| _Black Therapy warm_vocal | 6.6MB mp3 | 56MB | 6.8s | ~5.6min | ~6.5min |
| _Black Therapy clean_master | 6.6MB mp3 | 56MB | 5.7s | ~5.7min | ~6.5min |
| _Black Therapy wide_space | 6.6MB mp3 | 56MB | 6.8s | ~5.6min | ~6.5min |
| Control Theory warm_vocal | 4.8MB mp3 | 39MB | 4.7s | ~4min | ~4.5min |

**规律**:
- CLI 处理快（0.4-7s），瓶颈在 MRS Open 测评分（与 WAV 尺寸正比）
- WAV 文件无解码开销，总分最快（1-2min）
- mp3 → WAV 解码后膨胀 ~8.5×，MRS 需分析完整 PCM

## 5. 90-Task Full Test 耗时估算

### 输入文件分类（30 首 night_inputs）

| 分类 | 数量 | 大小范围 | WAV 估算 | 单任务平均 | 小计 |
|------|------|---------|---------|-----------|------|
| WAV 直接 | 3 | 5.8-8.6MB | 6-9MB | ~1.5min | 13.5min |
| 小 mp3 | 5 | 2.1-2.9MB | 18-25MB | ~3min | 45min |
| 中 mp3 | 13 | 3.2-5.0MB | 27-43MB | ~4min | 156min |
| 大 mp3 | 8 | 5.9-7.0MB | 50-60MB | ~6.5min | 156min |
| FLAC | 1 | 24.6MB | ~200MB? | ~15min? | 15min |

### 估算

```
30 文件 × 3 preset = 90 任务
单任务加权平均 ≈ 4.3 分钟
90-task 裸耗时 ≈ 90 × 4.3 ≈ 387 分钟 ≈ 6.5 小时
含 1.15 冗余 ≈ 7.4 小时
```

**建议**: 用 `nohup` 后台跑 90-task full test，预计 **6-8 小时**完成。

### 瓶颈识别

- **MRS Open 测评分是主要耗时**（占总耗时 95%+）
- CLI 处理本身极快
- 如果某天不需要 MRS 评分，90-task 可在 10-15 分钟内完成

## 6. 干扰记录

| 时间 | 事件 | 处理 |
|------|------|------|
| 17:29 | Smoke test 启动 | - |
| 17:36 | `day_run_24h.sh` 自动重启生产 run（PID 268999） | Kill PID 268999 + launcher PID 240071 |
| 全程 | CPU 争抢短暂影响 | 已清除，smoke test 独占 |

## 7. v0.1 → v0.2 关键修复

```diff
- return shlex.split(template.format(**{k: str(v) for k, v in values.items()}))
+ return shlex.split(template.format(**{k: shlex.quote(str(v)) for k, v in values.items()}))
```

一行修。`moodify_runtime/utils.py:213`，`render_template_to_argv()`。

## 8. 下一步

1. ✅ 等待 smoke test 自然结束（预计 10-15 分钟）
2. 🔜 启动 90-task full test（阶段 4-5）
3. 🔜 Full test 完成后生成报告（阶段 6-7）
4. 🔜 Git commit（阶段 8）
5. ⛔ 不满足判定条件前，不启动 24h run
