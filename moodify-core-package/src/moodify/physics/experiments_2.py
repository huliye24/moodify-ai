"""PHYSICS-009: 理论地基验证实验套件.

覆盖 PHYSICS-008 中 23 个未验证假设中不需要人耳的 12 个.
用法:
  python -m moodify.physics.experiments_2 --exp G   # 单个
  python -m moodify.physics.experiments_2 --exp all # 全部

输出: outputs/physics_2/<experiment_id>/
"""

import os, sys, json, time, hashlib, random, argparse
from pathlib import Path
from datetime import datetime

import numpy as np

np.random.seed(42)
random.seed(42)
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

SRC = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, SRC)
OUTPUT_BASE = Path(SRC).parent / "outputs" / "physics_2"


def checksum(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()[:16]


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
    with open(d / "checksum.txt", "w") as f:
        f.write(f"experiment={exp_id}\nchecksum={checksum(results)}\n")
    return d


def get_audio_paths():
    d = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    songs = sorted(d.glob("*.wav"))
    return songs if songs else []


# ═══════════════════════════════════════════════════════════
#  Experiment G: T_EFFECTS Validation (CH-1, Extended)
#  500 samples, per-emotion B matrix, compare predicted vs actual
# ═══════════════════════════════════════════════════════════

def experiment_G(n_samples: int = 100, emotions: list = None) -> dict:
    """CH-1: Validate T_EFFECTS against real DSP measurements."""
    print("\n" + "="*60)
    print("EXPERIMENT G: T_EFFECTS Validation (Extended)")
    print("="*60)

    import soundfile
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS
    from moodify.safety.bounds import HARD_BOUNDS
    from moodify.knowledge.emotion_targets import get_ideal_process_vector

    if emotions is None:
        emotions = ["GA", "DR", "WL"]

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}
    song = str(songs[len(songs)//2])  # middle song for variety
    print(f"  Audio: {Path(song).stem}, Emotions: {emotions}, Samples: {n_samples}")

    audio, sr = soundfile.read(song)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    engine = DiagnosisEngine()
    chain = SpectralDSPChain()
    raw_data = []
    all_results = {}

    for emotion in emotions:
        print(f"\n  --- {emotion} ---")
        preset = get_recommended_params(emotion)
        ideal = get_ideal_process_vector(emotion)

        # Baseline state
        vecs_before = []
        for _ in range(5):
            ws = engine.diagnose_quick(song)
            vecs_before.append(StateTransferEngine.diagnostic_to_process(ws).to_array())
        x0 = np.mean(vecs_before, axis=0)

        te_engine = StateTransferEngine()
        delta_X = []
        delta_U = []
        te_errors = []

        for i in range(n_samples):
            # Sample within HARD_BOUNDS (fix P12 issue from experiment A)
            u = {}
            for pk in PARAM_KEYS:
                if pk in preset and pk in HARD_BOUNDS:
                    lo, hi = HARD_BOUNDS[pk]
                    lo = max(lo, preset[pk] * 0.3)  # don't go below 30% of preset
                    hi = min(hi, preset[pk] * 2.5)  # don't go above 250% of preset
                    u[pk] = float(lo + np.random.random() * (hi - lo))

            try:
                processed = chain.process(audio, sr, u)
                with __import__('tempfile').NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    soundfile.write(tmp.name, processed, sr)
                    ws_after = engine.diagnose_quick(tmp.name)
                    os.unlink(tmp.name)

                x_i = StateTransferEngine.diagnostic_to_process(ws_after).to_array()
                dx_real = x_i - x0

                # T_EFFECTS prediction
                strength = _estimate_strength_from_params(u, emotion)
                dx_te = te_engine.apply_chain_transfer(strength)

                te_error = float(np.linalg.norm(dx_real - dx_te))

                delta_X.append(dx_real.tolist())
                delta_U.append([u.get(pk, 0) for pk in PARAM_KEYS])
                te_errors.append(te_error)

                raw_data.append({
                    "emotion": emotion, "sample": i,
                    "te_error": round(te_error, 4),
                    "dE_real": float(dx_real[0]), "dE_te": float(dx_te[0]),
                    "dD_real": float(dx_real[1]), "dD_te": float(dx_te[1]),
                    "dS_real": float(dx_real[2]), "dS_te": float(dx_te[2]),
                    "dT_real": float(dx_real[3]), "dT_te": float(dx_te[3]),
                    "dH_real": float(dx_real[4]), "dH_te": float(dx_te[4]),
                })
            except Exception as e:
                continue

            if (i+1) % 20 == 0:
                print(f"    {i+1}/{n_samples}, mean TE error: {np.mean(te_errors[-20:]):.4f}")

        # Analysis
        dX = np.array(delta_X).T
        te_arr = np.array(te_errors)

        # Per-dimension correlation: T_EFFECTS predicted vs real
        dim_names = ["E", "D", "S", "T", "H"]
        dim_corrs = {}
        for j, dim in enumerate(dim_names):
            real_dims = dX[j, :]
            # Extract TE predictions from raw_data
            te_preds = np.array([r[f"d{dim}_te"] for r in raw_data if r["emotion"] == emotion])
            real_vals = np.array([r[f"d{dim}_real"] for r in raw_data if r["emotion"] == emotion])
            if len(te_preds) > 5:
                corr = float(np.corrcoef(te_preds, real_vals)[0, 1])
                dim_corrs[dim] = round(corr, 3) if not np.isnan(corr) else 0.0

        fraction_good = np.mean(te_arr < 0.08)  # threshold from calibrate.py
        all_results[emotion] = {
            "n_valid": len(te_arr),
            "mean_te_error": round(float(np.mean(te_arr)), 4),
            "std_te_error": round(float(np.std(te_arr)), 4),
            "fraction_good": round(float(fraction_good), 3),
            "dim_correlations": dim_corrs,
        }
        print(f"    Valid: {len(te_arr)}, Mean TE error: {np.mean(te_arr):.4f}")
        print(f"    Fraction good (<0.08): {fraction_good:.2%}")
        print(f"    Dim correlations: {dim_corrs}")

    overall_good = np.mean([r["fraction_good"] for r in all_results.values()])
    h1 = overall_good >= 0.5

    results = {
        "experiment": "G",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-1: T_EFFECTS predicts real DSP displacement",
        "n_samples_per_emotion": n_samples,
        "emotions": emotions,
        "overall_fraction_good": round(float(overall_good), 3),
        "per_emotion": all_results,
        "h1_accepted": h1,
        "verdict": "PASS (TE usable)" if h1 else "FAIL (TE unreliable — confirmed PHYSICS-007 finding)",
    }
    path = save_results("G_te_validation", results, raw_data)
    print(f"\n  H1: {h1} | {results['verdict']}")
    print(f"  -> {path}")
    return results


def _estimate_strength_from_params(params: dict, emotion_code: str) -> dict:
    """Rough inverse: estimate 5D strength from 15D params."""
    from moodify.knowledge.craft_chains import CRAFT_CHAINS_15PARAMS, PARAM_KEYS
    from moodify.optimizer.search import STRENGTH_TO_PARAMS, CHAIN_ORDER

    chain = CRAFT_CHAINS_15PARAMS.get(emotion_code, {})
    strength = {}
    for dim in CHAIN_ORDER:
        pnames = STRENGTH_TO_PARAMS.get(dim, [])
        if not pnames:
            strength[dim] = 0.5
            continue
        ratios = []
        for pn in pnames:
            if pn in params and pn in chain:
                spec = chain[pn]
                if spec["max"] != spec["min"]:
                    ratio = (params[pn] - spec["min"]) / (spec["max"] - spec["min"])
                    ratios.append(max(0.0, min(1.0, ratio)))
        strength[dim] = float(np.mean(ratios)) if ratios else 0.5
    return strength


# ═══════════════════════════════════════════════════════════
#  Experiment H: LHS Search Convergence (CH-9)
# ═══════════════════════════════════════════════════════════

def experiment_H() -> dict:
    """CH-9: Test if 2000 LHS samples are enough for search convergence."""
    print("\n" + "="*60)
    print("EXPERIMENT H: LHS Search Convergence")
    print("="*60)

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.optimizer.search import search_optimal_strengths

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    engine = DiagnosisEngine()
    ws = engine.diagnose_quick(str(songs[0]))

    n_values = [100, 200, 500, 1000, 2000, 5000]
    n_seeds = 5
    raw_data = []

    print(f"  Testing n_samples from {n_values[0]} to {n_values[-1]}, {n_seeds} seeds each")

    for n in n_values:
        top_scores = []
        for seed in range(n_seeds):
            np.random.seed(seed)
            results = search_optimal_strengths(ws, "GA", top_k=3, n_samples=n,
                                                defects=[], vector_bias=None)
            if results:
                top_scores.append(results[0][2])  # top-1 proxy score
            np.random.seed(42)  # reset

        if top_scores:
            mean_score = float(np.mean(top_scores))
            std_score = float(np.std(top_scores, ddof=1)) if len(top_scores) > 1 else 0.0
            cv = std_score / abs(mean_score) if abs(mean_score) > 1e-6 else 0.0
            raw_data.append({
                "n_samples": n, "mean_top1_score": round(mean_score, 2),
                "std_top1_score": round(std_score, 2), "cv": round(cv, 4),
            })
            print(f"    n={n:5d}: top1={mean_score:.1f} +/- {std_score:.1f} (CV={cv:.3f})")

    # Check convergence: does CV decrease as n increases?
    cvs = [r["cv"] for r in raw_data]
    converged = len(cvs) >= 3 and cvs[-1] < 0.05  # CV < 5% at max n

    results = {
        "experiment": "H",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-9: 2000 LHS samples sufficient for search convergence",
        "convergence_data": raw_data,
        "cv_at_2000": raw_data[-2]["cv"] if len(raw_data) >= 5 else None,
        "cv_at_5000": raw_data[-1]["cv"] if raw_data else None,
        "h1_accepted": converged,
        "verdict": "PASS (search converges)" if converged else "FAIL (search unstable — increase n_samples)",
    }
    path = save_results("H_search_convergence", results, raw_data)
    print(f"\n  H1: {converged} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment I: AI Music Diagnostic Distribution (CH-8)
# ═══════════════════════════════════════════════════════════

def experiment_I() -> dict:
    """CH-8: Measure diagnostic parameter distribution on AI music."""
    print("\n" + "="*60)
    print("EXPERIMENT I: AI Music Diagnostic Distribution")
    print("="*60)

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.orchestration.state_transfer import StateTransferEngine

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    engine = DiagnosisEngine()
    classifier = DefectClassifier()

    # Collect diagnostics for all baseline audio
    all_params = {f"S{i}": [] for i in range(1, 6)}
    all_params.update({f"D{i}": [] for i in range(1, 5)})
    all_params.update({f"SP{i}": [] for i in range(1, 5)})
    all_params.update({f"L{i}": [] for i in range(1, 5)})
    all_params.update({f"E{i}": [] for i in range(1, 5)})

    defect_counts = {}
    raw_data = []

    for song in songs:
        for _ in range(10):  # multiple diagnoses per song for stability
            ws = engine.diagnose_quick(str(song))
            d = ws.to_dict()
            for cat in ["Spectrum", "Dynamics", "Space", "Layers", "Emotion"]:
                for k, v in d[cat.lower()].items():
                    key = f"{cat[0]}{k.split('_')[0][-1]}" if '_' in k else k
                    if isinstance(v, (int, float)):
                        full_key = f"{key}"
                        if full_key not in all_params:
                            full_key = f"{cat[0]}{list(d[cat.lower()].keys()).index(k)+1}"
                            if full_key not in all_params:
                                continue
                        all_params[full_key].append(float(v))

            # Check defect classification
            defects = classifier.classify(ws, "GA")
            for defect in defects:
                key = f"{defect.parameter}_{defect.severity}"
                defect_counts[key] = defect_counts.get(key, 0) + 1

            raw_data.append({
                "song": song.stem,
                "S1": d["spectrum"]["S1_SubPresence"],
                "S2": d["spectrum"]["S2_BassWarmth"],
                "S3": d["spectrum"]["S3_MidClarity"],
                "D1": d["dynamics"]["D1_LRA"],
                "E3": d["emotion"]["E3_FatigueRisk"],
            })

    # Compute distributions
    dist_stats = {}
    for key, vals in all_params.items():
        if vals:
            arr = np.array([v for v in vals if not np.isnan(v) and not np.isinf(v)])
            if len(arr) > 0:
                dist_stats[key] = {
                    "mean": round(float(np.mean(arr)), 3),
                    "std": round(float(np.std(arr)), 3),
                    "p5": round(float(np.percentile(arr, 5)), 3),
                    "p95": round(float(np.percentile(arr, 95)), 3),
                    "n": len(arr),
                }

    # Check: what fraction of AI music is classified as "defective"?
    total_classifications = sum(defect_counts.values())
    defect_rate = total_classifications / max(len(raw_data), 1)

    results = {
        "experiment": "I",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-8: Defect thresholds appropriate for AI music",
        "n_samples": len(raw_data),
        "average_defects_per_diagnosis": round(defect_rate, 2),
        "parameter_distributions": dist_stats,
        "h1_accepted": defect_rate < 5.0,  # < 5 defects per diagnosis is reasonable
        "verdict": "PASS (thresholds reasonable)" if defect_rate < 5.0
                   else f"FAIL ({defect_rate:.1f} defects/diag — thresholds too strict for AI music)",
    }
    path = save_results("I_ai_diagnostic_dist", results, raw_data)
    print(f"  Defects/diagnosis: {defect_rate:.1f}")
    print(f"  Parameters measured: {len(dist_stats)}")
    print(f"  H1: {results['h1_accepted']} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment J: EMA Alpha Optimization (CH-11)
# ═══════════════════════════════════════════════════════════

def experiment_J() -> dict:
    """CH-11: Find optimal EMA alpha for bias estimation."""
    print("\n" + "="*60)
    print("EXPERIMENT J: EMA Alpha Optimization")
    print("="*60)

    # Synthetic ground truth: known bias = -5.0, noise std = 2.0
    TRUE_BIAS = -5.0
    NOISE_STD = 2.0
    np.random.seed(12345)

    alphas = np.arange(0.02, 0.51, 0.02)
    n_trials = 20
    n_steps = 50
    raw_data = []

    print(f"  True bias={TRUE_BIAS}, noise={NOISE_STD}, {len(alphas)} alphas, {n_trials} trials")

    best_alpha = None
    best_error = float('inf')

    for alpha in alphas:
        final_errors = []
        half_lives = []

        for trial in range(n_trials):
            mu = 0.0  # start with no prior
            estimates = []

            for step in range(n_steps):
                obs = TRUE_BIAS + np.random.randn() * NOISE_STD
                mu = (1 - alpha) * mu + alpha * obs
                estimates.append(mu)

            final_error = abs(mu - TRUE_BIAS)
            final_errors.append(final_error)

            # Find half-life: steps until |estimate - true| < |true|/2
            half_steps = n_steps
            for s, est in enumerate(estimates):
                if abs(est - TRUE_BIAS) < abs(TRUE_BIAS) / 2:
                    half_steps = s + 1
                    break
            half_lives.append(half_steps)

        mean_error = float(np.mean(final_errors))
        mean_hl = float(np.mean(half_lives))
        raw_data.append({
            "alpha": round(float(alpha), 2),
            "mean_final_error": round(mean_error, 4),
            "mean_half_life": round(mean_hl, 1),
        })

        if mean_error < best_error:
            best_error = mean_error
            best_alpha = float(alpha)

    # Theoretical half-life for alpha=0.15
    hl_015 = np.log(2) / np.log(1 / (1 - 0.15))
    hl_015_correct = np.log(0.5) / np.log(1 - 0.15)  # = ln(0.5)/ln(0.85) ≈ 4.27

    results = {
        "experiment": "J",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-11: EMA alpha=0.15 is optimal",
        "current_alpha": 0.15,
        "current_half_life_claimed": 7,
        "current_half_life_actual": round(float(hl_015_correct), 2),
        "optimal_alpha": best_alpha,
        "optimal_error": round(best_error, 4),
        "alpha_scan": raw_data,
        "h1_accepted": abs(best_alpha - 0.15) < 0.05,
        "verdict": f"PASS (alpha=0.15 near optimal)"
                   if abs(best_alpha - 0.15) < 0.05
                   else f"FAIL (optimal alpha={best_alpha:.2f}, not 0.15)",
    }
    path = save_results("J_ema_alpha", results, raw_data)
    print(f"  Claimed half-life (code): 7 steps")
    print(f"  Actual half-life (math): {hl_015_correct:.1f} steps")
    print(f"  Optimal alpha: {best_alpha:.2f} (current: 0.15)")
    print(f"  H1: {results['h1_accepted']} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment K: Euclidean vs Mahalanobis Distance (CH-13)
# ═══════════════════════════════════════════════════════════

def experiment_K() -> dict:
    """CH-13: Compare Euclidean vs Mahalanobis distance rankings."""
    print("\n" + "="*60)
    print("EXPERIMENT K: Euclidean vs Mahalanobis Distance")
    print("="*60)

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.optimizer.search import get_static_sigma_inv, _mahalanobis_distance
    from moodify.knowledge.emotion_targets import get_ideal_process_vector

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    engine = DiagnosisEngine()
    raw_data = []

    emotions = ["GA", "DR", "WL", "SE", "HL"]
    disagreements = 0
    total_comparisons = 0

    for song in songs:
        # Generate multiple diagnoses by slightly perturbing input
        ws_base = engine.diagnose_quick(str(song))

        for emotion in emotions:
            ideal = get_ideal_process_vector(emotion)
            sigma_inv = get_static_sigma_inv()

            # Create 10 "versions" by adding small noise to the diagnosis
            vec_base = StateTransferEngine.diagnostic_to_process(ws_base).to_array()
            np.random.seed(42)
            versions = []
            for _ in range(10):
                noise = np.random.randn(5) * 0.02
                versions.append(np.clip(vec_base + noise, 0.0, 1.0))

            # Rank by Euclidean
            euclidean_dists = [float(np.linalg.norm(v - ideal)) for v in versions]
            euclidean_ranks = np.argsort(euclidean_dists)

            # Rank by Mahalanobis
            mahalanobis_dists = [float(_mahalanobis_distance(v, ideal, sigma_inv)) for v in versions]
            mahalanobis_ranks = np.argsort(mahalanobis_dists)

            # Compare top-3
            euclidean_top3 = set(euclidean_ranks[:3])
            mahalanobis_top3 = set(mahalanobis_ranks[:3])
            overlap = len(euclidean_top3 & mahalanobis_top3)

            if overlap < 2:  # disagree on at least 2 of top 3
                disagreements += 1
            total_comparisons += 1

            raw_data.append({
                "song": song.stem, "emotion": emotion,
                "euclidean_top3": str(sorted(euclidean_ranks[:3])),
                "mahalanobis_top3": str(sorted(mahalanobis_ranks[:3])),
                "overlap": overlap,
            })

    agreement_rate = 1.0 - disagreements / max(total_comparisons, 1)

    results = {
        "experiment": "K",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-13: Euclidean and Mahalanobis distances give consistent rankings",
        "n_comparisons": total_comparisons,
        "n_disagreements": disagreements,
        "agreement_rate": round(agreement_rate, 3),
        "h1_accepted": agreement_rate >= 0.8,
        "verdict": "PASS (consistent rankings)"
                   if agreement_rate >= 0.8
                   else "FAIL (inconsistent — Euclidean != Mahalanobis rankings)",
    }
    path = save_results("K_euclidean_vs_mahalanobis", results, raw_data)
    print(f"  Agreement rate: {agreement_rate:.1%} ({total_comparisons-disagreements}/{total_comparisons})")
    print(f"  H1: {results['h1_accepted']} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment L: HPSS Margin Optimization (CH-18)
# ═══════════════════════════════════════════════════════════

def experiment_L() -> dict:
    """CH-18: Find optimal HPSS margin for AI music."""
    print("\n" + "="*60)
    print("EXPERIMENT L: HPSS Margin Optimization")
    print("="*60)

    import soundfile
    import librosa

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    margins = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    raw_data = []

    for song in songs:
        audio, sr = soundfile.read(str(song))
        audio = audio.astype(np.float32)
        if audio.ndim > 1:
            audio = audio[:, 0]  # use left channel

        print(f"  {song.stem}:")
        for margin in margins:
            D = librosa.stft(audio, n_fft=2048, hop_length=512)
            H_mask, P_mask = librosa.decompose.hpss(D, margin=margin, mask=True)

            H = librosa.istft(D * H_mask, hop_length=512, length=len(audio))
            P = librosa.istft(D * P_mask, hop_length=512, length=len(audio))
            reconstructed = H + P

            # Reconstruction error
            min_len = min(len(audio), len(reconstructed))
            error = np.mean((audio[:min_len] - reconstructed[:min_len])**2)
            error_db = 10 * np.log10(error + 1e-10)

            # Energy in residual (R component = original - H - P)
            residual_energy = np.sum((audio[:min_len] - reconstructed[:min_len])**2) / (np.sum(audio[:min_len]**2) + 1e-10)

            raw_data.append({
                "song": song.stem, "margin": margin,
                "error_db": round(float(error_db), 2),
                "residual_energy_ratio": round(float(residual_energy), 4),
            })
            print(f"    margin={margin}: error={error_db:.1f}dB, residual={residual_energy:.3%}")

    # Find best margin (lowest average error)
    margin_errors = {}
    for r in raw_data:
        m = r["margin"]
        if m not in margin_errors:
            margin_errors[m] = []
        margin_errors[m].append(r["error_db"])

    avg_errors = {m: float(np.mean(errs)) for m, errs in margin_errors.items()}
    best_margin = min(avg_errors, key=avg_errors.get)
    current_margin = 2.0
    current_error = avg_errors.get(2.0, 0)
    best_error = avg_errors[best_margin]

    results = {
        "experiment": "L",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-18: HPSS margin=2.0 is optimal for AI music",
        "current_margin": current_margin,
        "current_error_db": round(current_error, 2),
        "best_margin": float(best_margin),
        "best_error_db": round(best_error, 2),
        "improvement_db": round(current_error - best_error, 2),
        "margin_scan": {str(k): round(v, 2) for k, v in avg_errors.items()},
        "h1_accepted": best_margin == 2.0 or abs(current_error - best_error) < 1.0,
        "verdict": f"PASS (margin=2.0 near optimal)"
                   if best_margin == 2.0 or abs(current_error - best_error) < 1.0
                   else f"FAIL (optimal margin={best_margin}, not 2.0)",
    }
    path = save_results("L_hpss_margin", results, raw_data)
    print(f"\n  Current margin: {current_margin} (error: {current_error:.1f}dB)")
    print(f"  Best margin: {best_margin} (error: {best_error:.1f}dB)")
    print(f"  H1: {results['h1_accepted']} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment M: Master Dimension Validity (CH-14)
# ═══════════════════════════════════════════════════════════

def experiment_M() -> dict:
    """CH-14: Test if master dimension has any effect on output."""
    print("\n" + "="*60)
    print("EXPERIMENT M: Master Dimension Validity")
    print("="*60)

    import soundfile
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.optimizer.search import strength_to_params, STRENGTH_TO_PARAMS, CHAIN_ORDER
    from moodify.orchestration.state_transfer import StateTransferEngine

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    audio, sr = soundfile.read(str(songs[0]))
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    engine = DiagnosisEngine()
    chain = SpectralDSPChain()

    # Baseline: all dimensions = 0.5
    base_strength = {d: 0.5 for d in CHAIN_ORDER}
    base_params = strength_to_params(base_strength, "GA")
    base_audio = chain.process(audio, sr, base_params)
    ws_base = engine.diagnose_quick.__wrapped__ if hasattr(engine.diagnose_quick, '__wrapped__') else engine.diagnose_quick

    # Test: vary master from 0.1 to 0.9, keep others fixed
    raw_data = []
    master_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    vecs = []

    for m_val in master_values:
        strength = {d: 0.5 for d in CHAIN_ORDER}
        strength["master"] = m_val
        params = strength_to_params(strength, "GA")

        # Check if params differ from baseline
        param_diff = sum(abs(params.get(k, 0) - base_params.get(k, 0)) for k in params)
        has_effect = param_diff > 1e-6

        processed = chain.process(audio, sr, params)
        with __import__('tempfile').NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            soundfile.write(tmp.name, processed, sr)
            ws = engine.diagnose_quick(tmp.name)
            os.unlink(tmp.name)

        vec = StateTransferEngine.diagnostic_to_process(ws).to_array()
        vecs.append(vec)

        raw_data.append({
            "master_strength": m_val,
            "param_diff_from_baseline": round(param_diff, 6),
            "any_param_changed": has_effect,
            "E": float(vec[0]), "D": float(vec[1]),
            "S": float(vec[2]), "T": float(vec[3]), "H": float(vec[4]),
        })
        print(f"    master={m_val}: param_diff={param_diff:.6f}, any_effect={has_effect}")

    # Check if varying master changes the output state
    vecs_arr = np.array([v for v in vecs])
    state_variance = float(np.var(vecs_arr))
    has_state_effect = state_variance > 1e-8

    results = {
        "experiment": "M",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-14: Master dimension controls zero parameters (wasted search dimension)",
        "any_param_changed": any(r["any_param_changed"] for r in raw_data),
        "state_variance": round(state_variance, 10),
        "has_any_effect": has_state_effect,
        "verdict": "PASS (master has effect)" if has_state_effect
                   else "FAIL (master dimension is dead — confirms CH-14)",
        "h1_accepted": has_state_effect,
    }
    path = save_results("M_master_dimension", results, raw_data)
    print(f"\n  Any param changed: {results['any_param_changed']}")
    print(f"  State variance: {state_variance:.2e}")
    print(f"  Has effect: {has_state_effect}")
    print(f"  H1: {has_state_effect} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment N: Quick vs Full Diagnosis (CH-17)
# ═══════════════════════════════════════════════════════════

def experiment_N() -> dict:
    """CH-17: Compare quick vs full diagnosis modes."""
    print("\n" + "="*60)
    print("EXPERIMENT N: Quick vs Full Diagnosis")
    print("="*60)

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.diagnosis.health_scorer import HealthScorer

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    engine = DiagnosisEngine()
    classifier = DefectClassifier()
    scorer = HealthScorer()
    raw_data = []

    whs_diffs = []

    for song in songs:
        for _ in range(5):
            ws_quick = engine.diagnose_quick(str(song))
            ws_full = engine.diagnose(str(song))

            defects_q = classifier.classify(ws_quick, "GA")
            defects_f = classifier.classify(ws_full, "GA")

            whs_q = scorer.compute_whs(ws_quick, defects_q)["WHS"]
            whs_f = scorer.compute_whs(ws_full, defects_f)["WHS"]

            diff = abs(whs_q - whs_f)
            whs_diffs.append(diff)

            raw_data.append({
                "song": song.stem,
                "whs_quick": round(whs_q, 1),
                "whs_full": round(whs_f, 1),
                "whs_diff": round(diff, 1),
            })
        print(f"  {song.stem}: WHS quick={whs_q:.1f}, full={whs_f:.1f}, diff={diff:.1f}")

    mean_diff = float(np.mean(whs_diffs))
    max_diff = float(np.max(whs_diffs))
    fraction_large = np.mean([1.0 for d in whs_diffs if d > 5.0])

    results = {
        "experiment": "N",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-17: Quick diagnosis is adequate substitute for full",
        "mean_whs_diff": round(mean_diff, 1),
        "max_whs_diff": round(max_diff, 1),
        "fraction_diff_gt_5": round(float(fraction_large), 3),
        "h1_accepted": mean_diff < 5.0 and fraction_large < 0.2,
        "verdict": "PASS (quick adequate)" if mean_diff < 5.0
                   else f"WARN (mean diff={mean_diff:.1f} WHS points)",
    }
    path = save_results("N_quick_vs_full", results, raw_data)
    print(f"\n  Mean WHS diff: {mean_diff:.1f}, Max: {max_diff:.1f}")
    print(f"  Fraction > 5: {fraction_large:.1%}")
    print(f"  H1: {results['h1_accepted']} | {results['verdict']}")
    print(f"  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment O: Reverb & Distortion Mapping (CH-19, CH-20)
# ═══════════════════════════════════════════════════════════

def experiment_O() -> dict:
    """CH-19/20: Validate reverb and distortion parameter mappings."""
    print("\n" + "="*60)
    print("EXPERIMENT O: Reverb & Distortion Mapping Validation")
    print("="*60)

    import soundfile
    import pedalboard

    songs = get_audio_paths()
    if not songs:
        return {"status": "FAIL", "reason": "No audio"}

    audio, sr = soundfile.read(str(songs[0]))
    audio = audio.astype(np.float32)
    if audio.ndim > 1:
        audio_mono = audio[:, 0]
    else:
        audio_mono = audio

    # Test reverb: scan dry_wet from 0.0 to 1.0
    raw_data = []
    dry_wet_values = np.arange(0.0, 1.05, 0.1)

    print("  Reverb mapping (dry_wet -> room_size + wet_level):")
    for dw in dry_wet_values:
        board = pedalboard.Pedalboard([
            pedalboard.Reverb(room_size=float(dw), damping=0.5,
                              wet_level=float(dw), dry_level=1.0-float(dw),
                              width=0.8),
        ])
        output = board(audio_mono.reshape(1, -1).astype(np.float32), sr)[0]
        rms_in = np.sqrt(np.mean(audio_mono**2))
        rms_out = np.sqrt(np.mean(output**2))
        gain_db = 20 * np.log10((rms_out + 1e-10) / (rms_in + 1e-10))

        raw_data.append({
            "param": "reverb_dry_wet", "value": round(float(dw), 1),
            "rms_gain_db": round(float(gain_db), 2),
        })

    # Test distortion: scan drive from 0.0 to 0.7
    print("  Distortion mapping (drive * 20 -> drive_db):")
    drive_values = np.arange(0.0, 0.75, 0.05)
    for dv in drive_values:
        board = pedalboard.Pedalboard([
            pedalboard.Distortion(drive_db=float(dv) * 20.0),
        ])
        output = board(audio_mono.reshape(1, -1).astype(np.float32), sr)[0]

        # Measure harmonic distortion
        rms_total = np.sqrt(np.mean(output**2))
        # Simple THD estimation: compare with lowpass-filtered version
        from scipy.signal import butter, filtfilt
        b, a = butter(4, 0.8)
        filtered = filtfilt(b, a, output)
        thd_approx = np.sqrt(np.mean((output - filtered)**2)) / (rms_total + 1e-10)

        raw_data.append({
            "param": "harmonic_drive", "value": round(float(dv), 2),
            "drive_db": round(float(dv) * 20.0, 1),
            "thd_estimate": round(float(thd_approx), 4),
        })

    results = {
        "experiment": "O",
        "timestamp": datetime.now().isoformat(),
        "assumption_tested": "CH-19/20: Reverb and distortion parameter mappings are reasonable",
        "mapping_data": raw_data,
        "verdict": "INFO (no pass/fail — visual inspection required)",
        "h1_accepted": True,  # informational only
    }
    path = save_results("O_reverb_distortion_map", results, raw_data)
    print(f"\n  -> {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════

EXPERIMENTS = {
    "G": experiment_G,
    "H": experiment_H,
    "I": experiment_I,
    "J": experiment_J,
    "K": experiment_K,
    "L": experiment_L,
    "M": experiment_M,
    "N": experiment_N,
    "O": experiment_O,
}


def main():
    parser = argparse.ArgumentParser(description="Moodify Physics Experiments II")
    parser.add_argument("--exp", required=True, help="G,H,I,J,K,L,M,N,O or 'all'")
    parser.add_argument("--n", type=int, default=0, help="Override sample size")
    args = parser.parse_args()

    if args.exp == "all":
        exp_ids = list(EXPERIMENTS.keys())
    else:
        exp_ids = [e.strip() for e in args.exp.split(",")]

    for eid in exp_ids:
        if eid not in EXPERIMENTS:
            print(f"Unknown experiment: {eid}")
            sys.exit(1)

    print(f"Moodify Physics Experiments II — {len(exp_ids)} experiments")
    print(f"Output: {OUTPUT_BASE}")
    t_start = time.perf_counter()

    all_results = {}
    for eid in exp_ids:
        t0 = time.perf_counter()
        func = EXPERIMENTS[eid]
        try:
            if args.n and eid == "G":
                result = func(n_samples=args.n)
            else:
                result = func()
            all_results[eid] = result
        except Exception as e:
            import traceback
            traceback.print_exc()
            all_results[eid] = {"status": "ERROR", "reason": str(e)}
        print(f"\n  [{eid}] elapsed: {time.perf_counter()-t0:.0f}s")

    total = time.perf_counter() - t_start
    print(f"\n{'='*60}")
    print("SUMMARY")
    for eid, r in all_results.items():
        print(f"  [{eid}] {r.get('verdict', 'ERROR')}")
    print(f"  Total: {total:.0f}s")

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_elapsed_s": round(total, 1),
        "results": {eid: {"verdict": r.get("verdict", "ERROR"),
                           "assumption": r.get("assumption_tested", "")}
                     for eid, r in all_results.items()},
    }
    with open(OUTPUT_BASE / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Summary: {OUTPUT_BASE / 'summary.json'}")


if __name__ == "__main__":
    main()
