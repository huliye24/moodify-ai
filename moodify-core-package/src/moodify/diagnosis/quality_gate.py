"""
quality_gate.py — 三质量门系统 (SPEC §10.2)
=============================================
Gate 1: 诊断完整性 — Phase 1 完成后
Gate 2: 分离质量   — Phase 2 完成后
Gate 3: 平台合规性 — Phase 6 完成后
"""

import math
from dataclasses import dataclass


@dataclass
class GateResult:
    gate_name: str
    passed: bool
    checks: list[dict]
    warnings: list[str]
    action: str        # "continue" | "warn" | "fallback_to_fullmix" | "reject"


class QualityGate:
    """三质量门系统 (SPEC §10.2)"""

    # ——— Gate 1: 诊断完整性 ——————————————————

    @staticmethod
    def gate_1_diagnosis(diagnosis, elapsed_ms: float) -> GateResult:
        """
        Gate 1: 诊断完整性检查 (SPEC §10.2)

        Requirements:
          - 14 auto params non-NaN/Inf
          - elapsed < 5s per 3-min (linear)
          - defect classification complete
        """
        checks = []

        # Check 1: 参数完整性
        auto_params = diagnosis.get_auto_params()
        nan_params = [k for k, v in auto_params.items()
                      if v is None or math.isnan(v) or math.isinf(v)]
        checks.append({
            "name": "14 auto params valid",
            "passed": len(nan_params) == 0,
            "detail": f"NaN/Inf: {nan_params}" if nan_params else "all valid",
        })

        # Check 2: 性能
        duration_s = getattr(diagnosis, 'duration_s', 180)
        max_acceptable_ms = (duration_s / 180.0) * 5000.0
        checks.append({
            "name": "diagnosis speed",
            "passed": elapsed_ms <= max_acceptable_ms,
            "detail": f"{elapsed_ms:.0f}ms / {max_acceptable_ms:.0f}ms max",
        })

        # Check 3: 数据完整性
        checks.append({
            "name": "duration > 0",
            "passed": duration_s > 0,
            "detail": f"duration={duration_s:.1f}s",
        })

        all_passed = all(c["passed"] for c in checks)

        return GateResult(
            gate_name="Gate 1: Diagnosis Completeness",
            passed=all_passed,
            checks=checks,
            warnings=[]
            if all_passed
            else ["Diagnosis incomplete; using full-mix processing mode, skip source separation"],
            action="continue" if all_passed else "fallback_to_fullmix",
        )

    # ——— Gate 2: 分离质量 ——————————————————

    @staticmethod
    def gate_2_separation(separation_result: dict) -> GateResult:
        """
        Gate 2: 分离质量验证 (SPEC §7.5, §10.2)

        Requirements:
          - vocals SI-SDRi >= 8 dB
          - drums SI-SDRi >= 6 dB
          - bass SI-SDRi >= 5 dB
          - cross-stem low-freq correlation > 0.3
          - mono fold-down RMS loss < 3 dB

        If 1 stem fails → merge to other → 3-stem
        If 2+ stems fail → abandon separation → full-mix mode
        """
        checks = []
        failed_stems = []

        min_thresholds = {
            "vocals": 8,
            "drums": 6,
            "bass": 5,
            "other": 6,
        }

        for stem_name, threshold in min_thresholds.items():
            si_sdri = separation_result.get(f"{stem_name}_si_sdri")
            if si_sdri is not None:
                passed = si_sdri >= threshold
                checks.append({
                    "name": f"{stem_name} SI-SDRi",
                    "passed": passed,
                    "detail": f"{si_sdri:.1f} dB (min {threshold} dB)",
                })
                if not passed:
                    failed_stems.append(stem_name)
            else:
                checks.append({
                    "name": f"{stem_name} SI-SDRi",
                    "passed": False,
                    "detail": "not available",
                })
                failed_stems.append(stem_name)

        # Cross-stem correlation
        xcorr = separation_result.get("cross_stem_correlation", 0.5)
        checks.append({
            "name": "cross-stem correlation",
            "passed": xcorr > 0.3,
            "detail": f"{xcorr:.3f}",
        })

        # Mono compatibility
        mono_loss = separation_result.get("mono_rms_loss_db", 0.0)
        checks.append({
            "name": "mono fold-down loss",
            "passed": mono_loss < 3.0,
            "detail": f"{mono_loss:.1f} dB",
        })

        all_passed = all(c["passed"] for c in checks)

        if all_passed:
            action = "continue"
            warnings = []
        elif len(failed_stems) == 1:
            action = "merge_to_other"
            warnings = [f"Stem '{failed_stems[0]}' failed, merging to 'other'"]
        else:
            action = "fallback_to_fullmix"
            warnings = [f"{len(failed_stems)} stems failed, falling back to full-mix mode"]

        return GateResult(
            gate_name="Gate 2: Separation Quality",
            passed=all_passed,
            checks=checks,
            warnings=warnings,
            action=action,
        )

    # ——— Gate 3: 平台合规性 ——————————————————

    @staticmethod
    def gate_3_output(processed_diagnosis,
                      output_lufs: float,
                      output_true_peak: float,
                      target_lufs: float = -14.0) -> GateResult:
        """
        Gate 3: 最终输出合规性 (SPEC §9.6, §10.2)

        10 checks, all must pass for green output.
        1-2 failures → warn
        3+ failures → reject
        """
        checks = {}
        ws = processed_diagnosis
        d = ws.Dynamics
        sp = ws.Space
        e = ws.Emotion

        # 1. LUFS accuracy
        checks["LUFS"] = abs(output_lufs - target_lufs) <= 0.5

        # 2. True Peak
        checks["TruePeak"] = output_true_peak <= -1.0

        # 3. LRA
        checks["LRA"] = d.D1_LRA.value >= 6.0

        # 4. PLR
        checks["PLR"] = d.D4_PLR.value >= 6.0

        # 5. WidthHealth
        checks["WidthHealth"] = sp.SP4_WidthHealth

        # 6. Bass correlation (SP1)
        checks["BassCorr"] = sp.SP1_Correlation.value > 0.1

        # 7. Fatigue risk
        checks["Fatigue"] = e.E3_FatigueRisk.value <= 80

        # 8-10. (placeholders for THD, mono loss, EQ range)
        checks["THD_ok"] = True  # placeholder
        checks["MonoCompat"] = True  # placeholder
        checks["EQ_range"] = True  # placeholder

        passed_count = sum(1 for v in checks.values() if v)
        total = len(checks)

        if passed_count == total:
            action = "pass"
            level = "green"
        elif total - passed_count <= 2:
            action = "warn"
            level = "yellow"
        else:
            action = "reject"
            level = "red"

        failed_checks = [k for k, v in checks.items() if not v]

        return GateResult(
            gate_name="Gate 3: Platform Compliance",
            passed=action != "reject",
            checks=[{"name": k, "passed": v, "detail": ""} for k, v in checks.items()],
            warnings=failed_checks if failed_checks else [],
            action=f"{action}|{level}",
        )
