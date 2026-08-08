# DSK-MFY-PIPELINE-016｜工具链安装与第一条端到端生产流水线

**日期：** 2026-08-01
**执行 Worker：** DeepSeek / Codex
**任务性质：** 安装开源工具链，接通 Moodify 第一条完整的端到端生产流水线

## 1. 目标

Moodify 已有 36 个模块（DSP、转录、Bridge 证据、CLI DAW、CLI v2、频谱证据），但三条链路没有接通：

1. **开源工具链**（SoX/matchering/Rubber Band）未安装、未接线
2. **端到端流水线**不存在——独立模块之间没有 orchestrator
3. **证据不聚合**——不同系统产生的证据互不可见

本任务一次性解决这三个问题。

## 2. 前置条件

- `E:\moodify\scripts\install_moodify_toolchain.ps1` 已就绪
- 现有 36 个模块只读，不修改
- 只用合成 WAV 夹具测试

## 3. Phase 0｜工具链安装（15 分钟）

```powershell
powershell -ExecutionPolicy Bypass -File E:\moodify\scripts\install_moodify_toolchain.ps1
```

验证：
- `sox --version` 成功
- `py -3.11 -c "import matchering"` 成功
- `rubberband --version` 成功或明确报告缺失

写入 `E:\moodify\outputs\deepseek_validation\DSK-MFY-PIPELINE-016\TOOLCHAIN_INSTALLED.txt`。

## 4. Phase 1｜Adapter 接线（45 分钟）

新增 `E:\moodify\moodify-core-package\src\moodify\cli_daw\adapters\`：

```
SoXAdapter        → sox subprocess
MatcheringAdapter → matchering Python API
RubberBandAdapter → rubberband subprocess
```

每个 adapter 实现：
- `probe()` → 检测工具是否存在、版本
- `capabilities()` → 声明支持的操作
- `execute(action, params)` → 执行并返回证据

不可用工具返回 `UNAVAILABLE`，不静默跳过。

## 5. Phase 2｜DecisionOrchestrator（45 分钟）

新增 `E:\moodify\moodify-core-package\src\moodify\app\orchestrator.py`：

```
分析输入 → 生成 TreatmentPlan → dry-run 预览 → 等待确认 → 执行 → 验证
```

- 读入 OnePointSpec（essence/protect/allow/avoid/owner）
- 基于现有分析能力（librosa 频谱 + pyloudnorm 响度 + librosa 特征）生成建议
- dry-run 输出 plan JSON，不执行音频处理
- 确认后调用 CLI DAW NativeDSPBackend 执行
- 写 project.json 和 run_manifest.json

## 6. Phase 3｜EvidenceAggregator（30 分钟）

新增 `E:\moodify\moodify-core-package\src\moodify\app\evidence.py`：

收集分散证据源：
- Bridge evidence（DuckDB + YAML）
- Spectral evidence（PNG + CSV）
- CLI DAW render evidence（render_evidence.json）
- Lyrics evidence（lyrics_evidence.json）

写入统一 `evidence_bundle.json`：
```json
{
  "run_id": "...",
  "sources": {"bridge": {...}, "spectral": {...}, "daw": {...}, "lyrics": {...}},
  "aggregated_hashes": {...},
  "limitations": [...]
}
```

## 7. Phase 4｜验证闭环（30 分钟）

合成夹具 + OnePointSpec + 完整路径：

```
py -3.11 -m moodify.cli_v2 project init TEST_DIR
→ asset import TEST_DIR synthetic.wav
→ plan create TEST_DIR --intent warm_vocal.json --dry-run
→ run execute TEST_DIR --output-dir NEW_DIR
→ verify
→ evidence
```

至少验证：3 个 adapter probe 正确、dry-run 不产生音频、execute 产生 render.wav + 证据、source hash 不变。

## 8. 边界

- 允许新增：cli_daw/adapters/、app/orchestrator.py、app/evidence.py、tests/
- 允许修改：cli.py（最小路由接线）
- 禁止：修改既有模块、处理真实歌曲、联网下载模型、Git 操作、覆盖用户文件

## 9. 交付

```
outputs/deepseek_validation/DSK-MFY-PIPELINE-016/
  TOOLCHAIN_INSTALLED.txt
  run_a/
  HANDOFF.md
```
