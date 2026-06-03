# NEM-MT-002｜MRS 跑分系统判断标准建立

这是 Moodify 的第二个主线节点容器，目标是建立 **MRS（Moodify Reality Score）作为 AI 音乐真实度量化单位** 的判断标准、验证路线和工程接入规范。

## 一句话目标

让 MRS 从一个实验性评分脚本，升级为 Moodify 可长期使用的“跑分单位”：数值越高，代表 AI 音乐越接近真实声音；不设满分，允许持续突破。

## 人类阅读顺序

1. `pdf/NEM-MT-002_MRS_Scoring_System_Readable.pdf`
2. `nem/NEM-MT-002_MRS_Scoring_System.md`
3. `gate/GATE-1_MRS_Unit_Definition.md`
4. `gate/GATE-2_Validation_Matrix.md`
5. `commands/run_mrs_validation_commands.md`

## 本节点为什么重要

MT-001 负责让 Runtime 在云端稳定产生数据；MT-002 负责回答这些数据如何被量化判断。

如果没有 MRS，Moodify 只能依靠主观听感和零散判断；如果 MRS 成立，Moodify 就能拥有自己的跑分单位、工程反馈系统、实验比较标准和长期技术进步曲线。

## 当前依赖

- 依赖 MT-001 Runtime 稳定产生数据。
- 当前建议从 MRS Open Benchmark v0.3.1 的 ADOPT 状态出发，但本节点不锁死某一个公式版本。
- 人类听感可作为 sanity check，但不能作为主要 ground truth；MRS 应主要由数学、物理、声学特征建立。

## 当前下一步

1. 固化 MRS 单位定义。
2. 明确 MRS 不设满分，基线中位数可设为 1000。
3. 建立验证矩阵。
4. 接入 Runtime 作为可选评分列。
5. 用 10-30 首真实 AI 音乐样本跑第一轮基准。
