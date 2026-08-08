# AEP-6.1.01
# 特殊文件名 Smoke Test

## 1. AEP 元信息

```text
AEP ID: AEP-6.1.01
AEP Name: Special Filename Smoke Test
中文名称：特殊文件名 Smoke Test
所属 NEM：NEM-6.1-RUNTIME-STABILITY
所属工程链：Runtime Stability Side E-Chain
优先级：P0
状态：READY_TO_EXECUTE
```

---

## 2. 实验目的

验证 Moodify Runtime 在处理中文、空格、括号、特殊符号、长文件名时是否稳定，重点检查路径传参、CLI 参数解析、输出目录生成和日志记录。

---

## 3. 实验边界

本 AEP 只验证：

```text
文件名兼容性
路径传参稳定性
CLI 参数解析稳定性
输出目录生成
日志记录完整性
```

本 AEP 不处理：

```text
不优化音质
不调整 MRS 权重
不修改产品 UI
不引入新商业功能
```

---

## 4. 前置条件

```text
准备 5-10 个短音频样本
将样本复制并改名为不同特殊文件名
确认 ffmpeg / Python 依赖可用
确认 Runtime 基础命令可执行
```

---

## 5. 执行步骤

```text
1. 创建特殊文件名测试目录：data/test_inputs/special_filenames/
2. 准备文件名样例：
   - 中文歌曲.wav
   - test song with spaces.wav
   - song_(version_1).wav
   - song-特殊符号_#01.wav
   - very_long_filename_for_moodify_runtime_stability_test_001.wav
3. 对每个文件执行 Runtime process 命令。
4. 检查是否出现 unrecognized arguments。
5. 检查输出文件是否生成。
6. 检查日志是否记录每个文件。
7. 统计失败原因。
```

---

## 6. 需要采集的指标

```text
total_files
success_files
failed_files
success_rate
unrecognized_arguments_count
path_error_count
output_generated_count
log_record_count
```

---

## 7. 通过标准

```text
所有特殊文件名均可处理
unrecognized_arguments_count = 0
path_error_count = 0
每个文件都有输出和日志记录
```

---

## 8. 失败判定

```text
出现 unrecognized arguments
中文或空格文件名导致失败
输出路径错乱
日志缺失
```

---

## 9. 输出文件建议

```text
outputs/runtime_stability_6_1/special_filename_smoke_test/
logs/runtime_stability_6_1/special_filename_smoke_test.log
reports/runtime_stability_6_1_special_filename_smoke_test.md
```

---

## 10. Claude / Codex 执行指令

```text
请执行 AEP-6.1.01：特殊文件名 Smoke Test。

请基于当前 Moodify 项目完成实验设计、命令执行、日志检查、指标统计和结论判断。
最终输出一个 Markdown 小报告，包含：实验目的、执行命令、输出路径、关键指标、发现的问题、最终结论。
```
