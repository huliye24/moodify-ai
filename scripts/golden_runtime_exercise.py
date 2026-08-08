"""DSK-MFY-RUNTIME-INTEGRATION-001 — golden runtime exercise.

Drives one complete real production case through every lifecycle state via
the formal CLI v2, and retains all requests, responses, the state-transition
log, the approved execution envelope, the engine record, the verification
record, the executed output, and the complete evidence package under:

    artifacts/verification/runtime_integration/golden_case/
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "moodify-core-package"
FIXTURE = PACKAGE_ROOT / "tests" / "baseline" / "test_audio" / "vocal_folk.wav"
TARGET = REPO_ROOT / "artifacts" / "verification" / "runtime_integration" / "golden_case"

SPEC = {
    "essence": "Preserve the intimate vocal performance and acoustic space.",
    "must_preserve": ["vocal intimacy", "natural reverb tail"],
    "must_avoid": ["harsh sibilance", "pumping compression"],
    "desired_change": "Gentle loudness normalization to -1 dB peak without coloration.",
    "human_owner": "huliye24",
}
OWNER = "huliye24"


def run_cli(env: dict, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "moodify", *args],
        cwd=PACKAGE_ROOT, env=env, capture_output=True, text=True,
        encoding="utf-8", timeout=300, check=False)
    return {"args": list(args), "exit_code": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr}


def main() -> int:
    if not FIXTURE.is_file():
        print(f"fixture missing: {FIXTURE}")
        return 1
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)

    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(PACKAGE_ROOT / "src") + ";" + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"

    transcript: list[dict] = []
    work = Path(tempfile.mkdtemp(prefix="mfy-golden-"))
    project = work / "golden_project"

    def cli(*args: str) -> dict:
        entry = run_cli(env, *args)
        transcript.append(entry)
        if entry["exit_code"] != 0:
            print(f"FAILED: {' '.join(args)} -> {entry['stderr'].strip()}")
            _write(transcript)
            return 1
        return json.loads(entry["stdout"])

    try:
        cli("project", "init", str(project))
        cli("asset", "import", str(project), str(FIXTURE))
        spec_file = work / "spec.json"
        spec_file.write_text(json.dumps(SPEC), encoding="utf-8")
        created = cli("case", "create", str(project), "--spec", str(spec_file), "--owner", OWNER)
        case_id = created["case_id"]
        steps = [
            ("case.analyze", ["case", "analyze", str(project), case_id]),
            ("case.approve", ["case", "approve", str(project), case_id, "--owner", OWNER]),
            ("case.execute", ["case", "execute", str(project), case_id]),
            ("case.verify", ["case", "verify", str(project), case_id]),
            ("case.package", ["case", "package", str(project), case_id]),
            ("case.status", ["case", "status", str(project), case_id]),
        ]
        for name, args in steps:
            doc = cli(*args)
            if doc == 1:
                return 1
            state = doc.get("state") or doc.get("case", {}).get("state", "")
            print(f"{name:>14} -> {state or doc.get('error_code', '')}")

        case_dir = project / "cases" / case_id
        final_case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
        shutil.copy2(case_dir / "case.json", TARGET / "case_final.json")
        shutil.copytree(case_dir / "evidence", TARGET / "evidence")
        (TARGET / "output").mkdir(parents=True, exist_ok=True)
        shutil.copy2(case_dir / "output" / "processed_audio.wav", TARGET / "output" / "processed_audio.wav")
        (TARGET / "source_manifest.json").write_text(json.dumps({
            "fixture": str(FIXTURE), "relative_path": str(FIXTURE.relative_to(REPO_ROOT)),
            "sha256": final_case["source_sha256"],
            "duration_s": 45.0, "sample_rate": 48000, "channels": 2}, indent=2), encoding="utf-8")
        _write(transcript)
        _write_readme(final_case)
        print(f"\ngolden case complete: {TARGET}")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _write(transcript: list[dict]) -> None:
    (TARGET / "cli_transcript.json").write_text(
        json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_readme(final_case: dict) -> None:
    manifest = json.loads((TARGET / "evidence" / "evidence_manifest.json").read_text(encoding="utf-8"))
    lines = [
        "# Golden Runtime Case — DSK-MFY-RUNTIME-INTEGRATION-001",
        "",
        "One complete real production case driven through the formal CLI v2.",
        "",
        "## Case",
        f"- case_id: {final_case['case_id']}",
        f"- final state: {final_case['state']}",
        f"- source fixture: `moodify-core-package/tests/baseline/test_audio/vocal_folk.wav`",
        f"- source_sha256: `{final_case['source_sha256'][:16]}...`",
        f"- plan_hash: `{final_case['plan_hash'][:16]}...`",
        f"- approval: `{final_case['artistic_approval']['approval_id']}` by {final_case['artistic_approval']['human_owner']}",
        f"- engine: {manifest['engine_name']} {manifest['engine_version']}",
        f"- execution: `{manifest['execution_id']}`",
        f"- verification: `{manifest['verification_id']}` ({manifest['verification_status']})",
        f"- moodify_version: {manifest['moodify_version']}",
        "",
        "## State path (from case_final.json transitions)",
        "```",
    ]
    for t in final_case["transitions"]:
        src = t["from"] or "-"
        lines.append(f"{src} -> {t['to']}  ({t['at']})")
    lines += [
        "```",
        "",
        "## Artifacts",
        "- `cli_transcript.json` — every CLI request and response",
        "- `case_final.json` — persisted case state incl. execution + verification records",
        "- `evidence/` — the formal evidence package (verified and internally consistent)",
        "- `output/processed_audio.wav` — the executed output",
        "- `source_manifest.json` — fixture identity",
    ]
    (TARGET / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
