"""check_regression.py — 退化检测 (SPEC-007).

用法:
  cd moodify-core-package
  python tests/baseline/check_regression.py

对比当前 baseline_metrics.json 和上次运行的基准数据, 检测退化。
"""

import json, sys
from pathlib import Path

BASELINE_FILE = Path(__file__).resolve().parent / "baseline_metrics.json"

REGRESSION_RULES = [
    # 硬退化 — FAIL
    {"metric": "status",         "rule": "new != 'pass' and old == 'pass'",
     "action": "fail", "msg": "previously passing test now fails"},
    {"metric": "whs_after",      "rule": "delta < -5",
     "action": "fail", "msg": "WHS dropped >5 points"},
    {"metric": "elapsed_s",      "rule": "delta_pct > 100 and new > 5.0",
     "action": "fail", "msg": "diagnosis time >2x slower (>5s)"},
    # 软退化 — WARN
    {"metric": "whs_after",      "rule": "delta < -2",
     "action": "warn", "msg": "WHS dropped 2-5 points"},
    {"metric": "eds",            "rule": "delta < -10",
     "action": "warn", "msg": "EDS dropped >10 points"},
    {"metric": "elapsed_s",      "rule": "delta_pct > 50 and new > old",
     "action": "warn", "msg": "search time >1.5x slower"},
]


def load_baseline(path: Path) -> dict[str, dict]:
    """Return {test_name: entry} dict."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {e["name"]: e for e in data}


def check_one(name: str, old: dict, new: dict) -> list[dict]:
    findings = []
    for rule in REGRESSION_RULES:
        metric = rule["metric"]
        old_val = old.get(metric)
        new_val = new.get(metric)

        if old_val is None or new_val is None:
            continue

        if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
            delta = new_val - old_val
            delta_pct = (delta / abs(old_val)) * 100 if old_val != 0 else 0

            if rule["rule"] == "delta < -5":
                triggered = delta < -5
            elif rule["rule"] == "delta < -2":
                triggered = delta < -2
            elif rule["rule"] == "delta < -10":
                triggered = delta < -10
            elif rule["rule"] == "delta_pct > 100 and new > 5.0":
                triggered = (delta_pct > 100) and (new_val > 5.0)
            elif rule["rule"] == "delta_pct > 50 and new > old":
                triggered = (delta_pct > 50) and (new_val > old_val)
            else:
                triggered = False
        elif rule["rule"] == "new != 'pass' and old == 'pass'":
            triggered = (new_val != "pass") and (old_val == "pass")
        else:
            continue

        if triggered:
            findings.append({
                "test": name,
                "action": rule["action"],
                "msg": rule["msg"],
                "old": old_val,
                "new": new_val,
            })
    return findings


def main():
    if not BASELINE_FILE.exists():
        print("No baseline_metrics.json found. Run run_baseline.py first to generate it.")
        return 1

    current = load_baseline(BASELINE_FILE)

    # We compare against the same file for now (in a real CI setup, this would
    # compare against a committed baseline). The value is in detecting the
    # structure change.
    print("Regression Check")
    print(f"  Reference: {BASELINE_FILE}")
    print(f"  Tests in baseline: {len(current)}")
    print()

    # Re-run baseline to get current state for comparison
    import subprocess
    run_py = Path(__file__).resolve().parent / "run_baseline.py"
    tmp_file = BASELINE_FILE.parent / ".baseline_current.json"
    result = subprocess.run(
        [sys.executable, str(run_py)],
        capture_output=True, text=True, cwd=str(BASELINE_FILE.parent.parent.parent))

    if result.returncode != 0:
        print("WARNING: re-run failed — cannot compare")
        print(result.stderr[-500:])
        return 1

    # The re-run saved baseline_metrics.json; read current and compare with prior
    if not tmp_file.exists():
        # Re-read the freshly-saved baseline
        new_data = load_baseline(BASELINE_FILE)
    else:
        new_data = load_baseline(tmp_file)

    all_findings = []
    for name, old_entry in current.items():
        new_entry = new_data.get(name)
        if new_entry is None:
            all_findings.append({
                "test": name, "action": "warn",
                "msg": "test removed from baseline",
            })
            continue
        findings = check_one(name, old_entry, new_entry)
        all_findings.extend(findings)

    if not all_findings:
        print("  No regression detected.")
        return 0

    fails = [f for f in all_findings if f["action"] == "fail"]
    warns = [f for f in all_findings if f["action"] == "warn"]

    for f in fails:
        print(f"  FAIL [{f['test']}] {f['msg']}: {f.get('old')} → {f.get('new')}")
    for f in warns:
        print(f"  WARN [{f['test']}] {f['msg']}: {f.get('old')} → {f.get('new')}")

    print(f"\n  {len(fails)} failures, {len(warns)} warnings")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
