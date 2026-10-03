# MSP/0.2 Calibration — Layer C Evidence Pack

**Schema:** `threshold-provenance-v1` + `threshold-sensitivity-v1`（判定规则 judgment-rules-**v1.1**）
**Generated:** 2026-10-02，core `1.0.0-rc.1`，branch `codex/professional-finishing-layer-20260920`
**证明目标（设计提案 §6 Layer C）：** 阈值来源化 + 敏感性验证 ——「质量好坏」判定的可信度来自可公开检验的校准链

## Headline（诚实事实）

- **16/16 条阈值全部 `DEFAULT_UNCALIBRATED`**：0 STANDARD / 0 EXPERIMENTAL / 16 DEFAULT。没有任何一条阈值经过听感校准或标准溯源——本证据包把这件事变成机器可读、报告可见的公开事实，而不是掩盖它。
- **数值冻结证明**：`UNIVERSAL_THRESHOLDS` 16 条值集合自 `5452ff44`（2026-08-02，AS-001）引入以来逐位未变（全提交历史比对，2026-10-02 验证）。Layer C **只做来源化，不改任何数值**；改值 = 重校准，需要实验证据 + 人类决策记录（测试钉死）。

## Contents

| Path | What it is |
|---|---|
| `calibration_registry.json` | `THRESHOLD_PROVENANCE` 全量 dump：每条阈值的 source_class / source 引用 / date / introduced_in / calibration_status / calibratable + `calibration_summary` |
| `sensitivity_report.json` | 敏感性报告：16 条规则经生产代码路径 `evaluate_risk_flags` 的翻转点扫描 + lab 校准桥 |

## Sensitivity report（敏感性验证）

方法：对每条规则沿其驱动量做单调段二分（离散规则用边界探测），观测裁决翻转点并与声明阈值比对。**无音频、无 DSP**——受测代码就是生产判定路径本身。

- **16/16 翻转点与声明阈值一致**（`all_match: true`）：如 `excessive_loudness_increase` 恰在 Δ=+4.0 LU 翻转、`duration_changed` 恰在 ±0.05 s 翻转、`analysis_confidence_low` 恰在 finite ratio 0.999 翻转。
- **lab 校准桥**：记录哪些 `auditory.lab` 扰动阶梯能产生越过阈值的刺激（GAIN_STEP 8/12 dB 越过 4.0 LU；SILENCE_INSERT 300/600/1000 ms 越过 ±50 ms；HARD_CLIP 必然越过 max_count=0）。**可达性映射而已**——由阶梯运行推导校准值是 lab 校准线的后续工作，本层不声称。单位不可比的配对（如压缩比 vs crest 降幅）显式标 `comparable: false`，不做伪精确断言。

## Reproduce

```bash
cd moodify-core-package
PYTHONPATH=src python -m pytest tests/test_msp02_calibration.py -q
# sensitivity_report.json：
PYTHONPATH=src python -c "from moodify.auditory.sensitivity import build_sensitivity_report; import json,pathlib; pathlib.Path('../artifacts/msp02_calibration_001/sensitivity_report.json').write_text(json.dumps(build_sensitivity_report(), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')"
# calibration_registry.json：
PYTHONPATH=src python -c "from moodify.auditory.judgment import THRESHOLD_PROVENANCE, calibration_summary, JUDGMENT_RULES_VERSION; import json,pathlib; registry={'registry_version':'threshold-provenance-v1','judgment_rules_version':JUDGMENT_RULES_VERSION,'compiled':'2026-10-02','table_frozen_since':{'commit':'5452ff44','date':'2026-08-02','verified':'2026-10-02 全提交历史逐位比对（16 条值集合 hash 6ea490e946 恒定）'},'source_classes':{'STANDARD':'数值可溯源到具名公开标准','EXPERIMENTAL':'数值由仓库内 lab 实验推导（auditory.lab / physics 校准线）','DEFAULT':'仓库内工程默认值，尚无校准证据'},'calibration_statuses':['CALIBRATED','DEFAULT_UNCALIBRATED'],'threshold_provenance':THRESHOLD_PROVENANCE,'calibration_summary':calibration_summary()}; pathlib.Path('../artifacts/msp02_calibration_001/calibration_registry.json').write_text(json.dumps(registry, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')"
```

Same code version → 逐字节相同输出（纯算术，无时间戳、无随机源）。

## Fact boundary

- 本包证明：**每条阈值带来源与日期、未校准者显式标记、判定规则在声明位置精确翻转、lab 阶梯可达性已映射**。
- 本包**不证明**：任何阈值是听感正确的限值。敏感性验证只证明「规则在声明的数值处翻转」，不证明「该数值是感知显著性的正确位置」——后者需要 lab 校准线产生人类/代理评审证据，是后续工作。
- `DEFAULT_UNCALIBRATED` 不得当作已验证限值消费；报告内的校准计数（`0/16 已校准`）是对下游 AI 消费者的显式警示。
- 防重校准护栏：`tests/test_msp02_calibration.py::test_threshold_values_are_frozen` 钉死全部 16 个数值；任何改值都会作为显式测试变更出现。
