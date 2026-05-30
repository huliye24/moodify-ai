"""B Matrix Identification — 并行版 (利用全部 16 核).

对 8 个情绪独立估计 5×15 输入矩阵 B，使用多进程并行。
16核加速比: 8-12× (8情绪 × 进程池)

用法:
  python -m moodify.physics.b_matrix_parallel --samples 500 --workers 16
  python -m moodify.physics.b_matrix_parallel --emotions GA,DR,WL --samples 200
"""

import os, sys, json, time, argparse, multiprocessing as mp
from pathlib import Path
from datetime import datetime
import numpy as np

SRC = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, SRC)
OUTPUT_BASE = Path(SRC).parent / "outputs" / "b_matrix"


def _worker_init(audio_path, emotion, n_samples):
    """Each worker loads audio once, then processes n_samples parameter sets."""
    import soundfile
    audio, sr = soundfile.read(audio_path)
    audio = audio.astype(np.float32)
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])
    return audio, sr, emotion, n_samples


def _process_batch(args):
    """Process a batch of parameter sets. Called by worker processes."""
    audio, sr, emotion, param_batch, song_path = args

    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.processing.spectral_chain import SpectralDSPChain
    from moodify.orchestration.state_transfer import StateTransferEngine
    from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS
    from moodify.safety.bounds import HARD_BOUNDS
    import tempfile as tf

    engine = DiagnosisEngine()
    chain = SpectralDSPChain()
    preset = get_recommended_params(emotion)

    # Baseline state (single diagnosis, shared across batches)
    ws_base = engine.diagnose_quick(song_path)
    x0 = StateTransferEngine.diagnostic_to_process(ws_base).to_array()

    results = []
    for params in param_batch:
        try:
            processed = chain.process(audio, sr, params)
            with tf.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                soundfile.write(tmp.name, processed, sr)
                ws_after = engine.diagnose_quick(tmp.name)
                os.unlink(tmp.name)

            x_i = StateTransferEngine.diagnostic_to_process(ws_after).to_array()
            dx = x_i - x0
            du = np.array([params.get(pk, 0) - preset.get(pk, 0) for pk in PARAM_KEYS])

            results.append({
                "dx": dx.tolist(),
                "du": du.tolist(),
                "status": "ok",
            })
        except Exception as e:
            reason = "unknown"
            msg = str(e)[:100]
            if "No such file" in msg or "not found" in msg.lower():
                reason = "file_not_found"
            elif "too short" in msg.lower() or "length" in msg.lower():
                reason = "audio_too_short"
            elif "decode" in msg.lower() or "format" in msg.lower() or "corrupt" in msg.lower():
                reason = "decode_error"
            elif "memory" in msg.lower() or "allocation" in msg.lower():
                reason = "out_of_memory"
            results.append({"dx": None, "du": None, "status": f"{reason}: {msg[:80]}"})

    return results


def _generate_params(emotion, n_samples):
    """Generate random parameter sets within HARD_BOUNDS, centered on preset."""
    from moodify.knowledge.craft_chains import get_recommended_params, PARAM_KEYS
    from moodify.safety.bounds import HARD_BOUNDS

    preset = get_recommended_params(emotion)
    params_list = []

    for _ in range(n_samples):
        u = {}
        for pk in PARAM_KEYS:
            if pk in preset and pk in HARD_BOUNDS:
                lo, hi = HARD_BOUNDS[pk]
                # Constrain to 20%-250% of preset (wider than before for better coverage)
                lo = max(lo, preset[pk] * 0.2)
                hi = min(hi, preset[pk] * 2.5)
                if hi <= lo:
                    hi = lo + abs(preset[pk]) * 0.5 + 1e-6
                u[pk] = float(lo + np.random.random() * (hi - lo))
        params_list.append(u)

    return params_list


def identify_b_matrix(emotion, audio_path, n_samples, n_workers):
    """Identify B matrix for one emotion using parallel workers."""
    from moodify.knowledge.craft_chains import PARAM_KEYS
    import soundfile

    print(f"\n  [{emotion}] Generating {n_samples} parameter sets...")
    params_list = _generate_params(emotion, n_samples)

    try:
        audio, sr = soundfile.read(audio_path)
        audio = audio.astype(np.float32)
        if audio.ndim == 1:
            audio = np.column_stack([audio, audio])
        if len(audio) < sr * 3:
            return {"emotion": emotion, "error": "Audio too short (< 3s)",
                    "n_failed": n_samples, "failure_reasons": {"audio_too_short": n_samples}}
    except FileNotFoundError:
        return {"emotion": emotion, "error": f"Audio file not found: {audio_path}",
                "n_failed": n_samples, "failure_reasons": {"file_not_found": n_samples}}
    except Exception as e:
        return {"emotion": emotion, "error": f"Audio load failed: {e}",
                "n_failed": n_samples, "failure_reasons": {"decode_error": n_samples}}

    # Split into batches for parallel processing
    batch_size = max(1, n_samples // n_workers)
    batches = []
    for i in range(0, n_samples, batch_size):
        batches.append((audio, sr, emotion, params_list[i:i+batch_size], audio_path))

    print(f"  [{emotion}] Processing {n_samples} samples with {len(batches)} batches on {n_workers} workers...")
    t0 = time.perf_counter()

    with mp.Pool(processes=n_workers) as pool:
        all_batch_results = pool.map(_process_batch, batches)

    # Flatten results
    all_results = []
    for batch in all_batch_results:
        all_results.extend(batch)

    elapsed = time.perf_counter() - t0

    # Extract valid results and categorize failures
    valid = [r for r in all_results if r["status"] == "ok"]
    failure_reasons = {}
    for r in all_results:
        if r["status"] != "ok":
            reason = r["status"].split(":")[0] if r["status"] else "unknown"
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
    n_failed = len(all_results) - len(valid)

    if len(valid) < 15:
        return {"emotion": emotion, "error": f"Only {len(valid)} valid samples", "n_failed": n_failed}

    # Build matrices
    dX = np.array([r["dx"] for r in valid]).T  # 5 x N
    dU = np.array([r["du"] for r in valid]).T  # 15 x N

    # OLS: B = dX @ pinv(dU)
    try:
        B_hat = dX @ np.linalg.pinv(dU)
    except np.linalg.LinAlgError:
        return {"emotion": emotion, "error": "SVD did not converge"}

    # Analysis
    n_sig = int(np.sum(np.abs(B_hat) > 0.005))
    U, s, Vt = np.linalg.svd(B_hat, full_matrices=False)
    rank_eff = int(np.sum(s > 0.01))

    # Per-dimension sensitivity
    dim_names = ["E", "D", "S", "T", "H"]
    dim_sensitivity = {}
    for j, dim in enumerate(dim_names):
        row = B_hat[j]
        top_indices = np.argsort(np.abs(row))[-3:][::-1]
        dim_sensitivity[dim] = {
            f"top_param_{i+1}": PARAM_KEYS[idx]
            for i, idx in enumerate(top_indices)
        }
        dim_sensitivity[dim]["top_values"] = [round(float(row[idx]), 5) for idx in top_indices]

    # Reconstruction error
    dX_pred = B_hat @ dU
    recon_error = float(np.mean((dX - dX_pred)**2))
    r2_per_dim = []
    for j in range(5):
        ss_res = np.sum((dX[j] - dX_pred[j])**2)
        ss_tot = np.sum((dX[j] - np.mean(dX[j]))**2)
        r2 = 1 - ss_res / (ss_tot + 1e-10)
        r2_per_dim.append(round(float(r2), 3))

    return {
        "emotion": emotion,
        "n_samples": n_samples,
        "n_valid": len(valid),
        "n_failed": n_failed,
        "failure_reasons": failure_reasons,
        "significant_entries": n_sig,
        "fraction_significant": round(n_sig / 75, 3),
        "effective_rank": rank_eff,
        "reconstruction_error": round(recon_error, 6),
        "r2_per_dimension": {dim_names[i]: r2_per_dim[i] for i in range(5)},
        "elapsed_s": round(elapsed, 1),
        "samples_per_second": round(len(valid) / elapsed, 1),
        "dim_sensitivity": dim_sensitivity,
    }


def main():
    parser = argparse.ArgumentParser(description="Parallel B Matrix Identification")
    parser.add_argument("--emotions", default="GA,DR,WL,SE,HL,LW,UD,CN",
                        help="Comma-separated emotion codes")
    parser.add_argument("--samples", type=int, default=500,
                        help="Samples per emotion (default: 500)")
    parser.add_argument("--workers", type=int, default=None,
                        help="Parallel workers (default: cpu_count)")
    parser.add_argument("--audio", default=None,
                        help="Audio file path (default: piano.wav from baseline)")
    args = parser.parse_args()

    emotions = [e.strip() for e in args.emotions.split(",")]
    n_workers = args.workers or min(mp.cpu_count(), len(emotions) * 2)
    audio_path = args.audio or str(Path(SRC).parent / "tests" / "baseline" / "test_audio" / "piano.wav")

    print("="*60)
    print("PARALLEL B MATRIX IDENTIFICATION")
    print("="*60)
    print(f"  Server: {mp.cpu_count()} cores")
    print(f"  Emotions: {emotions}")
    print(f"  Samples per emotion: {args.samples}")
    print(f"  Total DSP ops: {len(emotions) * args.samples}")
    print(f"  Workers: {n_workers}")
    print(f"  Audio: {audio_path}")
    print(f"  Output: {OUTPUT_BASE}")
    print()

    t_start = time.perf_counter()
    all_results = {}

    # Process emotions sequentially (each emotion uses all workers internally)
    for emotion in emotions:
        result = identify_b_matrix(emotion, audio_path, args.samples, n_workers)
        all_results[emotion] = result
        status = "OK" if "error" not in result else "FAIL"
        valid = result.get("n_valid", 0)
        rank = result.get("effective_rank", 0)
        elapsed = result.get("elapsed_s", 0)
        print(f"  [{status}] {emotion}: {valid} valid, rank={rank}, "
              f"{result.get('samples_per_second', 0):.0f} samp/s, {elapsed:.0f}s")

    total_time = time.perf_counter() - t_start

    # Aggregate report
    valid_emotions = {e: r for e, r in all_results.items() if "error" not in r}
    ranks = [r["effective_rank"] for r in valid_emotions.values()]
    avg_rank = float(np.mean(ranks)) if ranks else 0

    report = {
        "timestamp": datetime.now().isoformat(),
        "server_cores": mp.cpu_count(),
        "workers_used": n_workers,
        "total_samples": sum(r.get("n_valid", 0) for r in all_results.values()),
        "total_elapsed_s": round(total_time, 1),
        "avg_effective_rank": round(avg_rank, 1),
        "emotions": all_results,
    }

    OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_BASE / "b_matrix_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n{'='*60}")
    print(f"COMPLETE: {total_time:.0f}s")
    print(f"  Avg rank: {avg_rank:.1f}")
    print(f"  Total valid samples: {report['total_samples']}")
    print(f"  Report: {report_path}")
    print(f"{'='*60}")

    return report


if __name__ == "__main__":
    # Required for multiprocessing on some platforms
    mp.freeze_support()
    main()
