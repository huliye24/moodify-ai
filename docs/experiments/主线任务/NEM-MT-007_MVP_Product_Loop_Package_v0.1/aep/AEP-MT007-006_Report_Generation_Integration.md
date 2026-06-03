# 报告生成接入

所属节点：NEM-MT-007｜MVP 产品闭环  
节点阶段：产品成型  
状态：PENDING  

## 1. 目标

调用 MT-006 报告系统生成用户报告与技术报告。

## 2. 输入

- NEM 主节点文件；
- 当前 Node Status；
- Runtime / MRS / Preset / Report 相关依赖；
- 当前 AEP 所需模板文件。

## 3. 输出

user_report.pdf / technical_report.md

## 4. 执行原则

- 只解决本 AEP 的问题；
- 不扩大 MVP 范围；
- 所有输出必须可追踪；
- 所有结果必须能被 AI 复盘；
- 如果涉及用户可见结果，必须保持解释清晰。

## 5. 验收标准

报告能解释处理前后差异，并关联 MRS 与 preset。

## 6. 失败处理

如果本 AEP 未通过，应生成 failure_report，并写入 decisions/Decision_Log.md。

## 7. PoEW 证明

本 AEP 的工程工作量证明不是代码行数，而是是否产生了可复用、可验证、可接入 MVP 闭环的工程结果。
