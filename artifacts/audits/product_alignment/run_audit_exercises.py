"""Isolated runtime exercises for DSK-MFY-PRODUCT-ALIGNMENT-001.

Uses only a generated sine-wave fixture and writes only below this audit folder.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
HERE = SCRIPT_DIR / "codex"
CORE = ROOT / "moodify-core-package"
BRIDGE = ROOT / "moodify-bridge"
WORK = HERE / "runtime"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wav(path: Path, seconds: float = 0.25, hz: float = 440.0) -> None:
    import math
    rate = 16000
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1); out.setsampwidth(2); out.setframerate(rate)
        for n in range(int(rate * seconds)):
            out.writeframesraw(struct.pack("<h", int(8000 * math.sin(2 * math.pi * hz * n / rate))))


def run(args: list[str], env: dict[str, str] | None = None) -> dict:
    cp = subprocess.run(args, cwd=CORE, text=True, capture_output=True, env=env)
    return {"argv": args, "exit_code": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}


def cli(*args: str) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(CORE / "src")
    return run([sys.executable, "-m", "moodify", *args], env)


def parse_stdout(result: dict) -> dict:
    try:
        return json.loads(result["stdout"])
    except Exception:
        return {}


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__), HERE / "run_audit_exercises.py")
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    source = WORK / "source.wav"
    wav(source)
    initial_hash = sha(source)
    project = WORK / "project"
    results: dict[str, object] = {"fixture": {"path": str(source), "sha256": initial_hash}}

    results["project_init"] = cli("project", "init", str(project), "--title", "audit")
    imported = cli("asset", "import", str(project), str(source))
    results["source_intake"] = imported
    asset_id = parse_stdout(imported).get("asset", {}).get("asset_id", "")

    # Positive CLI-v2 trace as actually supported (not as target architecture expects).
    dry = cli("plan", "create", str(project),
              "--intent", '{"gain_db":-1}', "--dry-run")
    results["dry_plan"] = dry
    dry_id = parse_stdout(dry).get("plan", {}).get("plan_id", "")
    results["dry_plan_apply_attempt"] = cli("run", "execute", str(project),
                                             "--plan-id", dry_id,
                                             "--output-dir", str(WORK / "dry_apply"))

    plan = cli("plan", "create", str(project),
               "--intent", '{"gain_db":-1}')
    results["executable_plan_without_spec"] = plan
    plan_id = parse_stdout(plan).get("plan", {}).get("plan_id", "")
    applied = cli("run", "execute", str(project), "--plan-id", plan_id,
                  "--output-dir", str(WORK / "unapproved_apply"))
    results["unapproved_apply"] = applied
    run_id = parse_stdout(applied).get("run_id", "")
    results["verify_after_success_status"] = cli("run", "verify", str(project),
                                                  "--run-id", run_id)

    # Source mutation after planning: expected to be caught in cli-v2.
    plan2 = cli("plan", "create", str(project),
                "--intent", '{"gain_db":-2}')
    plan2_id = parse_stdout(plan2).get("plan", {}).get("plan_id", "")
    with source.open("ab") as fh:
        fh.write(b"AUDIT_MUTATION")
    results["source_changed_apply"] = cli("run", "execute", str(project),
                                           "--plan-id", plan2_id,
                                           "--output-dir", str(WORK / "changed_source"))
    results["source_hashes"] = {"initial": initial_hash, "mutated": sha(source)}

    # Retry: same output is rejected; a new output creates a duplicate run.
    results["retry_same_output"] = cli("run", "execute", str(project),
                                        "--plan-id", plan_id,
                                        "--output-dir", str(WORK / "unapproved_apply"))
    # Restore exact source so new-output retry can execute.
    wav(source)
    results["retry_new_output"] = cli("run", "execute", str(project),
                                       "--plan-id", plan_id,
                                       "--output-dir", str(WORK / "duplicate_apply"))
    results["malformed_json"] = cli("plan", "create", str(project),
                                     "--intent", "{bad")

    # OnePointSpec validation and five conflict probes.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BRIDGE / "src")
    conflict_code = r'''
import json, sys, types
# services imports optional parquet modules at module load; these exercises call
# only detect_conflicts, so isolate that function from an unavailable pyarrow.
pa=types.ModuleType("pyarrow"); pa.__version__="audit-stub-not-used"
pq=types.ModuleType("pyarrow.parquet"); pa.parquet=pq
sys.modules.setdefault("pyarrow",pa); sys.modules.setdefault("pyarrow.parquet",pq)
from moodify_bridge.schemas import OnePointSpec
from moodify_bridge.services import detect_conflicts
base={"source":"fixture.wav","case_id":"audit","essence":"intimate soft vocal","human_owner":"human","must_preserve":["vocal intimacy","dynamic range","mono compatibility","soft texture"],"must_avoid":["sibilance","clipping"],"desired_change":"warmer"}
out={}
try:
    OnePointSpec.model_validate({k:v for k,v in base.items() if k!="must_preserve"})
    out["omit_must_preserve"]="accepted"
except Exception as e: out["omit_must_preserve"]="blocked: "+type(e).__name__
cases={
 "warmth_vs_intimacy":"warm saturated vocal",
 "loudness_vs_dynamics":"increase loudness and compressed impact",
 "width_vs_mono":"wide stereo image",
 "hf_vs_sibilance":"bright high frequency enhancement",
 "transient_vs_soft":"transient enhancement"
}
for key,desired in cases.items():
    item=dict(base); item["desired_change"]=desired
    out[key]=detect_conflicts(OnePointSpec.model_validate(item))
print(json.dumps(out,ensure_ascii=False))
'''
    results["constraint_exercises"] = run([sys.executable, "-c", conflict_code], env)

    # Evidence aggregator is able to package missing inputs with limitations.
    evidence_code = f'''
import json
from pathlib import Path
from moodify.app.evidence import aggregate_evidence, write_evidence_bundle
b=aggregate_evidence("audit-missing", {{"output":Path(r"{WORK / 'does-not-exist.wav'}")}})
p=write_evidence_bundle(b, Path(r"{WORK / 'missing_evidence_bundle'}"))
print(p.read_text(encoding="utf-8"))
'''
    results["evidence_missing_input"] = run([sys.executable, "-c", evidence_code], {
        **os.environ, "PYTHONPATH": str(CORE / "src")})

    # Product-level engine identity/version is absent from CLI-v2 plans.
    pdata = json.loads((project / "project.json").read_text(encoding="utf-8"))
    chosen = next(p for p in pdata["plans"] if p["plan_id"] == plan_id)
    results["serialized_plan_fields"] = sorted(chosen.keys())
    results["noninteractive"] = {"stdin_isatty": sys.stdin.isatty(), "cli_completed": applied["exit_code"] == 0}
    (HERE / "runtime_exercises.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
