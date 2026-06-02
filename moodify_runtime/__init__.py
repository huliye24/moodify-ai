"""
Moodify Daily Run System  v2

外层 Runtime（加固版）：
- 不侵入 Moodify v01 / legacy 核心代码
- 负责每日样本登记、运行队列、云端夜跑、指标记录、报告、工艺记忆
- v2: 信号处理 / 进程组清理 / 磁盘检查 / 失败重试 / 输出保留策略 / 增量写摘要
"""

__version__ = "0.2.0"
