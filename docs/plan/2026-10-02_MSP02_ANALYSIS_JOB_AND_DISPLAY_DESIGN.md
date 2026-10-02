# MSP 0.2 — 分析作业协议化与结果显示屏 设计提案

**日期：** 2026-10-02
**状态：** PROPOSAL — 待人类裁决（§8）
**Canon 依据：** v2.1 Sound Protocol（`b6673830`）+ v2.0 Professional Finishing（`a69c3e3c`）
**哲学依据：** 《软件建造的哲学》POSC_001 / 002 / 011 / 012（`E:\软件建造的哲学\RiverType_中文版`，中文初译版 0.1）
**前置事实来源：** 代码库勘察（2026-10-02，本会话）+ `docs/REPOSITORY_STATUS.md` + `docs/protocol/MOODIFY_SOUND_PROTOCOL_0_1.md`

---

## 1. 问题定义

用户意图（2026-10-02）：

> Moodify 做成一个 CLI 软件，可以被 AI 调用。核心是听觉智能：把音乐音频变成波谱，然后去做分析。**先忽略情感**，从理科的知识去检测音乐质量的好坏——这是最核心的功能。需要一个基础 UI 界面（一个显示屏），把分析结果绘制和显示出来，同时 AI 给出报告和后处理方案。

**先忽略情感** 是一条显式裁剪：本设计全部承诺都在**理科测量层**，音乐判断（表达/比例/意图）显式列为未承诺项（§4.2 judgment_boundary）。

## 2. 书的三个直接锚点

1. **POSC_001（软件作为建造的世界）**：「一个小小的命令行工具也可以是一个完整的世界，只要它的边界清晰、规则连贯。」CLI-first 不是降级形态，是被哲学支持的产品形态。该篇第 175 行直接给出音频系统的验收口径：「可靠的分析、可逆的变换、可复现的质量控制以及以人为中心的生产成为常态而非例外」。
2. **POSC_011（超越指标的判断）**：「Moodify 需要的是一个评估层级，而非单一分数。」测量揭示技术状况（L1）、受控比较揭示感知差异（L2）；报告不得把 L1/L2 包装成音乐判断（L3-L5）。每一项指标都要声明它的**可见范围与盲区**——「一项指标只在使之成为可能的那种盲目性的限度之内才是可信的」。
3. **POSC_012（无终局的完成）**：按「层」组织开发——每层有界承诺 + 与风险相称的证明 + 收束仪式。既不做永恒 beta，也不做完美主义。商业化不是一次宣布，而是完成层的积累：「护城河不是某一个秘密算法。它是真正被完成的关系的数量。」

## 3. 现状事实（不虚构）

### 3.1 已有且可用（勘察确认，2026-10-02）

| 能力 | 资产 | 状态 |
|---|---|---|
| AI 可调用分析 | `moodify analyze <audio>`（`release_cli.py` → `release.analyze_to_case()`）：stdout 恒 JSON，落 case bundle（case/measurements/evidence/judgment_rules/auditory_report + 频谱 PNG + timeline + STFT npz） | CANONICAL，就是「音频→波谱→理科检测→报告」的骨架 |
| 理科测量 | `auditory/metrics.py`（BS.1770 响度、真峰 4x 过采样、LRA、立体声/相位风险、频谱描述子、频段能量比），每个指标带 value/unit/method/status/warnings | CANONICAL |
| 技术判断 | `auditory/judgment.py`：版本化 `UNIVERSAL_THRESHOLDS`，PASS/RISK/UNKNOWN，「决定工作流，绝不批准艺术」——与「先忽略情感」完全一致 | CANONICAL |
| 波谱表示 | `auditory/representation/build.py` 四尺度（S0-S3）+ `spectrogram.py`（ffmpeg 线性/对数频谱图）+ `events/engine.py` 时间听觉 | CANONICAL / EXPERIMENTAL |
| Agent 协议 | MSP/0.1 `moodify protocol validate\|process`：声明式 JSON 作业，未知键拒绝，exit code 纪律 | CANONICAL（仅预设处理） |
| 处理链 | `moodify finishing new/render/verify/export`（Mix Graph v0.1，`a8a98804`，golden 确定性重放已证）+ `v01_pipeline` | EXPERIMENTAL（schema 未冻结）/ CANONICAL |
| 比较引擎 | `auditory/comparison.py`（deltas、delta 频谱图）+ `build_contact_sheet` + pairwise/ntrack（补丁包 09/10） | CANONICAL / EXPERIMENTAL |
| HTTP 面 | FastAPI `POST /api/v1/auditory/analyze` 等齐全 | CANONICAL |

### 3.2 对照用户意图的缺口

| # | 缺口 | 说明 |
|---|---|---|
| G1 | **「分析」不是协议一等作业** | AI 要分析只能走 ad-hoc `moodify analyze` 或在 process 作业里顺带拿诊断；MSP/0.1 作业类型只有 process。分析没有作业契约、没有 schema 冻结路径 |
| G2 | **没有显示屏** | 报告只有 JSON/MD/PNG，core 包无 HTML 报告生成器；`apps/ear-workbench`（静态 HTML 工作台）存在但未接 1.0 分析链 |
| G3 | **「后处理方案」不是一等输出** | 诊断→预设建议在链内存在（`v01_diagnostics`），Mix Graph 节点带 reason，但没有独立的、AI 可消费的 plan 文档把两者接起来 |
| G4 | **指标没有声明可见范围** | metrics 已带 method/status/warnings，但没有 POSC_011 要求的「这个指标看不见什么」字段 |
| G5 | 双 CLI 语义冲突 | `release_cli.analyze`（1.0 扫描）与 `cli.py analyze`（v0.1 频谱 PNG）同动词不同义；`setup.py` 与 `pyproject.toml` 对 `moodify` 入口点声明不一致 |
| G6 | ffmpeg 未声明为运行时依赖 | 1.0 扫描路径硬依赖 ffmpeg（解码+频谱图），文档与安装检查未显式化 |

## 4. 设计

### 4.1 协议层：MSP 0.1 → 0.2（一个协议，三种作业）

不建第二协议（Canon 不变量 8：One Core，禁止两套声音逻辑）。在 MSP 内增加作业类型：

```
moodify.sound/0.2
  job.type = "analyze"   新增：纯读取分析作业（本提案核心）
  job.type = "process"   0.1 兼容保持（预设处理）；v0.2 起可选携带 mix_graph 载荷（Mix Graph 提案 §5.1-2 既定方向）
  job.type = "compare"   新增：比较作业（Layer B，§6）
```

analyze 作业纪律：

- **纯读取**：不写音频文件，只写报告与证据；失败 fail-closed（协议已有纪律）。
- 与 `moodify analyze` ad-hoc 命令共用同一 Core 执行路径（`release.analyze_to_case`），CLI 命令保留为薄封装——与 Mix Graph「三层结构」裁决一致（AI 面 = 权威面，人/调试面 = 薄封装）。
- 0.1 作业在 0.2 下必须原样可用；协议版本字符串精确，不兼容即拒绝。

### 4.2 报告 schema（`report.json` 顶层结构）

```jsonc
{
  "protocol": "moodify.sound/0.2",
  "job": { "type": "analyze", "source": "audio/x.wav", "profile": "MFY-WSE-SCAN-PROFILE-001" },
  "source": { "path": "...", "sha256": "...", "duration_s": 0, "sample_rate": 0, "channels": 0 },
  "representation": {
    "scales": ["S0","S1","S2","S3"],          // 四尺度摘要（复用 representation/build）
    "spectrograms": ["scan/spectrum_linear.png", "scan/spectrum_log.png"]
  },
  "measurements": [
    {
      "id": "loudness_integrated", "value": -14.2, "unit": "LUFS",
      "method": "ITU-R BS.1770-5", "status": "PASS",
      "target_range": null,                      // 有标准依据时才填，不虚构
      "visibility": "能看到整体响度与门限后的稳态；看不到响度随段落的叙事分布是否恰当"
    }
  ],
  "findings": [
    { "id": "F-001", "severity": "RISK", "domain": "level",
      "description": "...", "measurement_ids": ["true_peak_db"],
      "evidence_refs": ["scan/analysis_data.npz#windows"],
      "repro": "moodify show <case_id>" }
  ],
  "plan": {
    "status": "DRAFT_PLAN_NOT_EXECUTED",        // 永不自动执行（Canon 不变量 9）
    "graph_draft": { "nodes": [ { "op": "eq", "params": {}, "reason": "...",
                                  "evidence_refs": ["F-001"], "reversible": true } ] },
    "next_actions": ["moodify protocol process <job.json>"]   // AI 可直接复制的下一步
  },
  "judgment_boundary": {
    "layer1_measurement": "EXECUTED",
    "layer2_comparison": "NOT_RUN",
    "layer3_musical_judgment": "NOT_PROMISED",
    "layer4_production_judgment": "NOT_PROMISED",
    "layer5_cultural_judgment": "NOT_PROMISED"
  },
  "provenance": { "core_version": "...", "profile": "...", "config_hashes": {}, "ts": "..." }
}
```

关键设计点（全部来自书）：

1. **不设单一总分**。POSC_011：「一个综合分数就是一部浓缩的宪法。它宣告哪些损失可以换取哪些收益。」要加分的时刻必须是人类显式裁决，且把权重宪法写进文档。`moodify-qa` 的 0-100 分是独立包的既有物，不并入本协议。
2. **`visibility` 字段是 POSC_011 的落地**：每个指标声明可见范围与盲区。实现上来自静态指标注册表（每指标一段固定文案），成本极低、哲学上承重。
3. **`plan.status` 永远是 DRAFT**：报告给「后处理方案」，但方案不等于执行。AI 拿 plan 生成 process 作业，人/AI 在 process 结果上再走 verify——「Generated is not finished」。
4. **`judgment_boundary` 写进 schema**：不承诺的层显式写 NOT_PROMISED，防止下游把 L1/L2 报告当音乐判断消费。这是对「距离商业化还有好远」的诚实表达方式：能力边界成为数据，而不是文案。

### 4.3 显示屏（基础 UI）

定位：**报告渲染器，不是产品 UI**（产品 UI 线已 parked，`7fdb1ee2`）。Canon 下它是生产端报告面，与 App（PLAY 消费端）无关。

- **形态（推荐 A）**：自包含单文件 `report.html`——内联 CSS/JS、无 CDN、无服务器（本地优先约束，MOODIFY_INTENT §8 精神延续）。`moodify protocol analyze` 默认产出报告三件套：`report.json`（AI）+ `report.md`（人读 diff 友好）+ `report.html`（显示屏）。
- **内容**：频谱图（PNG 已有，直接嵌入 base64 或同目录引用）、指标面板（含 visibility 悬浮提示）、findings 列表（severity 分色）、plan 节点链（串行图，enabled/reversible 可视化）、judgment_boundary 徽章、provenance 页脚。
- **技术**：Python 字符串模板组装（无新依赖；matplotlib 已是硬依赖，出 PNG 后 HTML 只做排版）。不做交互式绘图（plotly/dash 明确不引入）。
- **备选（不推荐为 v1）**：复活 `apps/ear-workbench` 静态工作台接 1.0 分析链——有价值但属于「产品 UI 线」，等单文件报告稳定后作为 Layer B+ 可选。
- 入口：`moodify report <case_id|report.json>` 重新渲染；`moodify report open`（可选）起 localhost 静态服务并开浏览器。

### 4.4 AI 调用面纪律（汇总现状 + 增补）

| 纪律 | 现状 | 增补 |
|---|---|---|
| stdout 恒 JSON / stderr 错误 JSON | 已有 | 保持 |
| exit code（0 成功 / 2 失败） | 已有 | 保持并写入协议文档 |
| schema 版本化 + 未知键拒绝 | 已有（MSP） | 扩展到 report.json（jsonschema 校验，依赖已有） |
| `next_actions` 可复制命令 | 无 | §4.2 plan 内提供 |
| `--format` | 无 | Layer A 加 `--format {json,summary}`（summary 为人读短表），可选 |

### 4.5 数据流（全链）

```
音频 ──▶ moodify.sound/0.2 analyze 作业
          │ decode → 四尺度表示 + 频谱图 → 理科测量 → 阈值判断
          ▼
     report.json / report.md / report.html（显示屏）
          │ plan.graph_draft（DRAFT_PLAN_NOT_EXECUTED）
          ▼
     AI 或人改写为 moodify.sound/0.2 process 作业
          │ Mix Graph v0.1 render（可重放/可旁路）
          ▼
     master.wav + evidence ──▶ compare 作业（Layer B）验证
```

## 5. 技术债清理（Layer A 顺手项，POSC_007）

| 项 | 动作 | 层 |
|---|---|---|
| G5 双 CLI 冲突 | `pyproject.toml` 为唯一入口权威；`setup.py` 入口点删除或与 pyproject 对齐；`cli.py analyze` 已有 `v01-analyze` 别名，文档标注 `analyze` 动词归 release_cli 语义 | A |
| G6 ffmpeg | 安装文档显式声明 + `moodify doctor`（可选，探测 ffmpeg/依赖并输出 JSON） | A |
| `cli_v2/`、`cli_daw/` 仅剩 `__pycache__` | 确认无引用后清残骸 | A |
| REPOSITORY_STATUS 能力表 56/69 行矛盾（Mix Graph 同一行既 EXPERIMENTAL 又 ABSENT） | 69 行为 v2.0 时代陈旧行，随 Mix Graph v0.1 完成事实更新 | A |

## 6. 路线图（层完成法：每层有界承诺 + 相称证明 + 收束）

**Layer A — 分析协议化 + 显示屏（基础版）**
- 承诺边界：MSP 0.2 analyze 作业 + report.json/md/html 三件套 + judgment_boundary/visibility/plan 字段落地；3 首试点曲（含 1 首 golden）出完整报告证据。
- 不做：compare 作业、阈值重校准、交互 UI、process 作业携带 graph。
- 证明：schema 校验测试 + report 快照测试 + golden case + 四道门（ruff / `pytest -m v01` / 全量 / CI）+ Canon 门。
- 收束物：`docs/protocol/MOODIFY_SOUND_PROTOCOL_0_2.md` + `artifacts/msp02_analysis_001/`。

**Layer B — 比较作业协议化（L2 激活）**
- 承诺边界：`compare` 作业（before/after 与 A/B，响度对齐前提校验复用 `validate_pair`），报告增加对比层（deltas、delta 频谱图、contact sheet）。
- 证明：响度对齐 A/B 黄金 case + 判断边界字段更新为 EXECUTED。

**Layer C — 阈值来源化与校准**
- 承诺边界：`UNIVERSAL_THRESHOLDS` 每条阈值带来源与日期（标准/实验/默认），未校准的标 `DEFAULT_UNCALIBRATED`；接 `sensitivity/` 与 lab 校准线。
- 证明：校准证据 + 敏感性报告。**这是商业化的科学信用基础**——「质量好坏」的判定可信度来自可公开检验的校准链。

**Layer D — 商业化前置（人类决策密集区）**
- 打包分发（pip/PyPI 之外：单二进制或容器）、云端 API 化与计量（LA 节点）、**license 结构**（仓库 GPL-3.0：商业闭源/双许可/开放核心，`HUMAN_DECISION_REQUIRED`）、品牌与定价。
- 本提案不含商业承诺；Layer D 开工前须独立提案。

## 7. 距离商业化的诚实评估

按书的语言：当前系统**功能**大量存在（1072 测试 = 主动记忆），**形式**正在收敛（Mix Graph 确定性重放、MSP 协议纪律），缺的是四样：

1. **诚实的能力边界**成为产品的一部分（本提案 judgment_boundary/visibility 直接口）。
2. **可分发的安装形态**（现状要求 Python 3.10 + ffmpeg + pinned 依赖，对目标用户不可接受）。
3. **校准的科学信用**（Layer C）。
4. **商业结构决策**（license/定价/目标客群——全是人类决策，AI 不代填）。

基础版（Layer A+B）在现有代码上没有科学风险，只有工程收口；真正的距离在 Layer C/D。

## 8. HUMAN_DECISION_REQUIRED

| # | 决策 | 推荐 | 影响 |
|---|---|---|---|
| D1 | 协议演进：MSP 0.2 内加作业类型（推荐） vs 独立 ear/analysis 协议 | **0.2 内加作业类型** | 独立协议违反 One Core 纪律，且碎片化 AI 调用面 |
| D2 | 显示屏形态：单文件 HTML 报告（推荐） vs 复活 ear-workbench vs App 内嵌 | **单文件 HTML** | workbench 属产品 UI 线（已 parked），App 属消费端（Canon），都不适合作为报告渲染器 v1 |
| D3 | 双 CLI 收敛：`moodify analyze` 归 1.0 扫描语义（推荐） vs 改名区分 | **归 1.0** | v0.1 已有 `v01-analyze` 别名，破坏面最小 |
| D4 | 报告是否永不包含单一总分 | **永不（除非未来人类显式裁决权重宪法）** | POSC_011；影响对外卖点形态，商业层再议 |
| D5 | Layer A 开工分支 | 续作 `codex/professional-finishing-layer-20260920` | 与 Mix Graph 同线，Canon 依据在此分支 |

## 9. 完成门（Layer A）

1. `ruff` 全绿
2. 新增测试 + `pytest -m v01` 全绿
3. 全量 pytest 全绿（LSM 模式 parallel=2）
4. GitHub Actions 绿
5. Canon 门：`python scripts/canon_guard.py` + 协议文档与 Canon v2.1 一致（0.2 草案标注 EXPERIMENTAL，冻结门 = golden + 确定性重放证据，沿 Mix Graph v0.1 先例）

---

*本提案所有 TARGET 表述不得在任何对外材料写成已实现。事实边界：§3 勘察快照为 2026-10-02 状态。*
