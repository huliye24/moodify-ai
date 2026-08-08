"""Studio prep CLI — session init, asset verify, WSE analysis, candidate plans,
candidate generation/comparison, and report building.

All subcommands require --output-dir. No source files are modified.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .models import (
    TOOL_VERSION,
    AssetEntry,
    AssetKind,
    AssetRole,
    BackupTarget,
    DeliverableContract,
    RecordingSpec,
    SessionBrief,
    SessionManifest,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check_output_dir(output_dir: Path, allow_nonempty: bool = False) -> None:
    """Refuse to write into an existing non-empty directory by default."""
    if output_dir.exists():
        if not output_dir.is_dir():
            raise NotADirectoryError(f"Output path exists but is not a directory: {output_dir}")
        contents = list(output_dir.iterdir())
        if contents and not allow_nonempty:
            raise FileExistsError(
                f"Output directory is not empty: {output_dir}. "
                "Use --force to overwrite or specify a new directory."
            )


def _check_paths_different(a: Path, b: Path) -> None:
    if a.resolve() == b.resolve():
        raise ValueError(f"Source and output paths must be different: {a}")


def _sha256_file(path: Path) -> str:
    """Deterministic SHA-256 of a file (same semantics as moodify-bridge)."""
    import hashlib

    if not path.is_file():
        raise FileNotFoundError(f"Asset is not a readable file: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _probe_audio(path: Path) -> dict:
    """Read-only audio probe: sample rate, channels, duration, frame count."""
    try:
        import soundfile as sf
    except ImportError:
        return {"error": "soundfile not installed; cannot probe audio"}
    try:
        info = sf.info(str(path))
        return {
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "duration_s": round(info.duration, 3),
            "frame_count": info.frames,
            "format": info.format,
            "subtype": info.subtype,
        }
    except Exception as exc:
        return {"error": f"Audio probe failed: {exc}"}


def _write_json(data: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def _guess_kind(ext: str) -> AssetKind:
    audio_exts = {".wav", ".flac", ".aiff", ".aif", ".mp3", ".ogg", ".m4a"}
    midi_exts = {".mid", ".midi"}
    if ext.lower() in audio_exts:
        return AssetKind.AUDIO
    if ext.lower() in midi_exts:
        return AssetKind.MIDI
    return AssetKind.TEXT


def _guess_role(filename: str) -> AssetRole:
    fn = filename.lower()
    if "vocal" in fn:
        return AssetRole.VOCAL_STEM
    if "instrumental" in fn or "inst" in fn:
        return AssetRole.INSTRUMENTAL_STEM
    if "reference" in fn or "ref" in fn:
        return AssetRole.REFERENCE_MIX
    if "lyric" in fn:
        return AssetRole.LYRIC_SHEET
    if fn.endswith(".mid") or fn.endswith(".midi"):
        return AssetRole.MIDI
    return AssetRole.SOURCE_STEM


# ── session-init ──────────────────────────────────────────────

def _cmd_session_init(args: argparse.Namespace) -> int:
    """Initialize a new recording session from a YAML brief file."""
    brief_path = Path(args.brief)
    if not brief_path.exists():
        print(f"ERROR: Brief file not found: {brief_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    try:
        _check_output_dir(output_dir, allow_nonempty=args.force)
    except (FileExistsError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Parse YAML brief
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML is required for session-init. Install with: pip install pyyaml",
              file=sys.stderr)
        return 1

    try:
        with open(brief_path, "r", encoding="utf-8") as f:
            brief_data = yaml.safe_load(f)
    except Exception as exc:
        print(f"ERROR: Failed to parse YAML brief: {exc}", file=sys.stderr)
        return 1

    if brief_data is None:
        print("ERROR: Brief file is empty.", file=sys.stderr)
        return 1

    # Build session brief
    try:
        session_brief = SessionBrief(
            project_title=brief_data.get("project_title", "Untitled"),
            client_name=brief_data.get("client_name", "Unknown"),
            engineer_name=brief_data.get("engineer_name", "Unknown"),
            studio_location=brief_data.get("studio_location", "Unknown"),
            session_date=brief_data.get("session_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            genre=brief_data.get("genre", ""),
            target_bpm=brief_data.get("target_bpm"),
            target_key=brief_data.get("target_key", ""),
            notes=brief_data.get("notes", ""),
        )
    except Exception as exc:
        print(f"ERROR: Invalid session brief: {exc}", file=sys.stderr)
        return 1

    # Build recording spec
    rs_data = brief_data.get("recording_spec", {})
    try:
        recording_spec = RecordingSpec(
            sample_rate=rs_data.get("sample_rate", "48000"),
            bit_depth=rs_data.get("bit_depth", "24"),
            file_format=rs_data.get("file_format", "wav"),
            target_peak_dbfs=rs_data.get("target_peak_dbfs", -6.0),
            channel_count=rs_data.get("channel_count", 2),
            naming_template=rs_data.get("naming_template",
                "{session_id}_T{take:03d}_{role}.wav"),
        )
    except Exception as exc:
        print(f"ERROR: Invalid recording spec: {exc}", file=sys.stderr)
        return 1

    # Backup targets
    backup_targets = []
    for bt_data in brief_data.get("backup_targets", []):
        try:
            backup_targets.append(BackupTarget(**bt_data))
        except Exception as exc:
            print(f"ERROR: Invalid backup target: {exc}", file=sys.stderr)
            return 1

    # Deliverable contract
    dc_data = brief_data.get("deliverable_contract", {})
    try:
        deliverable = DeliverableContract(**dc_data) if dc_data else DeliverableContract()
    except Exception as exc:
        print(f"ERROR: Invalid deliverable contract: {exc}", file=sys.stderr)
        return 1

    manifest = SessionManifest(
        session_brief=session_brief,
        recording_spec=recording_spec,
        backup_targets=backup_targets,
        deliverable_contract=deliverable,
    )

    # Register assets listed in brief
    for asset_data in brief_data.get("assets", []):
        filename = asset_data.get("filename", "")
        if not filename:
            continue
        role_str = asset_data.get("role", "source_stem")
        try:
            role = AssetRole(role_str)
        except ValueError:
            role = _guess_role(filename)
        kind = _guess_kind(Path(filename).suffix)
        entry = AssetEntry(
            role=role if asset_data.get("role") else _guess_role(filename),
            kind=kind,
            filename=filename,
            local_path=asset_data.get("local_path", ""),
            notes=asset_data.get("notes", ""),
        )
        # If role was explicitly set, use it
        if asset_data.get("role"):
            try:
                entry = AssetEntry(
                    role=AssetRole(asset_data["role"]),
                    kind=kind,
                    filename=filename,
                    local_path=asset_data.get("local_path", ""),
                    notes=asset_data.get("notes", ""),
                )
            except ValueError:
                pass
        manifest.add_asset(entry)

    # Write outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "manifest.json"
    _write_json(manifest.model_dump(mode="json"), manifest_path)
    print(f"  manifest: {manifest_path}")

    # Write checklist
    checklist_path = output_dir / "RECORDING_DAY_CHECKLIST.md"
    checklist_text = _build_checklist(manifest, brief_path)
    checklist_path.write_text(checklist_text, encoding="utf-8")
    print(f"  checklist: {checklist_path}")

    # Write delivery contract
    contract_path = output_dir / "delivery_contract.json"
    _write_json(deliverable.model_dump(mode="json"), contract_path)
    print(f"  contract: {contract_path}")

    print(f"\nSession initialized: {manifest.session_brief.session_id}")
    print(f"  Assets registered: {len(manifest.assets)}")
    print(f"  Backup targets: {len(manifest.backup_targets)}")
    return 0


def _build_checklist(manifest: SessionManifest, brief_path: Path) -> str:
    sb = manifest.session_brief
    rs = manifest.recording_spec
    bt_list = "\n".join(f"- [ ] `{bt.label}` → `{bt.path}`" for bt in manifest.backup_targets) or "- [ ] No backup targets configured"

    return f"""# Recording Day Checklist

**Session:** {sb.project_title}
**Client:** {sb.client_name}
**Date:** {sb.session_date}
**Engineer:** {sb.engineer_name}
**Location:** {sb.studio_location}
**Brief source:** `{brief_path}`

---

## Phase 1 — Before Recording (到棚后 30 分钟内)

- [ ] Power on all equipment; verify signal path
- [ ] Set sample rate: **{rs.sample_rate.value} Hz**
- [ ] Set bit depth: **{rs.bit_depth.value}-bit**
- [ ] Target input peak: **{rs.target_peak_dbfs} dBFS**
- [ ] Configure DAW project with above settings
- [ ] Test record 10s silence; verify file format ({rs.file_format.value}) and specs
- [ ] Verify headphone mixes for all performers
- [ ] Arm tracks; confirm no clipping on loudest test passage
- [ ] Write session date/time and take counter on physical log

## Phase 2 — Each Take

- [ ] Announce take number verbally before recording
- [ ] Record at least 3s pre-roll silence
- [ ] Monitor input meters during recording (peak < {rs.target_peak_dbfs} dBFS)
- [ ] After stop: immediately rename file per naming template: `{rs.naming_template}`
- [ ] Run `asset-verify` on the recorded file
- [ ] Note any issues (clicks, dropouts, distortion) in session log
- [ ] If take is bad: mark as rejected, do NOT delete; keep for audit

## Phase 3 — After Recording Session

- [ ] Verify all planned takes are recorded
- [ ] Run `asset-verify` on every take
- [ ] Check for missing or corrupted files (sha256 mismatch)
- [ ] Write session notes: performer comments, noteworthy moments, issues
- [ ] Generate WSE profile on key reference takes (optional, for immediate feedback)

## Phase 4 — Before Leaving Studio

- [ ] **Backup 1:** Copy all takes + manifest + checklist to first backup location
{bt_list}
- [ ] Verify backup: run `asset-verify` on backed-up files; sha256 must match
- [ ] Lock/read-only all original takes
- [ ] Confirm no files left in temp/scratch locations
- [ ] Photograph physical log (whiteboard/notes)
- [ ] Sign off: engineer + client confirm all deliverables captured

---

## Naming Template

```
{rs.naming_template}
```

## Registered Assets

| # | Filename | Role | Kind |
|---|----------|------|------|
""" + "\n".join(f"| {i+1} | `{a.filename}` | {a.role.value} | {a.kind.value} |" for i, a in enumerate(manifest.assets))

# ── asset-verify ─────────────────────────────────────────────

def _cmd_asset_verify(args: argparse.Namespace) -> int:
    """Read-only verification of audio/assets: SHA-256, size, audio probe."""
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    _check_output_dir(output_dir, allow_nonempty=args.force)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load manifest
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except Exception as exc:
        print(f"ERROR: Failed to read manifest: {exc}", file=sys.stderr)
        return 1

    manifest = SessionManifest(**manifest_data)
    errors = []
    verified = []

    for asset in manifest.assets:
        if not asset.local_path:
            print(f"  SKIP: {asset.filename} — no local_path set")
            continue

        local = Path(asset.local_path)
        if not local.exists():
            asset.decode_error = f"File not found: {asset.local_path}"
            errors.append(f"{asset.filename}: file not found")
            continue

        # Check source != output
        try:
            _check_paths_different(local, output_dir)
        except ValueError as exc:
            print(f"  REJECT: {asset.filename} — {exc}")
            return 1

        # Hash
        try:
            asset.sha256 = _sha256_file(local)
            asset.file_size_bytes = local.stat().st_size
        except Exception as exc:
            asset.decode_error = f"SHA-256 failed: {exc}"
            errors.append(f"{asset.filename}: hash failed — {exc}")
            continue

        # Audio probe
        if asset.kind == AssetKind.AUDIO:
            probe = _probe_audio(local)
            if "error" in probe:
                asset.decode_error = probe["error"]
                errors.append(f"{asset.filename}: {probe['error']}")
            else:
                asset.sample_rate = probe.get("sample_rate")
                asset.channels = probe.get("channels")
                asset.duration_s = probe.get("duration_s")
                asset.frame_count = probe.get("frame_count")

        asset.verified_at = _utc_now()
        verified.append(asset)

    # Write updated manifest
    updated_path = output_dir / "manifest_verified.json"
    _write_json(manifest.model_dump(mode="json"), updated_path)
    print(f"  Verified manifest: {updated_path}")

    # Summary
    print(f"\nAsset Verification Summary:")
    print(f"  Total: {len(manifest.assets)}")
    print(f"  Verified OK: {len(verified)}")
    print(f"  Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e}")

    return 1 if errors else 0


# ── CLI ───────────────────────────────────────────────────────

# ── wse-analyze ──────────────────────────────────────────────

def _cmd_wse_analyze(args: argparse.Namespace) -> int:
    """Run WSE analysis on an audio file."""
    from .wse_profile import (
        compute_wse_profile,
        compute_window_evolution,
        write_wse_profile,
        write_wse_warnings,
        write_window_evolution_csv,
    )

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    try:
        _check_output_dir(output_dir, allow_nonempty=args.force)
    except (FileExistsError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        _check_paths_different(input_path.resolve(), output_dir.resolve())
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    source_sha256 = _sha256_file(input_path)
    print(f"  Source SHA-256: {source_sha256}")

    profile = compute_wse_profile(
        str(input_path),
        source_sha256=source_sha256,
        frame_size=args.frame_size,
        hop_size=args.hop_size,
    )

    # Warnings
    if profile.warnings:
        print(f"  Warnings ({len(profile.warnings)}):")
        for w in profile.warnings:
            print(f"    - {w}")

    # Window evolution
    windows, n_windows = compute_window_evolution(
        str(input_path),
        frame_size=args.frame_size,
        hop_size=args.hop_size,
    )
    profile.window_count = n_windows

    # Write outputs
    profile_path = write_wse_profile(profile, output_dir)
    print(f"  WSE profile: {profile_path}")

    warnings_path = write_wse_warnings(profile, output_dir)
    print(f"  Warnings: {warnings_path}")

    csv_path = write_window_evolution_csv(windows, output_dir)
    print(f"  Evolution CSV: {csv_path} ({n_windows} windows)")

    # Summary
    print(f"\nWSE Analysis complete:")
    print(f"  Duration: {profile.duration_s}s, {profile.channels}ch @ {profile.sample_rate}Hz")
    print(f"  Peak: {profile.peak_linear:.4f} linear" if profile.peak_linear else "  Peak: null")
    print(f"  RMS: {profile.rms_linear:.4f} linear" if profile.rms_linear else "  RMS: null")
    print(f"  Crest: {profile.crest_factor:.2f}" if profile.crest_factor else "  Crest: null")
    if profile.loudness_lufs is not None:
        print(f"  Integrated LUFS: {profile.loudness_lufs:.1f}")
    else:
        print(f"  Integrated LUFS: null (pyloudnorm unavailable)")
    print(f"  LRA: null  |  True Peak: null  |  Phase: null  |  Masking: null")
    return 0


# ── candidate-plan ────────────────────────────────────────────

def _cmd_candidate_plan(args: argparse.Namespace) -> int:
    """Generate candidate processing plans from a WSE profile."""
    from .candidate_plan import generate_candidate_plans, write_candidate_plans

    wse_path = Path(args.wse_profile)
    if not wse_path.exists():
        print(f"ERROR: WSE profile not found: {args.wse_profile}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    try:
        _check_output_dir(output_dir, allow_nonempty=args.force)
    except (FileExistsError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    plan_set = generate_candidate_plans(str(wse_path))
    plan_path = write_candidate_plans(plan_set, output_dir)
    print(f"  Candidate plans: {plan_path}")

    print(f"\nCandidate Plans generated:")
    for plan in plan_set.plans:
        evidence_count = len(plan.evidence)
        risk_count = len(plan.risk)
        print(f"  [{plan.plan_id}] preset={plan.preset}, "
              f"evidence={evidence_count}, risk={risk_count}, "
              f"human_review=PENDING")

    if plan_set.general_warnings:
        print(f"\nWarnings:")
        for w in plan_set.general_warnings:
            print(f"  - {w}")
    return 0


# ── candidate-compare ─────────────────────────────────────────

def _cmd_candidate_compare(args: argparse.Namespace) -> int:
    """Compare generated candidate outputs using WSE metrics."""
    from .wse_profile import compute_wse_profile
    from .reporting import build_comparison_table

    candidates_dir = Path(args.candidates_dir)
    if not candidates_dir.is_dir():
        print(f"ERROR: Candidates directory not found: {args.candidates_dir}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    try:
        _check_output_dir(output_dir, allow_nonempty=args.force)
    except (FileExistsError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Find candidate WAV files
    candidate_wavs = list(candidates_dir.glob("candidate_*/*.wav"))
    if not candidate_wavs:
        print("  No candidate WAV files found. Cannot compare.", file=sys.stderr)
        return 1

    # Use first candidate as reference for comparison
    # (in production, you'd compare each against source)
    comparisons = []
    for wav_path in candidate_wavs:
        try:
            profile = compute_wse_profile(str(wav_path))
            profile_dict = profile.to_dict()
            # Store for later comparison
            comparisons.append({
                "candidate_path": str(wav_path),
                "profile": profile_dict,
            })
            print(f"  Profiled: {wav_path.name}")
        except Exception as exc:
            print(f"  WARNING: Failed to profile {wav_path.name}: {exc}")

    if len(comparisons) < 2:
        print("  Need at least 2 profiles to compare.", file=sys.stderr)
        return 1

    # Pairwise comparison against first (reference) candidate
    ref = comparisons[0]
    all_comparisons = []
    for cand in comparisons[1:]:
        comp = build_comparison_table(ref["profile"], cand["profile"])
        comp["reference_candidate"] = ref["candidate_path"]
        comp["candidate"] = cand["candidate_path"]
        all_comparisons.append(comp)

    # Write comparison output
    output_dir.mkdir(parents=True, exist_ok=True)
    comp_path = output_dir / "comparison.json"
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(all_comparisons, f, ensure_ascii=False, indent=2, default=str)
    print(f"  Comparison: {comp_path}")

    # Write human review placeholder
    review_path = output_dir / "human_review.md"
    review_text = _build_human_review_md(all_comparisons)
    review_path.write_text(review_text, encoding="utf-8")
    print(f"  Human review form: {review_path}")

    print(f"\nComparisons: {len(all_comparisons)}")
    for c in all_comparisons:
        print(f"  human_review={c['human_review']}")

    return 0


def _build_human_review_md(comparisons: list[dict]) -> str:
    lines = [
        "# Human Review — Candidate Comparison",
        "",
        "**STATUS: PENDING** — All candidates require human review before selection.",
        "",
        "## Instructions",
        "",
        "1. Loudness-match all candidates to the reference.",
        "2. Listen on at least 2 playback systems (monitors + headphones).",
        "3. Score each candidate on the checklist below.",
        "4. Do NOT assume louder = better.",
        "5. Do NOT select a candidate based on technical metrics alone.",
        "",
        "## Comparison Summary",
        "",
    ]
    for i, comp in enumerate(comparisons):
        lines.append(f"### Comparison {i + 1}")
        lines.append(f"- **Reference:** {comp.get('reference_candidate', '—')}")
        lines.append(f"- **Candidate:** {comp.get('candidate', '—')}")
        for key, val in comp.get("deltas", {}).items():
            lines.append(f"  - {key}: {val}")
        lines.append("")

    lines += [
        "## Listening Checklist",
        "",
        "| # | Item | Score (1-5) | Notes |",
        "|---|------|-------------|-------|",
        "| 1 | Volume matched? | yes / no | |",
        "| 2 | Clarity | — / 5 | 1=muddy, 5=clear |",
        "| 3 | Warmth | — / 5 | 1=cold, 5=warm |",
        "| 4 | Space/Width | — / 5 | 1=flat, 5=open |",
        "| 5 | Harshness control | — / 5 | 1=harsh, 5=smooth |",
        "| 6 | Artifact control | — / 5 | 1=artifacts, 5=clean |",
        "| 7 | Mono compatibility | — / 5 | 1=broken, 5=preserved |",
        "| 8 | Overall preference | — / 5 | |",
        "",
        "## Decision",
        "",
        "- [ ] Candidate A approved",
        "- [ ] Candidate B approved",
        "- [ ] Candidate C approved",
        "- [ ] Needs revision (describe below)",
        "- [ ] Use original (no processing)",
        "",
        "**Engineer signature:** _________________  **Date:** _________________",
        "",
        "**Client approval:** _________________  **Date:** _________________",
        "",
    ]
    return "\n".join(lines) + "\n"


# ── report-build ──────────────────────────────────────────────

def _cmd_report_build(args: argparse.Namespace) -> int:
    """Build Markdown + HTML technical report."""
    from .reporting import build_markdown_report, build_html_report

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    output_dir = Path(args.output_dir)
    try:
        _check_output_dir(output_dir, allow_nonempty=args.force)
    except (FileExistsError, NotADirectoryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Load inputs
    manifest = None
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception as exc:
        print(f"ERROR: Failed to read manifest: {exc}", file=sys.stderr)
        return 1

    wse_profile = None
    if args.wse_profile:
        wse_path = Path(args.wse_profile)
        if wse_path.exists():
            with open(wse_path, "r", encoding="utf-8") as f:
                wse_profile = json.load(f)

    comparison = None
    if args.comparison:
        comp_path = Path(args.comparison)
        if comp_path.exists():
            with open(comp_path, "r", encoding="utf-8") as f:
                comparison = json.load(f)

    # Build report
    md_content = build_markdown_report(
        manifest=manifest,
        wse_profile=wse_profile,
        comparisons=comparison if isinstance(comparison, list) else ([comparison] if comparison else None),
    )

    html_content = build_html_report(md_content, title="Moodify Studio Session Report")

    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "report.md"
    html_path = output_dir / "report.html"

    md_path.write_text(md_content, encoding="utf-8")
    html_path.write_text(html_content, encoding="utf-8")

    print(f"  Markdown: {md_path}")
    print(f"  HTML: {html_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Moodify Studio Session Prep — recording project toolchain",
    )
    parser.add_argument("--version", action="version", version=f"studio_prep {TOOL_VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    # session-init
    p_init = sub.add_parser("session-init", help="Initialize a recording session from YAML brief")
    p_init.add_argument("--brief", required=True, help="Path to session brief YAML file")
    p_init.add_argument("--output-dir", required=True, help="Session output directory (must be empty/new)")
    p_init.add_argument("--force", action="store_true", help="Allow writing into non-empty output dir")
    p_init.set_defaults(func=_cmd_session_init)

    # asset-verify
    p_verify = sub.add_parser("asset-verify", help="Verify assets (SHA-256, audio probe) read-only")
    p_verify.add_argument("--manifest", required=True, help="Path to session manifest.json")
    p_verify.add_argument("--output-dir", required=True, help="Output directory for verified manifest")
    p_verify.add_argument("--force", action="store_true", help="Allow writing into non-empty output dir")
    p_verify.set_defaults(func=_cmd_asset_verify)

    # wse-analyze
    p_wse = sub.add_parser("wse-analyze", help="Run WSE analysis on audio")
    p_wse.add_argument("--input", required=True, help="Path to audio file")
    p_wse.add_argument("--output-dir", required=True, help="Output directory for WSE results")
    p_wse.add_argument("--frame-size", type=int, default=2048, help="FFT frame size")
    p_wse.add_argument("--hop-size", type=int, default=1024, help="Hop size")
    p_wse.add_argument("--force", action="store_true")
    p_wse.set_defaults(func=_cmd_wse_analyze)

    # candidate-plan
    p_plan = sub.add_parser("candidate-plan", help="Generate candidate processing plans")
    p_plan.add_argument("--wse-profile", required=True, help="Path to WSE profile JSON")
    p_plan.add_argument("--output-dir", required=True, help="Output directory for candidate plans")
    p_plan.add_argument("--force", action="store_true")
    p_plan.set_defaults(func=_cmd_candidate_plan)

    # candidate-compare
    p_gen = sub.add_parser("candidate-compare", help="Compare generated candidates")
    p_gen.add_argument("--candidates-dir", required=True, help="Directory containing candidate outputs")
    p_gen.add_argument("--output-dir", required=True, help="Output directory for comparison")
    p_gen.add_argument("--force", action="store_true")
    p_gen.set_defaults(func=_cmd_candidate_compare)

    # report-build
    p_report = sub.add_parser("report-build", help="Build Markdown + HTML report")
    p_report.add_argument("--manifest", required=True, help="Path to session manifest")
    p_report.add_argument("--wse-profile", default="", help="Path to WSE profile JSON")
    p_report.add_argument("--comparison", default="", help="Path to candidate comparison JSON")
    p_report.add_argument("--output-dir", required=True, help="Output directory for reports")
    p_report.add_argument("--force", action="store_true")
    p_report.set_defaults(func=_cmd_report_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
