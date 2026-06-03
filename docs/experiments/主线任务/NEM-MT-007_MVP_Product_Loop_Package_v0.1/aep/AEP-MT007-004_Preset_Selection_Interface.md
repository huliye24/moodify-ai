# Preset 选择接口

所属节点：NEM-MT-007｜MVP 产品闭环  
节点阶段：产品成型  
状态：PENDING  

## 1. 目标

从工艺库读取可用 preset，并允许用户或系统选择默认 preset。

## 2. 输入

- NEM 主节点文件；
- 当前 Node Status；
- Runtime / MRS / Preset / Report 相关依赖；
- 当前 AEP 所需模板文件。

## 3. 输出

preset_selection.json / available_presets.md

## 4. 执行原则

- 只解决本 AEP 的问题；
- 不扩大 MVP 范围；
- 所有输出必须可追踪；
- 所有结果必须能被 AI 复盘；
- 如果涉及用户可见结果，必须保持解释清晰。

## 5. 验收标准

每个处理任务都能明确记录 preset_id 和 preset_version。

## 6. 失败处理

如果本 AEP 未通过，应生成 failure_report，并写入 decisions/Decision_Log.md。

## 7. PoEW 证明

本 AEP 的工程工作量证明不是代码行数，而是是否产生了可复用、可验证、可接入 MVP 闭环的工程结果。
