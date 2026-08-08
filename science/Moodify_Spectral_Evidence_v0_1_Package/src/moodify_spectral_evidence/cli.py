"""CLI: audit | build | validate"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from dataclasses import asdict
from pathlib import Path

from .analyzer import (
    AnalysisParams,
    CaseSpec,
    TrackSpec,
    analyze_track,
    compute_band_metrics,
)
from .workbook import write_research_workbook


TRACK_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_case_spec(spec_path: Path) -> tuple[dict, list[str]]:
    import yaml  # type: ignore[import-untyped]

    errors: list[str] = []
    if not spec_path.is_file():
        return {}, [f"Case spec not found: {spec_path}"]
    try:
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        return {}, [f"Invalid case spec: {exc}"]
    if not isinstance(data, dict):
        return {}, ["Case spec must be a mapping"]
    tracks = data.get("tracks")
    if not isinstance(tracks, list) or not tracks:
        errors.append("Case spec must contain at least one track")
        return data, errors
    seen: set[str] = set()
    for index, track in enumerate(tracks):
        if not isinstance(track, dict):
            errors.append(f"Track {index} must be a mapping")
            continue
        track_id = track.get("track_id", f"track_{index}")
        if not isinstance(track_id, str) or not TRACK_ID_PATTERN.fullmatch(track_id):
            errors.append(f"Invalid track_id: {track_id!r}")
        elif track_id in seen:
            errors.append(f"Duplicate track_id: {track_id}")
        seen.add(track_id)
        for version in ("before", "after"):
            value = track.get(version)
            if not isinstance(value, dict) or not isinstance(value.get("path"), str):
                errors.append(f"Track {track_id} missing {version}.path")
    return data, errors


def cmd_audit(args: argparse.Namespace) -> int:
    """Audit a case spec: check all audio files exist and are readable."""
    spec_path = Path(args.case_spec)
    data, schema_errors = _read_case_spec(spec_path)
    if schema_errors:
        for error in schema_errors:
            print(f"ERROR: {error}")
        return 2
    print(f"Audit: {data.get('title', spec_path.stem)}")
    errors = 0
    for i, t in enumerate(data.get("tracks", [])):
        before = Path(t["before"]["path"])
        after = Path(t["after"]["path"])
        b_ok = before.is_file()
        a_ok = after.is_file()
        flag = "[OK]" if b_ok and a_ok else "[MISSING]"
        print(f"  {flag} {t.get('track_id', f'track_{i}')}: before={b_ok} after={a_ok}")
        if not b_ok or not a_ok:
            errors += 1
    print(f"\n{len(data.get('tracks', []))} tracks, {errors} missing")
    return 0 if errors == 0 else 1


def cmd_build(args: argparse.Namespace) -> int:
    """Build before/after/difference spectrograms and metrics."""
    spec_path = Path(args.case_spec)
    out_dir = Path(args.output_dir).resolve()

    if out_dir.exists() and list(out_dir.iterdir()):
        print(f"ERROR: Output directory is not empty: {out_dir}")
        return 2

    data, schema_errors = _read_case_spec(spec_path)
    if schema_errors:
        for error in schema_errors:
            print(f"ERROR: {error}")
        return 2
    missing = [
        str(Path(track[version]["path"]))
        for track in data["tracks"]
        for version in ("before", "after")
        if not Path(track[version]["path"]).is_file()
    ]
    if missing:
        for path in missing:
            print(f"ERROR: Audio file not found: {path}")
        return 2
    params = AnalysisParams()
    spec = CaseSpec(
        case_id=data.get("case_id", spec_path.stem),
        title=data.get("title", spec_path.stem),
        tracks=[TrackSpec(
            track_id=t.get("track_id", f"track_{i}"),
            role=t.get("role", "other"),
            before_path=t["before"]["path"],
            after_path=t["after"]["path"],
        ) for i, t in enumerate(data.get("tracks", []))],
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building: {spec.title} ({len(spec.tracks)} tracks)")

    all_metrics = []
    all_band_metrics = []
    hashes = {}

    for track in spec.tracks:
        print(f"  Processing: {track.track_id}")
        track_dir = assets_dir / track.track_id
        metrics = analyze_track(track, params, track_dir)
        bands = [] if metrics.errors else compute_band_metrics(track, params, track_dir)
        all_metrics.append(metrics)
        all_band_metrics.extend(bands)
        if metrics.before_hash:
            hashes[f"{track.track_id}_before"] = metrics.before_hash
        if metrics.after_hash:
            hashes[f"{track.track_id}_after"] = metrics.after_hash

    # case_summary.json
    summary = {
        "case_id": spec.case_id,
        "title": spec.title,
        "params": asdict(params),
        "tracks": [asdict(m) for m in all_metrics],
        "hashes": hashes,
    }
    (out_dir / "case_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # manifest.json
    # track_summary.csv
    csv_path = out_dir / "track_summary.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["track_id", "role", "before_hash", "after_hash", "before_original_sr",
                         "after_original_sr", "channels", "duration_s", "rms_delta_db",
                         "peak_before", "peak_after", "warnings", "errors"])
        for m in all_metrics:
            writer.writerow([m.track_id, m.role, m.before_hash, m.after_hash,
                             m.before_original_sample_rate, m.after_original_sample_rate,
                             m.before_channels, m.before_duration_s, m.rms_delta_db,
                             m.before_peak_db, m.after_peak_db, "; ".join(m.warnings),
                             "; ".join(m.errors)])

    # band_comparison.csv
    band_csv = out_dir / "band_comparison.csv"
    with open(band_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["track_id", "band", "freq_range_hz", "before_energy_db",
                         "after_energy_db", "delta_db"])
        for bm in all_band_metrics:
            writer.writerow([bm.track_id, bm.band, bm.freq_range_hz, bm.before_energy_db,
                             bm.after_energy_db, bm.delta_db])

    workbook_path = out_dir / "spectral_evidence.xlsx"
    write_research_workbook(workbook_path, spec, params, all_metrics, all_band_metrics)

    source_refs = {
        track.track_id: {
            "before_path": str(Path(track.before_path).resolve()),
            "after_path": str(Path(track.after_path).resolve()),
            "before_hash": hashes.get(f"{track.track_id}_before", ""),
            "after_hash": hashes.get(f"{track.track_id}_after", ""),
        }
        for track in spec.tracks
    }
    artifact_hashes = {
        str(path.relative_to(out_dir)).replace("\\", "/"): _sha256(path)
        for path in sorted(out_dir.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    manifest = {
        "case_id": spec.case_id,
        "builder": "moodify_spectral_evidence v0.1",
        "params": asdict(params),
        "tracks": len(spec.tracks),
        "hashes": hashes,
        "source_refs": source_refs,
        "artifact_hashes": artifact_hashes,
        "parquet_status": "NOT_AVAILABLE_NO_PYARROW",
        "difference_semantics": "after_db - before_db; common absolute amplitude reference",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    errors = sum(len(m.errors) for m in all_metrics)
    warnings = sum(len(m.warnings) for m in all_metrics)
    print(f"Done. {len(spec.tracks)} tracks, {errors} errors, {warnings} warnings")
    return 0 if errors == 0 else 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a built evidence bundle."""
    bundle_dir = Path(args.bundle_dir)
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: No manifest.json found in {bundle_dir}")
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(f"Validating: {manifest.get('case_id', 'unknown')}")
    errors = 0

    for track_id, source in manifest.get("source_refs", {}).items():
        for version in ("before", "after"):
            path = Path(source.get(f"{version}_path", ""))
            expected = source.get(f"{version}_hash", "")
            if not path.is_file() or _sha256(path) != expected:
                print(f"  SOURCE_HASH_MISMATCH: {track_id}_{version}")
                errors += 1

    for relative_path, expected_hash in manifest.get("artifact_hashes", {}).items():
        artifact = (bundle_dir / relative_path).resolve()
        try:
            artifact.relative_to(bundle_dir.resolve())
        except ValueError:
            print(f"  PATH_ESCAPE: {relative_path}")
            errors += 1
            continue
        if not artifact.is_file():
            print(f"  MISSING: {relative_path}")
            errors += 1
        elif _sha256(artifact) != expected_hash:
            print(f"  ARTIFACT_HASH_MISMATCH: {relative_path}")
            errors += 1

    # Check key artifacts exist
    for artifact in ["case_summary.json", "track_summary.csv", "band_comparison.csv",
                     "spectral_evidence.xlsx"]:
        p = bundle_dir / artifact
        if not p.exists():
            print(f"  MISSING: {artifact}")
            errors += 1

    print(f"Validation done: {errors} issues")
    return 0 if errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Moodify Spectral Evidence v0.1")
    sub = parser.add_subparsers(dest="command")

    p_audit = sub.add_parser("audit", help="Audit case spec for missing files")
    p_audit.add_argument("--case-spec", required=True)

    p_build = sub.add_parser("build", help="Build before/after evidence")
    p_build.add_argument("--case-spec", required=True)
    p_build.add_argument("--output-dir", required=True)

    p_validate = sub.add_parser("validate", help="Validate evidence bundle")
    p_validate.add_argument("bundle_dir")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    handlers = {"audit": cmd_audit, "build": cmd_build, "validate": cmd_validate}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
