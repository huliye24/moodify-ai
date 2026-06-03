# MT-001 Runtime 云端运行系统｜NEM 节点压缩包

创建日期：2026-06-02  
项目：Moodify  
节点编号：NEM-MT-001  
节点名称：Runtime 云端运行系统  
节点定位：Moodify 云端稳定自动运行工程地基  
优先级：P0 / 最高优先级  
前置依赖：无  
状态：ACTIVE

---

## 这个压缩包是什么？

这不是一个单独的 Markdown 文件，而是一个完整的 **NEM 节点包**。

它用于定义、拆解、执行和验收 Moodify 的第一个主线工程节点：

> 让 Moodify 在云端稳定、自动、可追踪、可恢复、可长期运行。

---

## 压缩包目录结构

```text
MT-001_Runtime_NEM_Package/
├── README.md
├── manifest.json
├── 00_README/
├── 01_NEM_Node/
│   └── NEM-MT-001_Runtime_Cloud_System.md
├── 02_AEP_Atomic_Packages/
│   ├── AEP-MT001-001_Cloud_Directory_Structure.md
│   ├── AEP-MT001-002_Runtime_Config.md
│   ├── AEP-MT001-003_Input_Registry.md
│   ├── AEP-MT001-004_Run_Queue.md
│   ├── AEP-MT001-005_Unattended_Run.md
│   ├── AEP-MT001-006_Logging_System.md
│   ├── AEP-MT001-007_Final_Report.md
│   ├── AEP-MT001-008_Failed_Task_Retry.md
│   ├── AEP-MT001-009_MRS_Optional_Scoring.md
│   └── AEP-MT001-010_Long_Run_Test.md
├── 03_Evolution_Gates/
│   └── Evolution_Gates.md
├── 04_Runtime_Config_Templates/
│   ├── runtime_config.template.json
│   ├── input_registry.template.jsonl
│   └── run_queue.template.jsonl
├── 05_Runbook_Cloud_Commands/
│   ├── cloud_run_commands.md
│   └── day_run_24h_command.sh
├── 06_Report_Templates/
│   ├── day_run_summary.template.md
│   └── final_summary.template.txt
├── 07_PoEW_Evidence/
│   └── PoEW_Checklist.md
├── 08_Decision_Log/
│   └── decision_log.md
└── 09_Backlog/
    └── backlog.md
```

---

## 使用方式

1. 解压该压缩包；
2. 将整个目录放入 Moodify 项目文档目录，例如：

```bash
docs/nem/MT-001_Runtime_NEM_Package/
```

3. 先阅读：

```text
01_NEM_Node/NEM-MT-001_Runtime_Cloud_System.md
```

4. 再按顺序执行：

```text
02_AEP_Atomic_Packages/
```

5. 每完成一个 AEP，就在对应文件里更新：

```text
状态：
证据：
问题：
下一步：
```

6. 每完成一个阶段，就检查：

```text
03_Evolution_Gates/Evolution_Gates.md
```

---

## 核心原则

- NEM 是节点分子，不是一次性任务。
- AEP 是工程原子包，是最小做功单元。
- Gate 是进化闸门，决定节点是否可以升级。
- PoEW 是工程工作量证明，用结果证明节点真实推进。
- MT-001 是 Moodify 后续所有主线任务的工程地基。
