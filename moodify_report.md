# Moodify 项目运行报告

**时间**: 2026-06-02  
**项目路径**: `/home/ubuntu/moodify-o3is`  
**运行模式**: 24 小时定时循环 (`day_run_001`)

---

## 1. 进程状态

- **PID**: 240099 (已用 `kill -9` 手动终止)
- **启动时间**: 2026-06-02 15:47
- **运行时长**: ~1h 26min 后终止
- **CPU**: 96% (接近满载)
- **内存**: ~2.3 GB

## 2. 数据概况

| 项目 | 数值 |
|------|------|
| 输入音频文件 | 30 首 (`.mp3`, `.flac`, `.wav`) |
| 任务队列 | 90 个 (30 文件 × 3 preset) |
| 输出总大小 | `outputs/daily_runs/` 359M, 175 个文件 |
| 当前 run (20260602_154710) | 295M, 仅 **6 个 .wav** 输出 |

三个 preset: `warm_vocal`, `clean_master`, `wide_space`

## 3. 严重 Bug: 文件名转义导致 93% 失败率

| 指标 | 数量 |
|------|------|
| 总任务尝试次数 | 87 |
| 成功 (exit code 0) | **6** |
| 失败 (exit code 2) | **81** |

### 根因

命令行构造时未正确转义含空格/括号的文件名。runtime 的 `command_templates` 使用字符串拼接方式生成命令：

```
python3 -m moodify.cli process {input} --preset {preset} --output-dir {output_dir}
```

当 `{input}` 是 `_Black Therapy (1).mp3` 时，拼接后变成：

```
python3 -m moodify.cli process /path/to/_Black Therapy (1).mp3 --preset warm_vocal ...
```

argparse 把空格后的 `Therapy`、`(1).mp3` 当作独立参数，报错：

```
cli.py: error: unrecognized arguments: Therapy (1).mp3
```

所有包含空格或括号的音频文件全部失败（如 `Control Theory.mp3`、`Moonlight Girl.mp3`、`句点15 (1).mp3` 等），只有不含特殊字符的文件名能成功（如 `假装无所谓2.mp3`）。

### 受影响文件列表

- `_Black Therapy (1).mp3`
- `_Black Therapy (2).mp3`
- `_Black Therapy.mp3`
- `Control Theory.mp3`
- `Moonlight Girl.mp3`
- `_Neural Poison  .mp3`
- `_Neural Poison   - 副本.mp3`
- `Okay Okay 刚刚好.mp3`
- `Silk and Ruin2.mp3`
- `句点15 (1).mp3`
- `句点8 (1).mp3`
- `我想被偏爱，不想被路过 (1).mp3`
- `我曾遥望银河星光 (1).mp3`
- `散焦之界 (1).mp3`
- `茧中微光 (1).mp3`
- ...以及其他含空格/括号的文件

## 4. 次要问题

- **中文字体缺失**: `v01_analyzer.py` 使用 DejaVu Sans 渲染频谱图，缺少 CJK 字形，中文歌名的图表显示为方块（不影响音频处理本身）
- **重试策略浪费资源**: 每个失败任务默认重试 2 次（共 3 次尝试），但该 bug 是确定性的（无论重试多少次都会失败），导致大量 CPU 空转

## 5. 修复建议

在 runtime 构造命令时对文件路径做 shell 转义。Python 中可以用 `shlex.quote()` 包装 `{input}` 和 `{output_dir}`：

```python
import shlex

cmd = template.format(
    input=shlex.quote(input_path),
    preset=preset,
    output_dir=shlex.quote(output_dir),
)
```

或者更彻底的做法：放弃字符串模板拼接，改用 `subprocess.run([...])` 传 list 参数，完全避免 shell 注入/拆分问题。

## 6. 当前状态

- 进程已终止
- 日志: `logs/day_run_001_20260602_154710.log`
- 输出: `outputs/daily_runs/20260602_154710/`
- 当前 run 产生的 6 个成功音频保留了，其余数据不受影响
