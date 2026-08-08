# DSK-MFY-SPECTRAL-EVIDENCE-012｜Codex 独立验收矩阵

| ID | 优先级 | 验收项 | 失败判定 |
|---|---|---|---|
| S0-01 | P0 | 合同先于编码，算法与参数版本冻结 | HOLD |
| S0-02 | P0 | 明确频谱/指标不能单独证明改善 | HOLD |
| S1-01 | P0 | before/after 参数、时间轴和色标一致 | HOLD |
| S1-02 | P0 | difference 恒为 after - before，图例明确 | HOLD |
| S1-03 | P0 | 无静默裁切、重采样、归一化或填零 | HOLD |
| S1-04 | P0 | 每个产物可追溯到输入哈希、版本和参数 | HOLD |
| S1-05 | P1 | 整曲及现有 stems 均按合同生成三类图 | REWORK |
| S2-01 | P0 | JSON/CSV 是事实层，XLSX 与其行数和数值一致 | HOLD |
| S2-02 | P0 | Human Review 未被自动填写或推断 | HOLD |
| S2-03 | P1 | Excel 可打开，链接、单位、null 原因有效 | REWORK |
| S2-04 | P1 | 可用时生成 Parquet；不可用时诚实说明 | REWORK |
| S3-01 | P0 | 源音频、历史记录和既有输出哈希未变化 | HOLD |
| S3-02 | P0 | 不产生自动优劣判断、训练或生产接入声明 | HOLD |
| S3-03 | P1 | 双构建、失败注入、CLI 和测试结果完整 | REWORK |
| S3-04 | P1 | HANDOFF 可从命令复现并列出全部限制 | REWORK |

Codex 将独立抽查数值与 Excel 一致性、差值方向、参数一致性、路径逃逸、损坏 WAV、时间轴错位、缺失 stem、重复 ID、NaN/Inf、人工标签伪造、源哈希变化和生产目录写入尝试。

