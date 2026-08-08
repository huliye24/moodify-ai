from __future__ import annotations

import argparse
import json
from pathlib import Path

from .audio import measure_audio, match_loudness, read_audio, write_audio
from .baselines import train_baselines
from .candidates import generate_candidates
from .deepseek_pack import build_deepseek_pack
from .experiment import prepare_pilot
from .pilot_gate import evaluate_pilot
from .records import audit_records, load_jsonl, write_jsonl


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA = ROOT / "schemas" / "power_pair_record_v0.2.json"


def _write_json(path: Path | None, value: object) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path is None:
        print(text, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def cmd_measure(args: argparse.Namespace) -> int:
    _write_json(args.out, measure_audio(args.input).to_dict())
    return 0


def cmd_match(args: argparse.Namespace) -> int:
    reference, sample_rate = read_audio(args.reference)
    candidate, candidate_rate = read_audio(args.candidate)
    if sample_rate != candidate_rate:
        raise ValueError("sample rates differ")
    matched, gain_db = match_loudness(reference, candidate, sample_rate)
    write_audio(args.out, matched, sample_rate)
    report = {
        "gain_db": gain_db,
        "reference": measure_audio(args.reference).to_dict(),
        "matched": measure_audio(args.out).to_dict(),
    }
    _write_json(args.report, report)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    results = generate_candidates(args.source, args.plan, args.out_dir)
    print(json.dumps({"generated": len(results), "out_dir": str(args.out_dir)}))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    records = load_jsonl(args.records)
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    summary, anomalies = audit_records(records, schema)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.out_dir / "audit_summary.json", summary)
    write_jsonl(args.out_dir / "anomalies.jsonl", anomalies)
    print(json.dumps(summary, sort_keys=True))
    return 0 if not anomalies else 2


def cmd_train(args: argparse.Namespace) -> int:
    results = train_baselines(load_jsonl(args.records), args.out_dir)
    print(json.dumps(results, sort_keys=True))
    return 0


def cmd_deepseek(args: argparse.Namespace) -> int:
    result = build_deepseek_pack(args.evidence_dir, args.out_dir)
    print(json.dumps(result, sort_keys=True))
    return 0


def cmd_pilot(args: argparse.Namespace) -> int:
    audit = json.loads(args.audit.read_text(encoding="utf-8"))
    thresholds = (
        json.loads(args.thresholds.read_text(encoding="utf-8")) if args.thresholds else None
    )
    result = evaluate_pilot(audit, thresholds)
    _write_json(args.out, result)
    print(json.dumps({"decision": result["decision"]}, sort_keys=True))
    return 0 if result["decision"] == "go" else 2


def cmd_prepare_pilot(args: argparse.Namespace) -> int:
    result = prepare_pilot(
        args.input_dir,
        args.out_dir,
        experiment_id=args.experiment_id,
        seed=args.seed,
        listener_count=args.listeners,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Moodify Power Reward Model v0.1")
    sub = parser.add_subparsers(dest="command", required=True)

    measure = sub.add_parser("measure")
    measure.add_argument("input", type=Path)
    measure.add_argument("--out", type=Path)
    measure.set_defaults(func=cmd_measure)

    match = sub.add_parser("match-loudness")
    match.add_argument("--reference", type=Path, required=True)
    match.add_argument("--candidate", type=Path, required=True)
    match.add_argument("--out", type=Path, required=True)
    match.add_argument("--report", type=Path)
    match.set_defaults(func=cmd_match)

    generate = sub.add_parser("generate-candidates")
    generate.add_argument("--source", type=Path, required=True)
    generate.add_argument("--plan", type=Path, required=True)
    generate.add_argument("--out-dir", type=Path, required=True)
    generate.set_defaults(func=cmd_generate)

    prepare = sub.add_parser("prepare-pilot")
    prepare.add_argument("--input-dir", type=Path, required=True)
    prepare.add_argument("--out-dir", type=Path, required=True)
    prepare.add_argument("--experiment-id", default="PWRM-EXP-001")
    prepare.add_argument("--seed", type=int, default=20260724)
    prepare.add_argument("--listeners", type=int, default=12)
    prepare.set_defaults(func=cmd_prepare_pilot)

    audit = sub.add_parser("audit-dataset")
    audit.add_argument("--records", type=Path, required=True)
    audit.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    audit.add_argument("--out-dir", type=Path, required=True)
    audit.set_defaults(func=cmd_audit)

    train = sub.add_parser("train-baselines")
    train.add_argument("--records", type=Path, required=True)
    train.add_argument("--out-dir", type=Path, required=True)
    train.set_defaults(func=cmd_train)

    pilot = sub.add_parser("evaluate-pilot")
    pilot.add_argument("--audit", type=Path, required=True)
    pilot.add_argument("--thresholds", type=Path)
    pilot.add_argument("--out", type=Path, required=True)
    pilot.set_defaults(func=cmd_pilot)

    deepseek = sub.add_parser("prepare-deepseek")
    deepseek.add_argument("--evidence-dir", type=Path, required=True)
    deepseek.add_argument("--out-dir", type=Path, required=True)
    deepseek.set_defaults(func=cmd_deepseek)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
