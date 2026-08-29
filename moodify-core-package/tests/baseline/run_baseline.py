"""run_baseline.py — 自动化基准测试主脚本 (SPEC-007).

用法:
  cd moodify-core-package
  python tests/baseline/run_baseline.py

输出: baseline_metrics.json (首次运行生成基准)
"""

import json
import importlib
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = str(ROOT / "src")
sys.path.insert(0, SRC)

AUDIO_DIR = Path(__file__).resolve().parent / "test_audio"
OUTPUT_DIR = ROOT / "outputs" / "baseline_test"
BASELINE_FILE = Path(__file__).resolve().parent / "baseline_metrics.json"


def find_audio(name_hint: str) -> str:
    """Find an audio file by name hint, returns path or raises."""
    for f in AUDIO_DIR.glob("*.wav"):
        if name_hint in f.stem:
            return str(f)
    wavs = list(AUDIO_DIR.glob("*.wav"))
    if wavs:
        return str(wavs[0])
    raise FileNotFoundError(f"No .wav files in {AUDIO_DIR}")


# ═══════════════════════════════════════════════════════════════
#  导入测试
# ═══════════════════════════════════════════════════════════════

def test_import_core():
    importlib.import_module("moodify.diagnosis.engine")
    importlib.import_module("moodify.processing.spectral_chain")
    importlib.import_module("moodify.orchestration.workflow_engine")
    return {"status": "pass"}


def test_import_optimizer():
    importlib.import_module("moodify.optimizer.search")
    importlib.import_module("moodify.optimizer.calibrate")
    return {"status": "pass"}


def test_import_llm():
    importlib.import_module("moodify.llm.client")
    importlib.import_module("moodify.llm.prompt_assembler")
    importlib.import_module("moodify.llm.offline_fallback")
    return {"status": "pass"}


def test_import_memory():
    importlib.import_module("moodify.memory.history")
    return {"status": "pass"}


# ═══════════════════════════════════════════════════════════════
#  Fallback 测试
# ═══════════════════════════════════════════════════════════════

def test_fallback_no_api_key():
    """DEEPSEEK_API_KEY 未设置时, 流程不崩溃."""
    key_backup = os.environ.pop("DEEPSEEK_API_KEY", None)
    try:
        from moodify.orchestration.workflow_engine import WorkflowOrchestrator
        w = WorkflowOrchestrator()
        audio_path = find_audio("piano")
        os.makedirs(str(OUTPUT_DIR), exist_ok=True)
        result = w.process(audio_path, "GA", output_dir=str(OUTPUT_DIR))
        return {"status": "pass" if result.success else "fail",
                "reason": str(result.risk_level)}
    finally:
        if key_backup is not None:
            os.environ["DEEPSEEK_API_KEY"] = key_backup


def test_fallback_search():
    """搜索回退 — 5D 搜索不可用时使用工艺卡保底."""
    from moodify.knowledge.craft_chains import get_recommended_params
    from moodify.knowledge.emotion_targets import resolve_emotion, KEY_TO_CODE

    code = "GA"
    try:
        key = resolve_emotion("GA")
        code = KEY_TO_CODE.get(key, "GA")
    except Exception:
        pass

    params = get_recommended_params(code)
    return {"status": "pass" if len(params) == 15 else "fail",
            "params_count": len(params)}


def test_fallback_preset():
    """所有 8 种情绪都有可用的预设参数."""
    from moodify.knowledge.craft_chains import get_recommended_params

    codes = ["GA", "SE", "UD", "LW", "HL", "DR", "WL", "CN"]
    missing = []
    for code in codes:
        try:
            params = get_recommended_params(code)
            if len(params) < 15:
                missing.append(code)
        except Exception:
            missing.append(code)

    return {"status": "fail" if missing else "pass",
            "missing": missing}


# ═══════════════════════════════════════════════════════════════
#  处理质量测试
# ═══════════════════════════════════════════════════════════════

def test_quality(audio_path: str) -> dict:
    """处理后的 WHS >= 处理前 WHS - 2."""
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.diagnosis.defect_classifier import DefectClassifier
    from moodify.diagnosis.health_scorer import HealthScorer
    from moodify.orchestration.workflow_engine import WorkflowOrchestrator

    os.makedirs(str(OUTPUT_DIR), exist_ok=True)

    engine = DiagnosisEngine()
    ws_before = engine.diagnose_quick(audio_path)

    w = WorkflowOrchestrator()
    result = w.process(audio_path, "GA", output_dir=str(OUTPUT_DIR))

    if not result.success or not result.output_path:
        return {"status": "fail", "reason": "Processing failed"}

    ws_after = engine.diagnose_quick(result.output_path)

    classifier = DefectClassifier()
    scorer = HealthScorer()
    defects_before = classifier.classify(ws_before, "GA")
    defects_after = classifier.classify(ws_after, "GA")
    whs_before = scorer.compute_whs(ws_before, defects_before)["WHS"]
    whs_after = scorer.compute_whs(ws_after, defects_after)["WHS"]

    if whs_after < whs_before - 2:
        return {"status": "warn", "whs_before": round(whs_before, 1),
                "whs_after": round(whs_after, 1)}
    return {"status": "pass", "whs_before": round(whs_before, 1),
            "whs_after": round(whs_after, 1)}


# ═══════════════════════════════════════════════════════════════
#  性能测试
# ═══════════════════════════════════════════════════════════════

def test_perf_diagnosis():
    """诊断时间 < 5s."""
    from moodify.diagnosis.engine import DiagnosisEngine

    audio_files = sorted(AUDIO_DIR.glob("*.wav"), key=lambda f: f.stat().st_size)
    if not audio_files:
        return {"status": "skip", "reason": "No audio files"}
    longest = str(audio_files[-1])

    engine = DiagnosisEngine()
    t0 = time.perf_counter()
    engine.diagnose_quick(longest)
    elapsed = time.perf_counter() - t0
    return {"status": "pass" if elapsed < 5.0 else "fail",
            "elapsed_s": round(elapsed, 2)}


def test_perf_search():
    """搜索时间 < 3s (2000 LHS 候选代理评估)."""
    from moodify.diagnosis.engine import DiagnosisEngine
    from moodify.optimizer.search import search_optimal_strengths

    audio_path = find_audio("piano")
    engine = DiagnosisEngine()
    ws = engine.diagnose_quick(audio_path)
    t0 = time.perf_counter()
    search_optimal_strengths(ws, "GA", top_k=3, n_samples=2000)
    elapsed = time.perf_counter() - t0
    return {"status": "pass" if elapsed < 3.0 else "warn",
            "elapsed_s": round(elapsed, 2)}


# ═══════════════════════════════════════════════════════════════
#  主运行
# ═══════════════════════════════════════════════════════════════

TESTS = [
    {"name": "import_core",       "func": test_import_core},
    {"name": "import_optimizer",  "func": test_import_optimizer},
    {"name": "import_llm",        "func": test_import_llm},
    {"name": "import_memory",     "func": test_import_memory},
    {"name": "fallback_no_api_key","func": test_fallback_no_api_key},
    {"name": "fallback_search",   "func": test_fallback_search},
    {"name": "fallback_preset",   "func": test_fallback_preset},
    {"name": "perf_diagnosis",    "func": test_perf_diagnosis},
    {"name": "perf_search",       "func": test_perf_search},
]


def run_all():
    results = []
    for test in TESTS:
        t0 = time.perf_counter()
        try:
            r = test["func"]()
        except Exception as e:
            r = {"status": "fail", "reason": str(e)[:200]}
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        entry = {"name": test["name"], **r, "elapsed_ms": elapsed_ms}
        results.append(entry)
        status = entry.get("status", "?")
        print(f"  [{status:4s}] {test['name']:<28s} ({elapsed_ms:5d}ms)")

    # Quality tests — one per audio file
    for af in sorted(AUDIO_DIR.glob("*.wav")):
        name = f"quality_wav_{af.stem}"
        t0 = time.perf_counter()
        try:
            r = test_quality(str(af))
        except Exception as e:
            r = {"status": "fail", "reason": str(e)[:200]}
        elapsed_ms = round((time.perf_counter() - t0) * 1000)
        entry = {"name": name, **r, "elapsed_ms": elapsed_ms}
        results.append(entry)
        status = entry.get("status", "?")
        print(f"  [{status:4s}] {name:<28s} ({elapsed_ms:5d}ms)")

    return results


def main():
    print(f"Baseline Suite — {len(TESTS)} import/fallback/perf tests + audio quality tests")
    print(f"Audio dir: {AUDIO_DIR}")
    print()

    results = run_all()

    # Save baseline
    BASELINE_FILE.write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nBaseline saved → {BASELINE_FILE}")

    # Summary
    passes = sum(1 for r in results if r.get("status") == "pass")
    warns = sum(1 for r in results if r.get("status") == "warn")
    fails = sum(1 for r in results if r.get("status") == "fail")
    print(f"Summary: {passes} pass, {warns} warn, {fails} fail / {len(results)} total")

    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
