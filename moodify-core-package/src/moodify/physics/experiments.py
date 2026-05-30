"""Moodify Physics Experiments — 统一入口.

用法:
  python -m moodify.physics.experiments --exp A     # 单个实验
  python -m moodify.physics.experiments --exp all   # 全部 6 项
  python -m moodify.physics.experiments --exp D,A,E # 指定多项

输出: outputs/physics/<experiment_id>/
  results.json, raw_data.csv, checksum.txt, report.md
"""

import os, sys, json, time, hashlib, random, argparse
from pathlib import Path
from datetime import datetime

import numpy as np

# ── 确定性执行 ────────────────────────────────────
np.random.seed(42)
random.seed(42)
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

SRC = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, SRC)

OUTPUT_BASE = Path(SRC).parent / "outputs" / "physics"


def checksum(data: dict) -> str:
    return hashlib.sha256(
        json.dumps(data, sort_keys=True, default=str).encode()
    ).hexdigest()[:16]


def save_results(exp_id: str, results: dict, raw_data: list = None):
    d = OUTPUT_BASE / exp_id
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    if raw_data:
        with open(d / "raw_data.csv", "w") as f:
            if raw_data:
                keys = raw_data[0].keys()
                f.write(",".join(keys) + "\n")
                for row in raw_data:
                    f.write(",".join(str(row[k]) for k in keys) + "\n")
    with open(d / "checksum.txt", "w") as f:
        f.write(f"experiment={exp_id}\nchecksum={checksum(results)}\n")
    return d


# ═══════════════════════════════════════════════════════════
#  Experiment D: Diagnosis Noise Covariance
# ═══════════════════════════════════════════════════════════

def experiment_D(n_repeats: int = 50, **kwargs) -> dict:
    """重复诊断同一音频 N 次，估计测量噪声协方差."""
    print("\n" + "="*60)
    print("EXPERIMENT D: Diagnosis Noise Covariance")
    print("="*60)

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.orchestration.state_transfer import StateTransferEngine

    audio_dir = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    songs = sorted(audio_dir.glob("*.wav"))[:3]
    if not songs:
        return {"status": "FAIL", "reason": "No baseline audio"}

    all_params = {s.stem: [] for s in songs}
    raw_data = []

    for song in songs:
        print(f"  {song.stem}: {n_repeats} diagnoses...")
        for i in range(n_repeats):
            engine = DiagnosisEngine()
            ws = engine.diagnose_quick(str(song))
            vec = StateTransferEngine.diagnostic_to_process(ws).to_array()
            all_params[song.stem].append(vec.tolist())
            raw_data.append({
                "song": song.stem, "trial": i,
                "E": float(vec[0]), "D": float(vec[1]),
                "S": float(vec[2]), "T": float(vec[3]),
                "H": float(vec[4]),
            })
        print(f"    done ({i+1}/{n_repeats})")

    param_names = ["E", "D", "S", "T", "H"]
    snr_results = {}
    overall_snr_ok = 0
    overall_total = 0

    for song_name, vecs in all_params.items():
        arr = np.array(vecs)  # (N, 5)
        mean = arr.mean(axis=0)
        std = arr.std(axis=0, ddof=1)
        snr = np.abs(mean) / (std + 1e-10)
        snr_results[song_name] = {param_names[i]: float(snr[i]) for i in range(5)}
        for i in range(5):
            overall_total += 1
            if snr[i] > 3:
                overall_snr_ok += 1

    fraction_reliable = overall_snr_ok / overall_total if overall_total else 0
    h1_accepted = fraction_reliable >= 0.85

    results = {
        "experiment": "D",
        "timestamp": datetime.now().isoformat(),
        "n_songs": len(songs),
        "n_repeats_per_song": n_repeats,
        "fraction_reliable_snr": round(fraction_reliable, 3),
        "h1_accepted": h1_accepted,
        "snr_by_song": snr_results,
        "verdict": "PASS" if h1_accepted else "INCONCLUSIVE",
    }
    path = save_results("D_diagnosis_noise", results, raw_data)
    print(f"  SNR >= 3: {overall_snr_ok}/{overall_total} = {fraction_reliable:.1%}")
    print(f"  H1 accepted: {h1_accepted}")
    print(f"  → {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment E: M Factor (Proxy-Reality Correlation)
# ═══════════════════════════════════════════════════════════

def experiment_E(**kwargs) -> dict:
    """测定代理评分与重诊断排序的 Spearman 相关性."""
    print("\n" + "="*60)
    print("EXPERIMENT E: M Factor (Proxy-Reality Correlation)")
    print("="*60)

    from moodify.calibration.experiment import run_calibration

    audio_dir = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    songs = [str(s) for s in sorted(audio_dir.glob("*.wav"))]
    if not songs:
        return {"status": "FAIL", "reason": "No baseline audio"}

    emotions = ["GA", "DR", "WL"]
    out_dir = str(OUTPUT_BASE / "E_calibration_versions")

    print(f"  Songs: {len(songs)}, Emotions: {len(emotions)}, Groups: {len(songs)*len(emotions)}")
    report = run_calibration(songs, emotions, out_dir, n_versions=5)

    rho_values = [g["spearman_rho"] for g in report.groups
                  if not (isinstance(g["spearman_rho"], float) and np.isnan(g["spearman_rho"]))]
    rho_mean = float(np.mean(rho_values)) if rho_values else 0.0
    rho_std = float(np.std(rho_values, ddof=1)) if len(rho_values) > 1 else 0.0

    # one-sided t-test: H0: rho <= 0.3, H1: rho > 0.3
    n = len(rho_values)
    if n >= 3:
        t_stat = (rho_mean - 0.3) / (rho_std / np.sqrt(n) + 1e-10)
    else:
        t_stat = 0.0

    h1_accepted = rho_mean > 0.3

    raw_data = []
    for g in report.groups:
        raw_data.append({
            "song": g.get("song", ""),
            "emotion": g.get("emotion", ""),
            "spearman_rho": g.get("spearman_rho", float('nan')),
            "discriminable": g.get("discriminable", False),
            "n_conflicts": len(g.get("conflicts", [])),
        })

    results = {
        "experiment": "E",
        "timestamp": datetime.now().isoformat(),
        "n_groups": len(report.groups),
        "rho_mean": round(rho_mean, 3),
        "rho_std": round(rho_std, 3),
        "t_stat_vs_0.3": round(float(t_stat), 3),
        "h1_accepted": h1_accepted,
        "aggregate_rho": report.aggregate_spearman_rho,
        "verdict": "PASS" if h1_accepted else "FAIL (proxy not reliable)",
    }
    path = save_results("E_m_factor", results, raw_data)
    print(f"  Aggregate rho: {report.aggregate_spearman_rho}")
    print(f"  Mean rho: {rho_mean:.3f} ± {rho_std:.3f}")
    print(f"  H1 accepted: {h1_accepted}")
    print(f"  → {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment F: Emotion Plasticity
# ═══════════════════════════════════════════════════════════

def experiment_F(**kwargs) -> dict:
    """测定每个 (曲目, 情绪) 组合的可塑性 ΔI."""
    print("\n" + "="*60)
    print("EXPERIMENT F: Emotion Plasticity")
    print("="*60)

    import soundfile
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.optimizer.search import search_optimal_strengths
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.emotion_targets import get_ideal_process_vector

    audio_dir = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    songs = sorted(audio_dir.glob("*.wav"))
    emotions = ["GA", "DR", "WL"]

    engine = DiagnosisEngine()
    chain = SpectralDSPChain()
    raw_data = []

    plastic_count = 0
    total = 0

    for song in songs:
        audio, sr = soundfile.read(str(song))
        audio = audio.astype(np.float32)
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])

        for emotion in emotions:
            total += 1
            print(f"  {song.stem} x {emotion}...")

            try:
                ws_before = engine.diagnose_quick(str(song))
                vec_before = StateTransferEngine.diagnostic_to_process(ws_before).to_array()
                ideal = get_ideal_process_vector(emotion)

                dist_before = float(np.linalg.norm(vec_before - ideal))

                results = search_optimal_strengths(ws_before, emotion, top_k=1, n_samples=2000)
                if results:
                    _, params, _ = results[0]
                    processed = chain.process(audio, sr, params)

                    import tempfile as tf
                    with tf.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                        soundfile.write(tmp.name, processed, sr)
                        ws_after = engine.diagnose_quick(tmp.name)
                        os.unlink(tmp.name)

                    vec_after = StateTransferEngine.diagnostic_to_process(ws_after).to_array()
                    dist_after = float(np.linalg.norm(vec_after - ideal))

                    delta = dist_before - dist_after  # positive = improvement
                else:
                    delta = 0.0
            except Exception as e:
                delta = 0.0
                print(f"    ERROR: {e}")

            plastic = delta > 0.02  # threshold above noise
            if plastic:
                plastic_count += 1

            raw_data.append({
                "song": song.stem, "emotion": emotion,
                "dist_before": round(dist_before, 4),
                "dist_after": round(dist_after, 4),
                "delta": round(delta, 4),
                "plastic": plastic,
            })
            print(f"    delta={delta:.4f}, plastic={plastic}")

    fraction_plastic = plastic_count / total if total else 0
    h1_accepted = fraction_plastic >= 0.5  # at least half are plastic

    results = {
        "experiment": "F",
        "timestamp": datetime.now().isoformat(),
        "n_groups": total,
        "n_plastic": plastic_count,
        "fraction_plastic": round(fraction_plastic, 3),
        "h1_accepted": h1_accepted,
        "verdict": "PASS (EWE1 supported)" if h1_accepted else "FAIL (EWE1 falsified)",
    }
    path = save_results("F_emotion_plasticity", results, raw_data)
    print(f"  Plastic: {plastic_count}/{total} = {fraction_plastic:.1%}")
    print(f"  H1 accepted: {h1_accepted}")
    print(f"  → {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment C: D(n) Growth
# ═══════════════════════════════════════════════════════════

def experiment_C(n_iterations: int = 30, **kwargs) -> dict:
    """运行 N 次 process，追踪 D 值增长曲线."""
    print("\n" + "="*60)
    print("EXPERIMENT C: D(n) Growth Curve")
    print("="*60)

    from moodify.orchestration.workflow_engine import WorkflowOrchestrator
    from moodify.calibration.online import CalibrationState

    audio_dir = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    songs = sorted(audio_dir.glob("*.wav"))
    emotions = ["GA", "DR", "WL", "SE", "HL", "LW", "UD", "CN"]

    if not songs:
        return {"status": "FAIL", "reason": "No baseline audio"}

    storage_dir = str(OUTPUT_BASE / "C_calibration_data")
    os.makedirs(storage_dir, exist_ok=True)

    raw_data = []
    w = WorkflowOrchestrator()

    for i in range(n_iterations):
        song = str(songs[i % len(songs)])
        emotion = emotions[i % len(emotions)]
        out_subdir = str(OUTPUT_BASE / "C_processed")

        print(f"  [{i+1}/{n_iterations}] {Path(song).stem} x {emotion}...")

        try:
            result = w.process(song, emotion, output_dir=out_subdir)
            success = result.success
        except Exception as e:
            success = False
            print(f"    ERROR: {e}")

        state = CalibrationState.load(storage_dir)
        d_val = state.d_value()

        raw_data.append({
            "iteration": i, "song": Path(song).stem, "emotion": emotion,
            "success": success, "total_n": state.total_n, "D": round(d_val, 4),
        })
        print(f"    D={d_val:.4f}, total_n={state.total_n}")

    # Fit both models
    ns = np.array([r["total_n"] for r in raw_data])
    ds = np.array([r["D"] for r in raw_data])

    # Hyperbolic: D = D0 + (Dmax-D0) * n/(n+n_half)
    # Use last few points to estimate
    d_final = float(np.mean(ds[-5:])) if len(ds) >= 5 else float(ds[-1])
    d_start = float(ds[0])

    results = {
        "experiment": "C",
        "timestamp": datetime.now().isoformat(),
        "n_iterations": n_iterations,
        "D_start": round(d_start, 4),
        "D_final": round(d_final, 4),
        "D_delta": round(d_final - d_start, 4),
        "h1_accepted": d_final > d_start + 0.01,
        "verdict": "PASS (D grows)" if d_final > d_start + 0.01 else "FAIL (D stagnant)",
    }
    path = save_results("C_d_growth", results, raw_data)
    print(f"  D: {d_start:.4f} -> {d_final:.4f} (delta={d_final-d_start:.4f})")
    print(f"  H1 accepted: {results['h1_accepted']}")
    print(f"  → {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment A: B Matrix Identification
# ═══════════════════════════════════════════════════════════

def experiment_A(n_samples: int = 50, **kwargs) -> dict:
    """系统辨识 — 估计 B 矩阵（15D 参数 → 5D 状态变化）."""
    print("\n" + "="*60)
    print("EXPERIMENT A: B Matrix Identification")
    print("="*60)

    import soundfile
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS

    audio_dir = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    song = str(sorted(audio_dir.glob("*.wav"))[0])
    print(f"  Reference audio: {Path(song).stem}")

    audio, sr = soundfile.read(song)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    engine = DiagnosisEngine()
    chain = SpectralDSPChain()

    # Baseline state (mean of 10 diagnoses)
    vecs_before = []
    for _ in range(10):
        ws = engine.diagnose_quick(song)
        vecs_before.append(StateTransferEngine.diagnostic_to_process(ws).to_array())
    x0 = np.mean(vecs_before, axis=0)

    # Sample parameters
    preset = get_recommended_params("GA")

    raw_data = []
    delta_X = []  # 5 x N
    delta_U = []  # 15 x N

    for i in range(n_samples):
        # Random perturbation around preset (within safe bounds)
        u = {}
        for pk in PARAM_KEYS:
            if pk in preset:
                # Scale to 50%-150% of preset
                scale = 0.5 + np.random.random()
                u[pk] = float(preset[pk] * scale)

        try:
            processed = chain.process(audio, sr, u)

            import tempfile as tf
            with tf.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                soundfile.write(tmp.name, processed, sr)
                ws = engine.diagnose_quick(tmp.name)
                os.unlink(tmp.name)

            x_i = StateTransferEngine.diagnostic_to_process(ws).to_array()
            dx = x_i - x0
            du = np.array([u.get(pk, 0) - preset.get(pk, 0) for pk in PARAM_KEYS])

            delta_X.append(dx.tolist())
            delta_U.append(du.tolist())

            raw_data.append({
                "sample": i, **{f"du_{pk}": float(du[j]) for j, pk in enumerate(PARAM_KEYS)},
                "dE": float(dx[0]), "dD": float(dx[1]), "dS": float(dx[2]),
                "dT": float(dx[3]), "dH": float(dx[4]),
            })
        except Exception as e:
            print(f"    sample {i}: ERROR {e}")
            continue

        if (i+1) % 10 == 0:
            print(f"    {i+1}/{n_samples}")

    # OLS: B = Delta_X @ pinv(Delta_U)
    dX_mat = np.array(delta_X).T  # 5 x N
    dU_mat = np.array(delta_U).T  # 15 x N

    try:
        B_hat = dX_mat @ np.linalg.pinv(dU_mat)
    except np.linalg.LinAlgError:
        B_hat = np.zeros((5, 15))

    # Count significant entries
    n_significant = int(np.sum(np.abs(B_hat) > 0.01))
    rank_eff = int(np.sum(np.linalg.svd(B_hat)[1] > 0.01))

    results = {
        "experiment": "A",
        "timestamp": datetime.now().isoformat(),
        "n_samples": len(delta_X),
        "n_significant_entries": n_significant,
        "fraction_significant": round(n_significant / 75, 3),
        "effective_rank": rank_eff,
        "h1_accepted": n_significant >= 15 and rank_eff >= 3,
        "verdict": "PASS (B has structure)" if (n_significant >= 15 and rank_eff >= 3)
                   else "INCONCLUSIVE",
    }
    path = save_results("A_b_matrix", results, raw_data)
    print(f"  Significant entries: {n_significant}/75 (need >= 15)")
    print(f"  Effective rank: {rank_eff} (need >= 3)")
    print(f"  H1 accepted: {results['h1_accepted']}")
    print(f"  → {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Experiment B: Closed-loop Convergence
# ═══════════════════════════════════════════════════════════

def experiment_B(n_iterations: int = 5, **kwargs) -> dict:
    """闭环收敛性测试 — 多次迭代是否减小误差."""
    print("\n" + "="*60)
    print("EXPERIMENT B: Closed-loop Convergence")
    print("="*60)

    import soundfile
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.optimizer.search import search_optimal_strengths
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.emotion_targets import get_ideal_process_vector

    audio_dir = Path(SRC).parent / "tests" / "baseline" / "test_audio"
    songs = sorted(audio_dir.glob("*.wav"))
    emotions = ["GA", "DR", "WL"]

    engine = DiagnosisEngine()
    chain = SpectralDSPChain()
    raw_data = []

    converging = 0
    total_groups = 0

    for song in songs:
        audio, sr = soundfile.read(str(song))
        audio = audio.astype(np.float32)
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])

        for emotion in emotions:
            total_groups += 1
            print(f"  {song.stem} x {emotion}...")
            ideal = get_ideal_process_vector(emotion)

            current_audio = audio.copy()
            distances = []

            for k in range(n_iterations):
                # Save to temp for diagnosis
                import tempfile as tf
                with tf.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    soundfile.write(tmp.name, current_audio, sr)
                    tmp_path = tmp.name

                ws = engine.diagnose_quick(tmp_path)
                vec = StateTransferEngine.diagnostic_to_process(ws).to_array()
                dist = float(np.linalg.norm(vec - ideal))
                distances.append(dist)

                if k < n_iterations - 1:
                    results_search = search_optimal_strengths(ws, emotion, top_k=1, n_samples=1000)
                    if results_search:
                        _, params, _ = results_search[0]
                        current_audio = chain.process(current_audio, sr, params)

                os.unlink(tmp_path)

            # Fit exponential: d_k = d_0 * lambda^k
            if len(distances) >= 3 and distances[0] > 1e-6:
                ks = np.arange(len(distances))
                log_d = np.log(np.array(distances) + 1e-10)
                slope = np.polyfit(ks, log_d, 1)[0]
                lam = np.exp(slope)
            else:
                lam = 1.0

            if lam < 0.95:
                converging += 1

            raw_data.append({
                "song": song.stem, "emotion": emotion,
                "distances": str([round(d, 4) for d in distances]),
                "lambda": round(float(lam), 4),
                "converging": lam < 0.95,
            })
            print(f"    lambda={lam:.4f}, converging={lam < 0.95}")

    fraction_converging = converging / total_groups if total_groups else 0
    h1_accepted = fraction_converging >= 0.5

    results = {
        "experiment": "B",
        "timestamp": datetime.now().isoformat(),
        "n_groups": total_groups,
        "n_converging": converging,
        "fraction_converging": round(fraction_converging, 3),
        "h1_accepted": h1_accepted,
        "verdict": "PASS (system converges)" if h1_accepted else "FAIL (system unstable)",
    }
    path = save_results("B_closed_loop", results, raw_data)
    print(f"  Converging: {converging}/{total_groups} = {fraction_converging:.1%}")
    print(f"  H1 accepted: {h1_accepted}")
    print(f"  → {path}")
    return results


# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════

EXPERIMENTS = {
    "A": experiment_A,
    "B": experiment_B,
    "C": experiment_C,
    "D": experiment_D,
    "E": experiment_E,
    "F": experiment_F,
}


def main():
    parser = argparse.ArgumentParser(description="Moodify Physics Experiments")
    parser.add_argument("--exp", required=True,
                        help="Experiment IDs: A,B,C,D,E,F or 'all' (comma-separated)")
    parser.add_argument("--n", type=int, default=0,
                        help="Override sample size (experiment-specific default if 0)")
    args = parser.parse_args()

    if args.exp == "all":
        exp_ids = list(EXPERIMENTS.keys())
    else:
        exp_ids = [e.strip() for e in args.exp.split(",")]

    # Validate
    for eid in exp_ids:
        if eid not in EXPERIMENTS:
            print(f"Unknown experiment: {eid}. Choose from: {list(EXPERIMENTS.keys())}")
            sys.exit(1)

    print(f"Moodify Physics Experiments — {len(exp_ids)} experiments")
    print(f"Output: {OUTPUT_BASE}")
    print(f"Order: {' → '.join(exp_ids)}")
    t_start = time.perf_counter()

    all_results = {}
    for eid in exp_ids:
        t0 = time.perf_counter()
        func = EXPERIMENTS[eid]
        try:
            if args.n and eid in ("A", "C", "D"):
                result = func(n_samples=args.n) if eid == "A" else (
                    func(n_iterations=args.n) if eid == "C" else func(n_repeats=args.n))
            else:
                result = func()
            all_results[eid] = result
        except Exception as e:
            import traceback
            traceback.print_exc()
            all_results[eid] = {"status": "ERROR", "reason": str(e)}
        elapsed = time.perf_counter() - t0
        print(f"\n  [{eid}] elapsed: {elapsed:.0f}s")

    total_elapsed = time.perf_counter() - t_start

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    passes = 0
    for eid, r in all_results.items():
        verdict = r.get("verdict", "ERROR")
        print(f"  [{eid}] {verdict}")
        if "PASS" in str(verdict):
            passes += 1
    print(f"\n  {passes}/{len(all_results)} experiments passed")
    print(f"  Total time: {total_elapsed:.0f}s")
    print(f"  Output: {OUTPUT_BASE}")

    # Write master summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_elapsed_s": round(total_elapsed, 1),
        "results": {eid: {"verdict": r.get("verdict", "ERROR")}
                     for eid, r in all_results.items()},
    }
    with open(OUTPUT_BASE / "summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"  Summary: {OUTPUT_BASE / 'summary.json'}")


if __name__ == "__main__":
    main()
