# AEP-MT003-008｜资源监控与成本评估

所属节点：NEM-MT-003｜MRS 性能优化与批量生产瓶颈突破  
类型：AEP｜Atomic Engineering Package｜工程原子包  
状态：PENDING  

---

## 1. 目标

记录 MRS 运行时 CPU、内存、磁盘和成本指标。

---

## 2. 输入

- 当前 Moodify Runtime 输出结果；
- 当前 MRS 评分脚本；
- 真实或准真实 AI 音乐样本；
- 运行日志与输出报告。

---

## 3. 检查项

- CPU 峰值
- 内存峰值
- 磁盘读写
- 缓存占用
- 单首成本估计

---

## 4. 交付物

输出 resource_monitor.csv 与 cost_note.md。

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
