# Codex 验收矩阵｜DSK-MFY-PIPELINE-016

## P0

| ID | 验收项 | 失败处置 |
|---|---|---|
| P0-01 | SoX + matchering + Rubber Band 全部安装成功或诚实报告缺失 | REWORK |
| P0-02 | 每个 adapter produce() 返回真实状态，不伪造 | HOLD |
| P0-03 | 源音频只读且 hash 不变，输出只进新目录 | HOLD |
| P0-04 | dry-run 不产生音频派生物 | REWORK |
| P0-05 | 旧 CLI 和既有模块不回归 | REWORK |

## 功能

| ID | 验收项 |
|---|---|
| F-01 | SoXAdapter 可用（增益、格式转换、静音检测） |
| F-02 | MatcheringAdapter 可用（参考母带匹配） |
| F-03 | RubberBandAdapter 诚实（有则可用，无则 UNAVAILABLE） |
| F-04 | DecisionOrchestrator 生成 TreatmentPlan |
| F-05 | dry-run 输出 plan JSON，不执行 |
| F-06 | execute → render.wav + render_evidence.json |
| F-07 | EvidenceAggregator 统一 evidence_bundle.json |

## 验证

| ID | 验收项 |
|---|---|
| V-01 | 合成 WAV 夹具闭环：init → import → plan → dry-run → execute → verify |
| V-02 | 双运行确定性（同输入同参数同输出） |
| V-03 | 工具缺失时 adapter 返回 UNAVAILABLE |
| V-04 | source hash、output hash、evidence hash 一致 |
