# Moodify Runtime 稳定性实验 6.1  
# AEP-NEM 压缩包说明

## 1. 这个压缩包是什么

这是 Moodify 支线计划中的第一个 Runtime 稳定性验证包。

它按照 AEP-NEM Engineering System 的格式组织：

- **E-Chain**：Runtime 稳定性支线工程链
- **NEM**：Runtime 稳定性验证节点
- **AEP**：8 个可执行工程原子包
- **Gate**：ADOPT / HOLD / REJECT 判断标准
- **Prompt**：可直接交给 Claude / Codex 的执行说明
- **Report Template**：实验完成后的统一报告模板

本压缩包的目的不是优化音质，也不是调整 MRS，而是验证：

> Moodify Runtime 是否具备稳定运行真实任务、自动记录日志、自动恢复异常、自动生成 summary 的能力。

---

## 2. 推荐使用方式

把整个压缩包交给 Claude / Codex 后，可以要求它：

```text
请阅读 README.md、NEM_Runtime_Stability_6_1.md 和 AEP 文件夹下的 8 个 AEP，
然后基于当前 Moodify 项目，按顺序执行 Runtime 稳定性实验 6.1。
```

建议执行顺序：

1. 先读 `NEM_Runtime_Stability_6_1.md`
2. 再读 `AEP_INDEX.md`
3. 按 AEP-6.1.01 到 AEP-6.1.08 顺序执行
4. 用 `GATES/gate_runtime_stability.md` 判断最终状态
5. 用 `REPORT_TEMPLATE/runtime_stability_6_1_report_template.md` 输出实验报告

---

## 3. 文件结构

```text
Moodify_Runtime_Stability_6_1_AEP_NEM/
├── README.md
├── MANIFEST.json
├── AEP_INDEX.md
├── NEM_Runtime_Stability_6_1.md
├── AEP/
│   ├── AEP_6_1_01_special_filename_smoke_test.md
│   ├── AEP_6_1_02_90_task_full_test.md
│   ├── AEP_6_1_03_6h_endurance_run.md
│   ├── AEP_6_1_04_24h_day_run.md
│   ├── AEP_6_1_05_failure_circuit_breaker.md
│   ├── AEP_6_1_06_task_recovery.md
│   ├── AEP_6_1_07_log_integrity.md
│   └── AEP_6_1_08_summary_auto_generation.md
├── GATES/
│   └── gate_runtime_stability.md
├── PROMPTS/
│   ├── claude_execution_prompt.md
│   └── codex_execution_prompt.md
├── REPORT_TEMPLATE/
│   └── runtime_stability_6_1_report_template.md
├── CONFIG_SUGGESTIONS/
│   └── runtime_stability_config_suggestion.json
└── CHECKLISTS/
    └── runtime_stability_operator_checklist.md
```

---

## 4. 当前节点定位

当前节点属于 Moodify 的支线实验系统。

它服务于主线目标：

> 第一个 Electron 桌面端软件交付物。

Runtime 稳定后，后续才能继续推进：

- MRS 跑分系统
- Preset 工艺库
- 样本资产库
- 报告与可解释性系统
- MVP 产品闭环
- 潮汐循环系统
- 桌面端集成

---

## 5. 最终输出

实验完成后，建议生成：

```text
reports/runtime_stability_6_1_report.md
```

最终结论必须是以下之一：

```text
ADOPT
HOLD
REJECT
```

其中：

- **ADOPT**：Runtime 可作为后续支线实验和桌面端集成地基。
- **HOLD**：Runtime 基本可用，但仍需补齐部分稳定性能力。
- **REJECT**：Runtime 不适合继续承载后续支线实验，必须先修复。
