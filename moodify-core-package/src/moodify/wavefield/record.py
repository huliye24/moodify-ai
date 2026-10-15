"""Case layout and append-only ledger for the Wave Field local lane.

The lane is mounted **inside the existing Studio subtree**
(``<case>/studio/wavefield``) — it never invents a second case root, never
duplicates the original audio, and never keeps its own copy of a measurement.

Layout:

```text
<case>/studio/wavefield/
  session.json            what source + which policy produced this lane
  search.json             the exact search policy document
  candidates/{A,B,C}.wav  rendered field candidates
  fields/{A,B,C}.json     the exact FieldSpec used for each candidate
  renders/{A,B,C}.json    renderer record: hashes, safety gain, engine version
  hearing/ORIGINAL.json   reference hearing (points at the source)
  hearing/{A,B,C}.json    hearing snapshot + technical gate result per candidate
  decisions.jsonl         append-only human choices (idempotent by request_id)
  export/chosen.wav       the chosen render (absent when ORIGINAL was kept)
  export/chosen_field.json
  export/manifest.json    everything needed to reproduce the chosen result
```

``renders/`` is an addition to the minimum tree: the manifest has to cite the
output hash, engine version and any safety gain for the chosen candidate
without re-rendering, and those are render facts, not field facts.
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path

from moodify.auditory.models import utcnow
from moodify.wavefield.models import (
    CANDIDATE_IDS,
    CHOICES,
    DECISION_SCHEMA,
    EXPORT_SCHEMA,
    ROLES,
    SESSION_SCHEMA,
    FieldSpec,
)
from moodify.wavefield.renderer import (
    ENGINE_VERSION,
    RENDERER_ID,
    RenderResult,
    render_file,
    render_result_from_dict,
    render_result_to_dict,
    sha256_file,
)

CASE_SUBDIR: tuple[str, ...] = ("studio", "wavefield")


class WaveFieldRecordError(RuntimeError):
    """A refused ledger / artifact operation, with a machine-readable reason."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def wavefield_dir(case_dir: str | os.PathLike[str]) -> Path:
    return Path(case_dir).joinpath(*CASE_SUBDIR)


def session_path(case_dir) -> Path:
    return wavefield_dir(case_dir) / "session.json"


def search_path(case_dir) -> Path:
    return wavefield_dir(case_dir) / "search.json"


def candidates_dir(case_dir) -> Path:
    return wavefield_dir(case_dir) / "candidates"


def fields_dir(case_dir) -> Path:
    return wavefield_dir(case_dir) / "fields"


def renders_dir(case_dir) -> Path:
    return wavefield_dir(case_dir) / "renders"


def hearing_dir(case_dir) -> Path:
    return wavefield_dir(case_dir) / "hearing"


def decisions_path(case_dir) -> Path:
    return wavefield_dir(case_dir) / "decisions.jsonl"


def export_dir(case_dir) -> Path:
    return wavefield_dir(case_dir) / "export"


def candidate_path(case_dir, candidate_id: str) -> Path:
    _require_candidate(candidate_id)
    return candidates_dir(case_dir) / f"{candidate_id}.wav"


def field_path(case_dir, candidate_id: str) -> Path:
    _require_candidate(candidate_id)
    return fields_dir(case_dir) / f"{candidate_id}.json"


def render_path(case_dir, candidate_id: str) -> Path:
    _require_candidate(candidate_id)
    return renders_dir(case_dir) / f"{candidate_id}.json"


def hearing_path(case_dir, candidate_id: str) -> Path:
    if candidate_id != "ORIGINAL":
        _require_candidate(candidate_id)
    return hearing_dir(case_dir) / f"{candidate_id}.json"


def ensure_layout(case_dir) -> Path:
    root = wavefield_dir(case_dir)
    for directory in (
        root,
        candidates_dir(case_dir),
        fields_dir(case_dir),
        renders_dir(case_dir),
        hearing_dir(case_dir),
        export_dir(case_dir),
    ):
        directory.mkdir(parents=True, exist_ok=True)
    # The append-only ledger exists from the start and stays empty until a human
    # decides.  Creating it here means "no choice yet" is readable state rather
    # than a missing file that has to be guessed at.
    decisions_path(case_dir).touch(exist_ok=True)
    return root


def _require_candidate(candidate_id: str) -> str:
    if candidate_id not in CANDIDATE_IDS:
        raise WaveFieldRecordError(
            "BAD_CANDIDATE", f"{candidate_id!r} is not one of {list(CANDIDATE_IDS)}"
        )
    return candidate_id


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------


def write_json(path: str | os.PathLike[str], data) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def read_json_safe(path: str | os.PathLike[str]):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_case_id(case_dir) -> str:
    data = read_json_safe(Path(case_dir) / "case.json")
    if isinstance(data, Mapping) and data.get("case_id"):
        return str(data["case_id"])
    return Path(case_dir).name


# ---------------------------------------------------------------------------
# Session / search / fields / renders / hearing
# ---------------------------------------------------------------------------


def write_session(
    case_dir,
    *,
    source_path: str,
    source_sha256: str,
    sample_rate: int,
    channels: int,
    frames: int,
    duration_seconds: float,
    policy: Mapping,
    engine_version: str = ENGINE_VERSION,
    renderer: str = RENDERER_ID,
) -> dict:
    document = {
        "schema": SESSION_SCHEMA,
        "case_id": read_case_id(case_dir),
        "source_path": source_path,
        "source_sha256": source_sha256,
        "sample_rate": int(sample_rate),
        "channels": int(channels),
        "frames": int(frames),
        "duration_seconds": float(duration_seconds),
        "policy_id": policy.get("policy_id"),
        "policy_version": policy.get("policy_version"),
        "calibration_status": policy.get("calibration_status"),
        "engine_version": engine_version,
        "renderer": renderer,
        "created_at": utcnow(),
    }
    ensure_layout(case_dir)
    write_json(session_path(case_dir), document)
    write_json(search_path(case_dir), dict(policy))
    return document


def read_session(case_dir):
    return read_json_safe(session_path(case_dir))


def read_search(case_dir):
    return read_json_safe(search_path(case_dir))


def write_field(case_dir, candidate_id: str, field: FieldSpec) -> Path:
    """Store a candidate's field record as ``fields/<candidate>.json``.

    The file is named after the *candidate* so the layout stays
    ``fields/A.json``; the record inside carries the ``field_id``.
    """
    ensure_layout(case_dir)
    _require_candidate(candidate_id)
    target = field_path(case_dir, candidate_id)
    write_json(target, field.to_dict())
    return target


def read_field(case_dir, candidate_id: str):
    """The stored field, or ``None``.  Reads never raise: absence is data."""
    try:
        data = read_json_safe(field_path(case_dir, candidate_id))
    except WaveFieldRecordError:
        return None
    if data is None:
        return None
    try:
        return FieldSpec.from_dict(data)
    except ValueError:
        return None


def write_render(case_dir, candidate_id: str, result: RenderResult) -> Path:
    return write_json(render_path(case_dir, candidate_id), result.to_dict())


def read_render(case_dir, candidate_id: str):
    try:
        data = read_json_safe(render_path(case_dir, candidate_id))
    except WaveFieldRecordError:
        return None
    return render_result_from_dict(data) if data else None


def write_hearing(case_dir, candidate_id: str, snapshot: Mapping) -> Path:
    return write_json(hearing_path(case_dir, candidate_id), dict(snapshot))


def read_hearing(case_dir, candidate_id: str):
    try:
        return read_json_safe(hearing_path(case_dir, candidate_id))
    except WaveFieldRecordError:
        return None


# ---------------------------------------------------------------------------
# Decisions (append-only, idempotent)
# ---------------------------------------------------------------------------


def read_decisions(case_dir) -> list[dict]:
    path = decisions_path(case_dir)
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue  # a torn line must not invalidate the rest of the ledger
    return rows


def decision_for(case_dir, request_id: str | None = None):
    rows = read_decisions(case_dir)
    if request_id:
        for row in rows:
            if row.get("request_id") == request_id:
                return row
        return None
    return rows[-1] if rows else None


def append_decision(
    case_dir,
    *,
    kept: str,
    role: str,
    request_id: str | None = None,
    candidate: Mapping | None = None,
    field: Mapping | None = None,
    source_sha256: str | None = None,
    engine_version: str = ENGINE_VERSION,
    renderer: str = RENDERER_ID,
) -> dict:
    """Append one human choice.  Never rewrites, never reorders.

    Returns ``{"record": ..., "created": bool}``.  A repeated ``request_id``
    returns the original record and writes nothing — retrying a request must
    not produce a second decision.
    """
    if kept not in CHOICES:
        raise WaveFieldRecordError("BAD_KEPT", f"{kept!r} is not one of {list(CHOICES)}")
    if role not in ROLES:
        raise WaveFieldRecordError("BAD_ROLE", f"{role!r} is not one of {list(ROLES)}")

    existing = decision_for(case_dir, request_id) if request_id else None
    if existing is not None:
        return {"record": existing, "created": False}

    ensure_layout(case_dir)
    record = {
        "schema": DECISION_SCHEMA,
        "case_id": read_case_id(case_dir),
        "request_id": request_id,
        "kept": kept,
        "role": role,
        "candidate": dict(candidate) if candidate else None,
        "field": dict(field) if field else None,
        "source_sha256": source_sha256,
        "engine_version": engine_version,
        "renderer": renderer,
        "decided_at": utcnow(),
        "note": (
            "human artistic authority; the machine records the choice and never "
            "grants artistic approval"
        ),
    }
    with decisions_path(case_dir).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return {"record": record, "created": True}


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def export_chosen(case_dir, *, kept: str | None = None) -> dict:
    """Materialise the chosen result into ``export/`` and write the manifest.

    Refuses when there is no recorded decision: export must never run ahead of
    the human choice.  ``ORIGINAL`` is exported as a **reference to the source**
    (no duplicated audio); A/B/C are exported as the rendered WAV.
    """
    session = read_session(case_dir)
    if not session:
        raise WaveFieldRecordError("SESSION_MISSING", "no wavefield session to export")
    decision = decision_for(case_dir)
    if not decision:
        raise WaveFieldRecordError("NOT_CHOSEN", "a choice must be recorded before export")
    if kept is not None and decision.get("kept") != kept:
        raise WaveFieldRecordError(
            "NOT_CHOSEN",
            f"latest decision is {decision.get('kept')!r}, not {kept!r}",
        )
    kept = decision["kept"]

    out_dir = export_dir(case_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    source_path = session["source_path"]

    manifest = {
        "schema": EXPORT_SCHEMA,
        "case_id": session.get("case_id"),
        "kept": kept,
        "policy_id": session.get("policy_id"),
        "policy_version": session.get("policy_version"),
        "calibration_status": session.get("calibration_status"),
        "source_path": source_path,
        "source_sha256": session.get("source_sha256") or sha256_file(source_path),
        "renderer": session.get("renderer", RENDERER_ID),
        "engine_version": session.get("engine_version", ENGINE_VERSION),
        "sample_rate": session.get("sample_rate"),
        "channels": session.get("channels"),
        "frames": session.get("frames"),
        "duration_seconds": session.get("duration_seconds"),
        "hearing_ref": None,
        "chosen_audio": None,
        "chosen_audio_sha256": None,
        "chosen_field": None,
        "chosen_field_hash": None,
        "safety_gain_db": 0.0,
        "reproduce": {
            "how": "render the stored FieldSpec from the stored source with the recorded renderer",
            "source_path": source_path,
            "field_record": None,
            "renderer": session.get("renderer", RENDERER_ID),
            "determinism": "deterministic within the recorded library versions and float rounding",
        },
        "decision": decision,
        "decided_at": decision.get("decided_at"),
        "created_at": utcnow(),
        "limitations": [
            "perceptual virtual acoustic field, not a physically exact propagation simulation",
            "a stereo render is a projection, not a measured three-dimensional sound field",
            f"field parameters are {session.get('calibration_status')}",
        ],
    }

    if kept == "ORIGINAL":
        manifest["export_mode"] = "REFERENCE_TO_SOURCE"
        chosen_field = {
            "schema": "moodify.wavefield.chosen/0.1",
            "kept": "ORIGINAL",
            "field": None,
            "reason": "no field was applied; the source audio itself is the chosen result",
            "source_path": source_path,
            "source_sha256": manifest["source_sha256"],
        }
        write_json(out_dir / "chosen_field.json", chosen_field)
        stale = out_dir / "chosen.wav"
        if stale.exists():
            stale.unlink()  # a previous field export must not linger beside an ORIGINAL choice
    else:
        candidate_audio = candidate_path(case_dir, kept)
        if not candidate_audio.is_file():
            raise WaveFieldRecordError("CANDIDATE_MISSING", f"{candidate_audio} not rendered")
        field = read_field(case_dir, kept)
        if field is None:
            raise WaveFieldRecordError("FIELD_MISSING", f"fields/{kept}.json is unreadable")
        render = read_render(case_dir, kept)

        chosen_audio = out_dir / "chosen.wav"
        shutil.copyfile(candidate_audio, chosen_audio)
        chosen_field = {
            "schema": "moodify.wavefield.chosen/0.1",
            "kept": kept,
            "field": field.to_dict(),
            "engine_version": manifest["engine_version"],
            "renderer": manifest["renderer"],
            "safety_gain_db": render.safety_gain_db if render else 0.0,
        }
        write_json(out_dir / "chosen_field.json", chosen_field)

        manifest.update(
            export_mode="RENDERED_FIELD",
            hearing_ref=f"hearing/{kept}.json",
            chosen_audio=str(chosen_audio),
            chosen_audio_sha256=sha256_file(chosen_audio),
            chosen_field=field.to_dict(),
            chosen_field_hash=field.field_hash(),
            safety_gain_db=render.safety_gain_db if render else 0.0,
        )
        manifest["reproduce"]["field_record"] = str(field_path(case_dir, kept))

    write_json(out_dir / "manifest.json", manifest)
    return manifest


def read_export(case_dir):
    return read_json_safe(export_dir(case_dir) / "manifest.json")


def reproduce_chosen(case_dir, output_path: str | os.PathLike[str] | None = None) -> dict:
    """Re-render the chosen field from the stored record and verify the hash.

    This is the executable form of the reproducibility requirement:
    ``source + chosen_field.json + renderer version = the same render``.

    With no ``output_path`` the re-render is written to a scratch file, hashed,
    and removed again — verification must not leave derived audio inside the
    documented export tree.
    """
    import tempfile

    manifest = read_export(case_dir)
    if not manifest:
        raise WaveFieldRecordError("EXPORT_MISSING", "nothing has been exported yet")
    kept = manifest["kept"]

    if kept == "ORIGINAL":
        reproduced_sha = sha256_file(manifest["source_path"])
        expected = manifest["source_sha256"]
        return {
            "ok": reproduced_sha == expected,
            "kept": kept,
            "mode": "REFERENCE_TO_SOURCE",
            "expected_sha256": expected,
            "reproduced_sha256": reproduced_sha,
            "output_path": manifest["source_path"],
            "render": None,
        }

    field = read_field(case_dir, kept)
    if field is None:
        raise WaveFieldRecordError("FIELD_MISSING", f"fields/{kept}.json is unreadable")

    scratch = output_path is None
    if scratch:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as handle:
            target = Path(handle.name)
    else:
        target = Path(output_path)

    try:
        result = render_file(manifest["source_path"], field, target)
        expected = manifest.get("chosen_audio_sha256")
        return {
            "ok": expected is None or result.output_sha256 == expected,
            "kept": kept,
            "mode": "RENDERED_FIELD",
            "expected_sha256": expected,
            "reproduced_sha256": result.output_sha256,
            "output_path": None if scratch else str(target),
            "scratch": scratch,
            "render": render_result_to_dict(result),
        }
    finally:
        if scratch:
            try:
                target.unlink()
            except OSError:  # pragma: no cover - best effort cleanup
                pass


# ---------------------------------------------------------------------------
# Inspection (the desktop's read surface)
# ---------------------------------------------------------------------------


def _artifact(path: Path) -> dict:
    row = {
        "path": str(path),
        "exists": path.is_file(),
        "sha256": None,
        "size": None,
        "mtime": None,
    }
    if row["exists"]:
        try:
            stat = path.stat()
            row["size"] = stat.st_size
            row["mtime"] = stat.st_mtime
            row["sha256"] = sha256_file(path)
        except OSError:  # pragma: no cover - raced deletion
            row["exists"] = False
    return row


def inspect(case_dir) -> dict:
    """Current Wave Field state, derived from disk only.

    Nothing is cached and nothing is inferred: absent artifacts are reported as
    absent, and ``blockers`` explains why a next action is locked.
    """
    root = wavefield_dir(case_dir)
    session = read_session(case_dir)
    search = read_search(case_dir)
    if not root.is_dir():
        return {
            "present": False,
            "case_dir": str(case_dir),
            "wavefield_dir": str(root),
            "session": None,
            "search": None,
            "fields": {},
            "candidates": {},
            "hearing": {},
            "judgment": {},
            "decisions": [],
            "chosen": None,
            "export": None,
            "blockers": ["NO_WAVEFIELD_SESSION"],
            "warnings": [],
        }

    fields: dict[str, dict | None] = {}
    candidates: dict[str, dict] = {}
    hearing: dict[str, dict | None] = {}
    judgment: dict[str, dict | None] = {}
    warnings: list[str] = []

    for candidate_id in CANDIDATE_IDS:
        spec = read_field(case_dir, candidate_id)
        fields[candidate_id] = spec.to_dict() if spec else None
        row = _artifact(candidate_path(case_dir, candidate_id))
        render = read_render(case_dir, candidate_id)
        row["render"] = render_result_to_dict(render) if render else None
        if row["exists"] and row["sha256"] and render and render.output_sha256 != row["sha256"]:
            row["stale"] = True
            warnings.append(f"{candidate_id}_STALE")
        else:
            row["stale"] = False
        candidates[candidate_id] = row

    # Every出口 gets a hearing entry — including ORIGINAL, which is the baseline.
    for identifier in ("ORIGINAL", *CANDIDATE_IDS):
        hearing[identifier] = read_hearing(case_dir, identifier)
        judgment[identifier] = (hearing[identifier] or {}).get("judge")

    decisions = read_decisions(case_dir)
    chosen = decisions[-1] if decisions else None
    export = read_export(case_dir)

    blockers: list[str] = []
    if not session:
        blockers.append("SESSION_MISSING")
    if all(not candidates[cid]["exists"] for cid in CANDIDATE_IDS):
        blockers.append("NO_CANDIDATES")
    if not chosen:
        blockers.append("NOT_CHOSEN")
    elif chosen["kept"] != "ORIGINAL" and not candidates[chosen["kept"]]["exists"]:
        blockers.append("CHOSEN_CANDIDATE_MISSING")

    return {
        "present": True,
        "case_dir": str(case_dir),
        "wavefield_dir": str(root),
        "session": session,
        "search": search,
        "fields": fields,
        "candidates": candidates,
        "hearing": hearing,
        "judgment": judgment,
        "decisions": decisions,
        "chosen": chosen,
        "export": export,
        "blockers": blockers,
        "warnings": warnings,
        "choices": list(CHOICES),
    }


def summarize_hearing(snapshot: Mapping | None) -> dict | None:
    """The numbers the minimum UI shows, taken verbatim from the snapshot."""
    if not snapshot:
        return None
    metrics = snapshot.get("metrics") or {}
    from moodify.wavefield.hearing import summarize

    judge_block = snapshot.get("judge") or {}
    return {
        **summarize(metrics),
        "technical_status": judge_block.get("technical_status"),
        "blocking_flags": judge_block.get("blocking_flags") or [],
        "warnings": judge_block.get("warnings") or [],
        "audition_correction_db": (snapshot.get("source_comparison") or {}).get(
            "audition_correction_db"
        )
        if snapshot.get("source_comparison")
        else None,
    }


def candidate_choices(case_dir) -> Sequence[dict]:
    """ORIGINAL + the three probes, with availability, for a UI to render."""
    rows = [
        {
            "id": "ORIGINAL",
            "label": "原版",
            "available": True,
            "path": (read_session(case_dir) or {}).get("source_path"),
            "field": None,
        }
    ]
    for candidate_id in CANDIDATE_IDS:
        path = candidate_path(case_dir, candidate_id)
        spec = read_field(case_dir, candidate_id)
        rows.append(
            {
                "id": candidate_id,
                "label": candidate_id,
                "available": path.is_file(),
                "path": str(path) if path.is_file() else None,
                "field": spec.to_dict() if spec else None,
            }
        )
    return rows
