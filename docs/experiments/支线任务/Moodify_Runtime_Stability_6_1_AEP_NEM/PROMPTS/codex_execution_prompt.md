# Codex 执行 Prompt  
# Runtime 稳定性实验代码与脚本任务

请你作为 Moodify 项目的代码执行与脚本生成智能体，基于本压缩包完成 Runtime 稳定性实验 6.1 所需的脚本、配置和报告模板。

请优先完成以下内容：

## 1. 配置文件

创建或检查：

```text
configs/runtime_stability_6_1.json
```

配置内容应支持：

```text
input_dir
output_dir
log_dir
report_path
max_runtime_hours
presets
max_consecutive_failures
task_timeout_minutes
summary_enabled
resume_enabled
```

---

## 2. 特殊文件名测试脚本

如当前项目缺少该能力，请创建：

```text
scripts/runtime_stability_special_filename_test.py
```

脚本功能：

```text
复制样本文件
生成特殊文件名
调用 Runtime 命令
检查输出和日志
生成小报告
```

---

## 3. 日志完整性检查脚本

如当前项目缺少该能力，请创建：

```text
scripts/check_runtime_log_integrity.py
```

脚本功能：

```text
扫描日志
检查每个任务是否有 start/end/status/exit_code/duration/output_path
输出 log_integrity_rate
```

---

## 4. Summary 检查脚本

如当前项目缺少该能力，请创建：

```text
scripts/check_runtime_summary.py
```

脚本功能：

```text
检查 summary 是否存在
检查字段是否完整
对照日志验证统计值
输出 summary_valid = true/false
```

---

## 5. 恢复实验支持

如当前 Runtime 已支持 resume，请写测试脚本。

如不支持，请标注为 blocking issue，并提出最小修改方案。

---

## 6. 熔断实验支持

如当前 Runtime 已支持 max_consecutive_failures，请写测试脚本。

如不支持，请标注为 blocking issue，并提出最小修改方案。

---

## 7. 最终报告

最终请生成：

```text
reports/runtime_stability_6_1_report.md
```

必须包含最终 Gate：

```text
ADOPT / HOLD / REJECT
```

注意：

```text
不要修改 MRS 公式。
不要优化 preset。
不要做音质判断。
本任务只服务 Runtime 稳定性。
```
