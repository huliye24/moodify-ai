# Moodify 听觉智能（Auditory Intelligence）

> DAWs 提供执行面。Moodify 提供听觉观察、判断、验证与学习。

Moodify 不是"AI 音乐后处理工具"的升级版——它是**听觉智能系统**。
音频处理不是最终目的，而是受控干预手段，用于产生观察、比较、判断与
学习就绪数据。

## 六大责任域

| 域 | 回答 | 位置 |
|---|---|---|
| 观察 Observation | 声音里发生了什么 | `moodify/auditory/`（metrics/decode/spectrogram/timeline/stereo） |
| 表示 Representation | 机器如何描述听到的内容 | `moodify/auditory/models.py`、`moodify/learning/models.py` |
| 判断 Judgment | 缺陷/风险/有意特征/未决歧义 | `moodify/auditory/judgment.py`、`comparison.py` |
| 干预 Intervention | 为检验或改善声音施加了什么受控变更 | `moodify/processing/`、`v01_*`、外部 Audacity |
| 验证 Verification | 改变了什么、是否达成目标且未造成新损伤 | `moodify/auditory/service.py`、`manifests.py` |
| 学习 Learning | 系统能从案例学到什么 | `moodify/learning/`（records/eligibility/exports） |

## 关键原则

- 处理能力保留，但定位为**听觉干预实验室**；
- Moodify 不做 DAW、不自动化 Audacity、不要求宏；
- 技术改进 ≠ 艺术批准；每个报告 `human_listening_required: true`；
- 案例未提交学习记录前不算"学习完成"；
- 训练资格默认 `UNKNOWN`/`PENDING_REVIEW`，绝不默认 `ELIGIBLE`；
- 源音频永不覆盖；所有产物可哈希可审计。

## 文档

- [概念](./concepts.md)
- [案例循环](./case_loop.md)
- [干预实验室](./intervention_lab.md)
- [学习记录](./learning_records.md)
- [数据集资格](./dataset_eligibility.md)
- [迁移地图](./migration_map.md)
- [能力清点](./current_capability_inventory.md)
