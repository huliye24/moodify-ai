# AEP-MT003-003｜quick_mrs / full_mrs 双档模式

所属节点：NEM-MT-003｜MRS 性能优化与批量生产瓶颈突破  
类型：AEP｜Atomic Engineering Package｜工程原子包  
状态：PENDING  

---

## 1. 目标

将 MRS 分为快速排序版与完整评估版。

---

## 2. 输入

- 当前 Moodify Runtime 输出结果；
- 当前 MRS 评分脚本；
- 真实或准真实 AI 音乐样本；
- 运行日志与输出报告。

---

## 3. 检查项

- quick_mrs 指标集合
- full_mrs 指标集合
- 速度/准确性取舍
- 报告字段差异

---

## 4. 交付物

输出 quick/full 配置模板。

---

## 5. 验收标准

- 有明确 before 数据；
- 有可复现命令；
- 有结构化报告；
- 有失败记录；
- 结论可以反馈到 MT-003 节点状态。

---

## 6. 注意事项

不要在没有数据的情况下做结论。  
不要让 MRS 阻塞 Runtime 主流程。  
所有变化必须记录到 Decision Log。
