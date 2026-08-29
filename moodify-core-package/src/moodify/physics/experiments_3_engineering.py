"""PHYSICS-010: Engineering Boundary Analysis — 参数灵敏度、单调性、可操作范围.

物理验证: "T_EFFECTS 是错的"
工程验证: "P02 在 +1.5~+3.5dB 内每 +1dB 提升 E 维度 +0.03, 超过 +4dB 饱和, SNR<2 时不可靠"

用法:
  python -m moodify.physics.experiments_3_engineering --exp all
输出: outputs/physics_3/
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np

np.random.seed(42)
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

SRC = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, SRC)
OUTPUT_BASE = Path(SRC).parent / "outputs" / "physics_3"
BASELINE_AUDIO = str(Path(SRC).parent / "tests" / "baseline" / "test_audio" / "piano.wav")


def save_results(exp_id: str, results: dict, raw_data: list = None):
    d = OUTPUT_BASE / exp_id
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    if raw_data:
        with open(d / "raw_data.csv", "w") as f:
            keys = list(raw_data[0].keys())
            f.write(",".join(keys) + "\n")
            for row in raw_data:
                f.write(",".join(str(row.get(k, "")) for k in keys) + "\n")
    return d


def _diagnose_5d(audio: np.ndarray, sr: int) -> np.ndarray:
    """Return 5D process vector for in-memory audio."""
    import soundfile
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.orchestration.state_transfer import StateTransferEngine
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        soundfile.write(tmp.name, audio, sr)
        tmp_path = tmp.name
    try:
        engine = DiagnosisEngine()
        ws = engine.diagnose_quick(tmp_path)
        return StateTransferEngine.diagnostic_to_process(ws).to_array()
    finally:
        os.unlink(tmp_path)


# ═══════════════════════════════════════════════════════════
#  Experiment P: Single-Parameter Sensitivity Sweeps
#  对 15 个参数逐个扫描, 测量每个参数对 5D 输出的因果效应
# ═══════════════════════════════════════════════════════════

def experiment_P(n_steps: int = 11, **kwargs) -> dict:
    """Single-parameter sweeps: measure d(output)/d(parameter) for all 15 params."""
    print("\n" + "="*60)
    print("EXPERIMENT P: Single-Parameter Sensitivity Sweeps")
    print("="*60)

    import soundfile
    from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.safety.bounds import HARD_BOUNDS

    audio, sr = soundfile.read(BASELINE_AUDIO)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    # Baseline state (mean of 10 diagnoses for noise reduction)
    x0_list = [_diagnose_5d(audio, sr) for _ in range(10)]
    x0 = np.mean(x0_list, axis=0)

    # Diagnosis noise floor (std across repeated diagnoses)
    noise_floor = float(np.mean(np.std(x0_list, axis=0)))

    chain = SpectralDSPChain()
    preset = get_recommended_params("GA")
    dim_names = ["E", "D", "S", "T", "H"]
    raw_data = []
    param_sensitivity = {}

    for pk in PARAM_KEYS:
        if pk not in preset or pk not in HARD_BOUNDS:
            continue

        lo, hi = HARD_BOUNDS[pk]
        rec = preset[pk]
        # Scan range: from max(lo, rec*0.3) to min(hi, rec*2.5) centered on rec
        scan_lo = max(lo, rec * 0.3)
        scan_hi = min(hi, rec * 2.5)

        if scan_hi - scan_lo < 1e-6:
            continue

        scan_values = np.linspace(scan_lo, scan_hi, n_steps)
        effects = {dim: [] for dim in dim_names}

        print(f"  {pk}: scanning {n_steps} points [{scan_lo:.1f}, {scan_hi:.1f}]...")

        for val in scan_values:
            params = dict(preset)
            params[pk] = float(val)
            try:
                processed = chain.process(audio, sr, params)
                x_i = _diagnose_5d(processed, sr)
                dx = x_i - x0
                for j, dim in enumerate(dim_names):
                    effects[dim].append(float(dx[j]))
                raw_data.append({
                    "parameter": pk, "value": round(float(val), 4),
                    "dE": float(dx[0]), "dD": float(dx[1]),
                    "dS": float(dx[2]), "dT": float(dx[3]),
                    "dH": float(dx[4]),
                })
            except Exception:
                for j, dim in enumerate(dim_names):
                    effects[dim].append(np.nan)

        # Analyze sensitivity per dimension
        dim_analysis = {}
        for dim in dim_names:
            arr = np.array(effects[dim])
            valid = arr[~np.isnan(arr)]
            if len(valid) < 3:
                dim_analysis[dim] = {"sensitivity": 0, "r2": 0, "snr": 0, "monotonic": False}
                continue

            # Linear sensitivity: d(dim)/d(param)
            x_vals = np.array(scan_values)[~np.isnan(arr)]
            y_vals = valid
            if len(x_vals) >= 3:
                slope, intercept = np.polyfit(x_vals, y_vals, 1)
                y_pred = slope * x_vals + intercept
                ss_res = np.sum((y_vals - y_pred)**2)
                ss_tot = np.sum((y_vals - np.mean(y_vals))**2)
                r2 = 1 - ss_res / (ss_tot + 1e-10)

                # SNR: max effect / noise floor
                effect_range = float(np.max(y_vals) - np.min(y_vals))
                snr = effect_range / (noise_floor + 1e-10)

                # Monotonicity: Spearman correlation between param value and effect
                from scipy.stats import spearmanr
                mono_corr = float(spearmanr(x_vals, y_vals)[0])
                monotonic = abs(mono_corr) > 0.7

                dim_analysis[dim] = {
                    "sensitivity": round(float(slope), 6),
                    "r2": round(float(r2), 3),
                    "snr": round(float(snr), 1),
                    "effect_range": round(float(effect_range), 4),
                    "monotonic_correlation": round(float(mono_corr), 3),
                    "monotonic": monotonic,
                }

        param_sensitivity[pk] = {
            "dim_effects": dim_analysis,
            "scan_range": [round(float(scan_lo), 2), round(float(scan_hi), 2)],
            "rec_value": round(float(rec), 2),
            "hard_bounds": [lo, hi],
        }

    # Identify engineering-useful parameters (SNR > 2 and monotonic in at least one dim)
    useful_params = []
    useless_params = []
    for pk, info in param_sensitivity.items():
        max_snr = max(d["snr"] for d in info["dim_effects"].values())
        any_mono = any(d["monotonic"] for d in info["dim_effects"].values())
        if max_snr > 2 and any_mono:
            useful_params.append(pk)
        else:
            useless_params.append(pk)

    results = {
        "experiment": "P",
        "timestamp": datetime.now().isoformat(),
        "diagnosis_noise_floor": round(noise_floor, 6),
        "n_parameters_tested": len(param_sensitivity),
        "n_useful": len(useful_params),
        "n_useless": len(useless_params),
        "useful_params": useful_params,
        "useless_params": useless_params,
        "param_sensitivity": param_sensitivity,
    }
    path = save_results("P_param_sensitivity", results, raw_data)
    print(f"\n  Noise floor: {noise_floor:.4f}")
    print(f"  Useful params (SNR>2 & monotonic): {len(useful_params)}/{len(param_sensitivity)}")
    print(f"  Useless params: {useless_params}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment Q: Parameter Interaction Detection
#  测试关键参数对的交互效应 (非可加性)
# ═══════════════════════════════════════════════════════════

def experiment_Q(**kwargs) -> dict:
    """Detect non-additive interactions between parameter pairs."""
    print("\n" + "="*60)
    print("EXPERIMENT Q: Parameter Interaction Detection")
    print("="*60)

    import soundfile
    from moodify.knowledge.craft_chains import get_recommended_params
    from moodify.processing.spectral_chain import SpectralDSPChain

    audio, sr = soundfile.read(BASELINE_AUDIO)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    x0 = _diagnose_5d(audio, sr)
    chain = SpectralDSPChain()
    preset = get_recommended_params("GA")

    # Key pairs to test (from domain knowledge + Experiment P results)
    test_pairs = [
        ("P02_vocal_presence_gain", "P15_high_shelf_gain"),   # both affect brightness
        ("P06_compression_ratio", "P09_compression_threshold"), # compressor params
        ("P06_compression_ratio", "P13_harmonic_drive"),       # dynamics + distortion
        ("P10_reverb_t60", "P11_reverb_dry_wet"),              # reverb params
        ("P04_proximity_low_freq", "P05_proximity_low_gain"),  # low warmth
    ]

    dim_names = ["E", "D", "S", "T", "H"]
    raw_data = []
    interaction_results = {}

    for pk_a, pk_b in test_pairs:
        rec_a = preset[pk_a]
        rec_b = preset[pk_b]

        # 4 corners: (lo,lo), (lo,hi), (hi,lo), (hi,hi)
        lo_a, hi_a = rec_a * 0.3, rec_a * 2.0
        lo_b, hi_b = rec_b * 0.3, rec_b * 2.0

        corners = [(lo_a, lo_b), (lo_a, hi_b), (hi_a, lo_b), (hi_a, hi_b)]
        effects = []

        for va, vb in corners:
            params = dict(preset)
            params[pk_a] = float(va)
            params[pk_b] = float(vb)
            try:
                processed = chain.process(audio, sr, params)
                x_i = _diagnose_5d(processed, sr)
                dx = x_i - x0
                effects.append(dx)
            except Exception:
                effects.append(np.zeros(5))

        # Interaction: E(hi,hi) - E(lo,hi) - E(hi,lo) + E(lo,lo)
        # If additive: interaction ≈ 0 for all dims
        interaction = effects[3] - effects[2] - effects[1] + effects[0]
        interaction_norm = float(np.linalg.norm(interaction))

        # Main effects for comparison
        main_a = float(np.linalg.norm(effects[2] - effects[0]))  # effect of A at lo_B
        main_b = float(np.linalg.norm(effects[1] - effects[0]))  # effect of B at lo_A

        interaction_ratio = interaction_norm / (main_a + main_b + 1e-10)
        significant = interaction_ratio > 0.3  # interaction > 30% of main effects

        interaction_results[f"{pk_a} x {pk_b}"] = {
            "interaction_norm": round(interaction_norm, 4),
            "main_effect_a": round(main_a, 4),
            "main_effect_b": round(main_b, 4),
            "interaction_ratio": round(float(interaction_ratio), 3),
            "significant": significant,
        }

        for dim_idx, dim in enumerate(dim_names):
            raw_data.append({
                "pair": f"{pk_a} x {pk_b}", "dimension": dim,
                "interaction_effect": float(interaction[dim_idx]),
                "significant": significant,
            })

        print(f"  {pk_a} x {pk_b}: ratio={interaction_ratio:.3f}, sig={significant}")

    n_sig = sum(1 for v in interaction_results.values() if v["significant"])

    results = {
        "experiment": "Q",
        "timestamp": datetime.now().isoformat(),
        "n_pairs_tested": len(test_pairs),
        "n_significant_interactions": n_sig,
        "interactions": interaction_results,
        "verdict": "INTERACTIONS DETECTED" if n_sig > 0 else "ADDITIVE (no interactions)",
    }
    path = save_results("Q_param_interactions", results, raw_data)
    print(f"\n  Significant interactions: {n_sig}/{len(test_pairs)}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment R: 5D Strength-to-Effect Calibration
#  For each strength dimension, measure actual (not T_EFFECTS) effect
# ═══════════════════════════════════════════════════════════

def experiment_R(**kwargs) -> dict:
    """Calibrate: what does changing each 5D strength actually do to the output?"""
    print("\n" + "="*60)
    print("EXPERIMENT R: 5D Strength-to-Effect Calibration")
    print("="*60)

    import soundfile
    from moodify.optimizer.search import strength_to_params, CHAIN_ORDER
    from moodify.processing.spectral_chain import SpectralDSPChain

    audio, sr = soundfile.read(BASELINE_AUDIO)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    x0 = _diagnose_5d(audio, sr)
    chain = SpectralDSPChain()
    dim_names = ["E", "D", "S", "T", "H"]

    # For each strength dimension, vary from 0.1 to 0.9, hold others at 0.5
    strength_levels = np.arange(0.1, 0.95, 0.1)
    raw_data = []
    strength_effects = {}

    for target_dim in CHAIN_ORDER:
        if target_dim == "master":
            continue  # skip dead dimension

        effects = {dim: [] for dim in dim_names}

        for s_val in strength_levels:
            strength = {d: 0.5 for d in CHAIN_ORDER}
            strength[target_dim] = float(s_val)
            params = strength_to_params(strength, "GA")
            try:
                processed = chain.process(audio, sr, params)
                x_i = _diagnose_5d(processed, sr)
                dx = x_i - x0
                for j, dim in enumerate(dim_names):
                    effects[dim].append(float(dx[j]))
                raw_data.append({
                    "strength_dim": target_dim, "strength_value": round(float(s_val), 2),
                    "dE": float(dx[0]), "dD": float(dx[1]),
                    "dS": float(dx[2]), "dT": float(dx[3]), "dH": float(dx[4]),
                })
            except Exception:
                for j, dim in enumerate(dim_names):
                    effects[dim].append(np.nan)

        # Compare against T_EFFECTS prediction
        dim_analysis = {}
        for dim in dim_names:
            arr = np.array(effects[dim])
            valid_idx = ~np.isnan(arr)
            if np.sum(valid_idx) < 3:
                dim_analysis[dim] = {"linear": False, "r2": 0}
                continue

            x_vals = strength_levels[valid_idx]
            y_vals = arr[valid_idx]
            slope, intercept = np.polyfit(x_vals, y_vals, 1)
            y_pred = slope * x_vals + intercept
            r2 = 1 - np.sum((y_vals - y_pred)**2) / (np.sum((y_vals - np.mean(y_vals))**2) + 1e-10)

            # Check if effect is in expected direction
            effect_sign = "positive" if slope > 0.001 else ("negative" if slope < -0.001 else "zero")
            effect_range = float(np.max(y_vals) - np.min(y_vals))

            dim_analysis[dim] = {
                "slope": round(float(slope), 4),
                "r2": round(float(r2), 3),
                "effect_range": round(float(effect_range), 4),
                "direction": effect_sign,
            }

        strength_effects[target_dim] = dim_analysis
        print(f"  {target_dim}: max_r2={max(d['r2'] for d in dim_analysis.values()):.3f}")

    # Count dimensions where at least one output dim responds linearly
    responsive_dims = sum(1 for d, info in strength_effects.items()
                          if any(v['r2'] > 0.5 for v in info.values()))

    results = {
        "experiment": "R",
        "timestamp": datetime.now().isoformat(),
        "n_strength_dims_tested": len(strength_effects),
        "n_responsive": responsive_dims,
        "strength_effects": strength_effects,
        "verdict": f"{responsive_dims}/{len(strength_effects)} strength dims have linear effect",
    }
    path = save_results("R_strength_calibration", results, raw_data)
    print(f"\n  Responsive dims: {responsive_dims}/{len(strength_effects)}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════

EXPERIMENTS = {"P": experiment_P, "Q": experiment_Q, "R": experiment_R}


def main():
    parser = argparse.ArgumentParser(description="Moodify Engineering Boundary Analysis")
    parser.add_argument("--exp", required=True, help="P,Q,R or 'all'")
    args = parser.parse_args()

    exp_ids = list(EXPERIMENTS.keys()) if args.exp == "all" else [e.strip() for e in args.exp.split(",")]

    print(f"Moodify Engineering Boundary Analysis — {len(exp_ids)} experiments")
    print(f"Output: {OUTPUT_BASE}")
    t_start = time.perf_counter()

    all_results = {}
    for eid in exp_ids:
        t0 = time.perf_counter()
        try:
            result = EXPERIMENTS[eid]()
            all_results[eid] = result
        except Exception as e:
            import traceback
            traceback.print_exc()
            all_results[eid] = {"status": "ERROR", "reason": str(e)}
        print(f"  [{eid}] elapsed: {time.perf_counter()-t0:.0f}s")

    total = time.perf_counter() - t_start
    print(f"\n{'='*60}")
    print(f"Total: {total:.0f}s")
    print(f"Output: {OUTPUT_BASE}")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_elapsed_s": round(total, 1),
        "results": {eid: r.get("verdict", "ERROR") for eid, r in all_results.items()},
    }
    with open(OUTPUT_BASE / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)


if __name__ == "__main__":
    main()
