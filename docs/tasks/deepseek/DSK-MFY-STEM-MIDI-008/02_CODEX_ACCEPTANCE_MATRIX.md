# DSK-MFY-STEM-MIDI-008｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| S0-01 | P0 | 编码前冻结输入/输出、错误和 raw/clean 合同 | HOLD |
| S0-02 | P0 | dirty worktree 与只读哈希被记录且保护 | HOLD |
| S0-03 | P1 | benchmark 区分合成 ground truth 与无标注 smoke | REWORK |
| S1-01 | P0 | 旧 `transcribe` 行为兼容 | HOLD |
| S1-02 | P0 | 每轨来源、类型、模型、参数、状态和哈希可追溯 | HOLD |
| S1-03 | P0 | 单轨失败可见且不产生伪成功 | HOLD |
| S1-04 | P0 | 无路径逃逸、覆盖或源文件变化 | HOLD |
| S1-05 | P1 | profile 严格、模型复用、Unicode/空轨处理正确 | REWORK |
| S1-06 | P1 | `other/unknown` 未伪称确定乐器 | REWORK |
| S2-01 | P0 | raw MIDI 不变，所有清洗为派生输出 | HOLD |
| S2-02 | P0 | 量化/调性纠错默认关闭且可证明 | HOLD |
| S2-03 | P0 | 无显式 key/scale 不修改 pitch | HOLD |
| S2-04 | P0 | Type 1 多轨 MIDI 可解析、轨/channel 独立 | HOLD |
| S2-05 | P1 | 清洗确定、幂等并有 raw-vs-clean diff | REWORK |
| S2-06 | P1 | 弯音/滑音与跨小节 note 不被粗暴破坏 | REWORK |
| S3-01 | P0 | 没有把无标注歌曲 smoke 冒充准确率 | HOLD |
| S3-02 | P1 | 合成夹具报告 note/onset/octave 指标 | REWORK |
| S3-03 | P1 | 两次运行规范化结果一致 | REWORK |
| S3-04 | P1 | 8 GB 本机性能/内存限制被测量并记录 | REWORK |
| S3-05 | P1 | 新增测试、相关回归、CLI smoke、Ruff 通过 | REWORK |
| S3-06 | P1 | 文档与 HANDOFF 可由第二执行者复现 | REWORK |

Codex 将独立构造：重复 stem、缺失 stem、非法路径、已有输出、单轨后端失败、
空轨、弯音、跨小节 note、零强度量化、非法 key、多轨重新解析、双运行和
源文件哈希复核，并给出 `ACCEPT / REWORK / HOLD`。

