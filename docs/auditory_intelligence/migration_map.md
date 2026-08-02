# 迁移地图（DSK-MFY-AUDITORY-INTELLIGENCE-RECLASSIFICATION-001）

## 原则

- 先重分类，后搬迁；
- 不加兼容导入不做批量重命名；
- 只加可操作且经测试的弃用警告；
- 每个迁移模块保留或提升测试覆盖；
- 既有 case 生命周期保持权威。

## 分类结果（概要，完整见 current_capability_inventory.json）

| 权威分类 | 模块 | 处置 |
|---|---|---|
| OBSERVATION | v01_analyzer, features, perception | 原位保留并文档化 |
| REPRESENTATION | domain, data_types | 原位保留 |
| JUDGMENT | diagnosis, evaluation, uncertainty, reality_metrics, mrs_adapter, v01_diagnostics | 原位保留 |
| INTERVENTION | processing, v01_pipeline/presets/exporter/types, craft_slider, calibration, optimizer, physics, conservation, transcription, score_engine, orchestration, adapters, services | 原位保留，文档定位为干预实验室 |
| VERIFICATION | auditory.service/manifests/reports/errors, v01_delivery | 新增完成 |
| LEARNING | learning（新） | 新增完成 |
| SHARED | app, storage, ports, capability_registry, api, safety, protocol, config, cli*, audio_io, bands, fingerprint, auditory | 不动 |
| LEGACY_UNKNOWN | knowledge, memory, llm, icc, system_depth | 显式未分类，需人工复核（不猜） |

## 兼容性策略

- 所有既有公共接口保持不变（cli.py 路由、v01_*、app.production_control）；
- 新增域（auditory/learning）为纯增量，不修改既有模块行为；
- cli_v2 仅新增子命令，不改既有子命令语义；
- 无弃用警告（无模块被弃用）。

## 迁移风险与回滚

- 风险：分类漂移 → 由 inventory 工具 + 人工复核维持；
- 风险：学习资格误判 → 默认 UNKNOWN + 导出 fail-closed；
- 回滚：删除 auditory/learning 增量即可恢复旧框架；处理能力从未被移除。

## 遗留债务

- LEGACY_UNKNOWN 5 个模块（knowledge/memory/llm/icc/system_depth）需人工
  复核其真实职责后补充分类；
- 既有 CLI（cli.py 旧 argparse）与 cli_v2 双入口并存，属存量；
- cli_v2/main.py 的分号紧凑风格为存量，ruff E702 未清理（避免大 diff）。
