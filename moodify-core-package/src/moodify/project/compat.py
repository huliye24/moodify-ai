"""Read-only compatibility bridge: existing case directories → Project Model view.

WHY THIS EXISTS (THINKPAD 002 / PRODUCT_REALIGNMENT_001 §16 Phase 2)
    Two realities coexist in this repository: historical/current case
    directories (Core bundles, Studio subtrees, the legacy numbered WSE layout)
    and the canonical Song Project model. Rewriting historical data would
    destroy provenance; ignoring historical cases would make the new model
    unusable against real work. This module is the third option: a reader that
    inspects recognised layouts and expresses what can be known about them
    through the Project Model vocabulary.

BOUNDARY — asserted by tests, not only documented
    - never writes: reading a case twice leaves every byte on disk unchanged;
    - never invents: a recorded hash is verified against the actual file, and a
      missing file is a problem, never an empty success;
    - never guesses: an unrecognised layout is UNSUPPORTED with a reason, and an
      unrecognised schema string is preserved as unknown, not interpreted;
    - never repairs: a tampered artifact is reported loudly, never re-hashed
      into agreement and never rewritten.

The vocabulary sections come from ``RESERVED_SECTIONS`` (moodify.project/0.1).
Each artifact additionally keeps the exact role it was observed in (``kind``),
because the reserved sections carry no schema yet and this reader refuses to
invent one.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..contracts.hashing import sha256_file
from ..sound_protocol import AUDIO_EXTENSIONS
from .errors import ProjectError, ProjectIntegrityError, ProjectValidationError
from .models import PROJECT_PROTOCOL, RESERVED_SECTIONS
from .service import MANIFEST_NAME, load_project

# ── recognised layouts ─────────────────────────────────────────────────────────

#: Canonical Song Project (``moodify.project/0.1``, create_project/load_project).
LAYOUT_PROJECT = "moodify_project_0_1"
#: Core auditory case bundle (release.analyze_to_case; report.json + scan/).
LAYOUT_CORE_CASE = "core_auditory_case"
#: Core bundle plus the Studio subtree (studio/, stems/, midi/, finishing/…).
LAYOUT_STUDIO_CASE = "studio_case"
#: Legacy numbered WSE case (00_source/ … 07_learning/).
LAYOUT_LEGACY_WSE = "legacy_wse_case"

#: Inspection status vocabulary (THINKPAD 002 §5E). UNSUPPORTED wins over
#: CORRUPT over INCOMPLETE over RECOGNIZED — the loudest truth is reported.
STATUS_RECOGNIZED = "RECOGNIZED"
STATUS_INCOMPLETE = "INCOMPLETE"
STATUS_CORRUPT = "CORRUPT"
STATUS_UNSUPPORTED = "UNSUPPORTED"

#: Schema strings this reader is willing to interpret. Anything else is
#: preserved as unknown instead of being read as if it were a known version
#: (§6: "unknown semantic version must not be silently accepted").
KNOWN_SCHEMAS = frozenset({
    PROJECT_PROTOCOL,
    "moodify.msp_report/0.2",
    "moodify.studio.meta/0.1",
    "moodify.studio.diagnosis/0.1",
    "moodify.studio.context/0.1",
    "moodify.studio.plan/0.1",
    "moodify.studio.finish-mode/0.1",
    "moodify.studio.pipeline/0.1",
    "moodify.studio.selection/0.1",
})

#: Canonical ProductionCase schema (case.json:schema_version).
_CASE_SCHEMA_VERSION = "1.0"

#: How many unreferenced file names are reported before the list is capped
#: (names only; the count is always exact).
_IGNORED_FILES_CAP = 50

#: Audio suffix set, lowercase, for on-disk probing (fixtures may use any
#: member of the canonical set — the reader hashes bytes and never decodes).
_AUDIO_SUFFIXES = tuple(sorted(AUDIO_EXTENSIONS))


# ── records ───────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ArtifactRef:
    """One file a layout records or contains, addressed case-relative.

    ``recorded_sha256`` is what the layout *claims*; ``verified`` is what this
    reader *checked* (None = no recorded hash to check against). A file that a
    layout records but does not contain is reported as ``exists=False`` — the
    difference between "missing" and "successful" is the point.
    """

    logical_path: str
    kind: str
    exists: bool
    size_bytes: int | None
    recorded_sha256: str | None = None
    verified: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "exists": self.exists,
            "kind": self.kind,
            "logical_path": self.logical_path,
            "recorded_sha256": self.recorded_sha256,
            "size_bytes": self.size_bytes,
            "verified": self.verified,
        }


@dataclass(frozen=True)
class SourceRef:
    """What can be known about the source audio of the inspected object.

    ``origin``: ``project_copy`` (a verified copy inside the project),
    ``in_case`` (a file inside the case, e.g. the legacy 00_source/ layout),
    ``external_path`` (a recorded path outside the case, verified when the
    file exists), or ``case_record`` (only a recorded digest, no file to read).
    """

    origin: str
    logical_path: str | None
    path: str | None
    original_name: str | None
    size_bytes: int | None
    recorded_sha256: str | None
    verified: bool | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "logical_path": self.logical_path,
            "origin": self.origin,
            "original_name": self.original_name,
            "path": self.path,
            "recorded_sha256": self.recorded_sha256,
            "size_bytes": self.size_bytes,
            "verified": self.verified,
        }


@dataclass(frozen=True)
class CaseProblem:
    """A fact the reader refuses to paper over.

    ``severity`` is ``"corrupt"`` (unreadable / invalid / tampered / conflicting
    — the object cannot be trusted) or ``"incomplete"`` (a recorded piece is
    absent — the object is trusted but not whole).
    """

    code: str
    message: str
    severity: str

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "severity": self.severity}


@dataclass(frozen=True)
class CaseInspection:
    """The normalized read-only view of one case/project directory."""

    root: str
    layout: str
    status: str
    case_id: str | None
    name: str | None
    source: SourceRef | None
    sections: dict[str, tuple[ArtifactRef, ...]]
    unknowns: tuple[str, ...]
    problems: tuple[CaseProblem, ...]
    ignored_files: tuple[str, ...]
    ignored_file_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "ignored_file_count": self.ignored_file_count,
            "ignored_files": list(self.ignored_files),
            "layout": self.layout,
            "name": self.name,
            "problems": [p.to_dict() for p in self.problems],
            "root": self.root,
            "sections": {
                name: [a.to_dict() for a in refs] for name, refs in self.sections.items()
            },
            "source": self.source.to_dict() if self.source is not None else None,
            "status": self.status,
            "unknowns": list(self.unknowns),
        }


# ── accumulator ───────────────────────────────────────────────────────────────

class _Acc:
    """Collects problems, unknowns, artifacts and referenced paths for one read."""

    def __init__(self) -> None:
        self.problems: list[CaseProblem] = []
        self.unknowns: list[str] = []
        self.referenced: set[str] = set()
        self._sections: dict[str, list[ArtifactRef]] = {
            name: [] for name in RESERVED_SECTIONS
        }

    def problem(self, code: str, message: str, severity: str) -> None:
        self.problems.append(CaseProblem(code=code, message=message, severity=severity))

    def unknown(self, note: str) -> None:
        if note not in self.unknowns:
            self.unknowns.append(note)

    def add(self, section: str, ref: ArtifactRef) -> None:
        if section not in self._sections:
            raise ProjectValidationError(f"unknown section: {section}")
        self._sections[section].append(ref)
        self.referenced.add(ref.logical_path)

    def reference(self, logical_path: str) -> None:
        """Mark a path as accounted for without publishing it as an artifact."""
        self.referenced.add(logical_path)

    def sections(self) -> dict[str, tuple[ArtifactRef, ...]]:
        return {
            name: tuple(sorted(refs, key=lambda r: (r.logical_path, r.kind)))
            for name, refs in self._sections.items()
        }


# ── small helpers ─────────────────────────────────────────────────────────────

def _norm_sha(value: Any) -> str | None:
    """Normalize a recorded hash to canonical ``sha256:<64 lowercase hex>``.

    Layouts disagree on the format (``sha256:``-prefixed in case.json and
    report.json, bare hex in scan manifests). Comparing unnormalized strings
    would report identical digests as conflicts, so both sides go through here.
    Returns None for anything that is not a well-formed sha256.
    """
    if not isinstance(value, str):
        return None
    text = value.strip().lower()
    if text.startswith("sha256:"):
        text = text[len("sha256:"):]
    if len(text) != 64 or any(c not in "0123456789abcdef" for c in text):
        return None
    return "sha256:" + text


def _read_json(path: Path) -> Any | None:
    """Parse JSON or return None. Callers decide the problem; this never raises."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def _list_files(directory: Path, suffixes: tuple[str, ...] | None = None) -> list[Path]:
    """Direct child files, sorted; suffix match is lowercase, None = all."""
    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name)
    except OSError:
        return []
    out = []
    for entry in entries:
        if not entry.is_file():
            continue
        if suffixes is None or entry.name.lower().endswith(suffixes):
            out.append(entry)
    return out


def _list_dirs(directory: Path) -> list[Path]:
    try:
        return sorted((p for p in directory.iterdir() if p.is_dir()), key=lambda p: p.name)
    except OSError:
        return []


def _rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _add_artifact(
    acc: _Acc,
    root: Path,
    section: str,
    path: Path,
    kind: str,
    recorded: Any = None,
) -> None:
    """Reference one on-disk file; a recorded hash (when present) is verified."""
    norm = _norm_sha(recorded)
    exists = path.is_file()
    size: int | None = None
    verified: bool | None = None
    if exists:
        size = path.stat().st_size
        if norm is not None:
            verified = sha256_file(path) == norm
    acc.add(section, ArtifactRef(
        logical_path=_rel(root, path),
        kind=kind,
        exists=exists,
        size_bytes=size,
        recorded_sha256=norm,
        verified=verified,
    ))
    if not exists and recorded is not None:
        acc.problem("ARTIFACT_MISSING",
                    f"recorded artifact is missing: {_rel(root, path)}", "incomplete")
    if verified is False:
        acc.problem("ARTIFACT_TAMPERED",
                    f"recorded hash does not match the file on disk: {_rel(root, path)}",
                    "corrupt")


def _recorded_scan_artifact(
    acc: _Acc,
    root: Path,
    scan_dir: Path,
    name: str,
    record: Any,
    kind: str,
) -> None:
    """Reference a scan artifact; scan artifacts land in the ``analysis`` section.

    The recorded ``path`` is untrusted input (the committed golden case even
    records a path from another machine). Only its **basename** is used, joined
    to the scan directory — a recorded path can therefore never direct a read
    outside the case, and a stale absolute path still verifies against the file
    that is actually there.
    """
    recorded_path = record.get("path") if isinstance(record, dict) else None
    basename = Path(str(recorded_path)).name if recorded_path else ""
    if not basename:
        acc.problem("ARTIFACT_RECORD_MALFORMED",
                    f"scan manifest entry '{name}' records no usable file name",
                    "incomplete")
        return
    recorded_sha = record.get("sha256") if isinstance(record, dict) else None
    _add_artifact(acc, root, "analysis", scan_dir / basename, kind, recorded_sha)


def _note_schema(acc: _Acc, logical_path: str, schema: Any) -> None:
    """Record an unrecognised schema as unknown; known/absent schemas pass."""
    if schema is None:
        return
    if not isinstance(schema, str) or schema not in KNOWN_SCHEMAS:
        acc.unknown(
            f"{logical_path} declares schema {schema!r}, which this reader does not "
            f"interpret; the file is recorded but its contents are not normalized"
        )


def _verify_scan_dir(acc: _Acc, root: Path, scan_dir: Path) -> None:
    """Verify the artifacts a scan_manifest.json records inside *scan_dir*."""
    manifest_path = scan_dir / "scan_manifest.json"
    if not manifest_path.is_file():
        return
    manifest = _read_json(manifest_path)
    if manifest is None:
        acc.problem("SCAN_MANIFEST_UNREADABLE",
                    f"{_rel(root, manifest_path)} exists but does not parse", "corrupt")
        return
    if not isinstance(manifest, dict):
        return
    artifacts = manifest.get("artifacts")
    if isinstance(artifacts, dict):
        for name in sorted(artifacts):
            _recorded_scan_artifact(acc, root, scan_dir, name,
                                    artifacts[name], "analysis.scan_artifact")


# ── layout detection ──────────────────────────────────────────────────────────

def detect_layout(root: Path) -> str | None:
    """Recognised layout of *root*, or None when nothing matches.

    Detection is by marker files only, never by guessing from partial content.
    Priority: project → studio case → core case → legacy WSE.
    """
    if (root / MANIFEST_NAME).is_file():
        return LAYOUT_PROJECT
    case_markers = (
        (root / "case.json").is_file()
        or (root / "report.json").is_file()
        or (root / "scan").is_dir()
    )
    if case_markers and (root / "studio").is_dir():
        return LAYOUT_STUDIO_CASE
    if case_markers:
        return LAYOUT_CORE_CASE
    if (root / "00_source").is_dir():
        return LAYOUT_LEGACY_WSE
    return None


# ── public entry ──────────────────────────────────────────────────────────────

def inspect_case(root: str | Path) -> CaseInspection:
    """Inspect one case/project directory without modifying a single byte.

    Raises :class:`ProjectValidationError` only when *root* itself is not a
    directory; every layout-level problem is data (status + problems), not an
    exception.
    """
    target = Path(root)
    if not target.is_dir():
        raise ProjectValidationError(f"not a directory: {target}")
    resolved = target.resolve()

    layout = detect_layout(resolved)
    if layout is None:
        acc = _Acc()
        acc.problem(
            "UNSUPPORTED_LAYOUT",
            "no recognised layout marker found (expected project.json, case.json/"
            "report.json/scan/, studio/, or the legacy 00_source/ layout)",
            "incomplete",
        )
        return _finish(resolved, layout=STATUS_UNSUPPORTED, case_id=None, name=None,
                       source=None, acc=acc)

    if layout == LAYOUT_PROJECT:
        return _inspect_project(resolved)
    if layout == LAYOUT_LEGACY_WSE:
        return _inspect_legacy(resolved)
    return _inspect_case_bundle(resolved, layout)


def _finish(
    root: Path,
    *,
    layout: str,
    case_id: str | None,
    name: str | None,
    source: SourceRef | None,
    acc: _Acc,
) -> CaseInspection:
    problems = tuple(acc.problems)
    if layout == STATUS_UNSUPPORTED:
        status = STATUS_UNSUPPORTED
    elif any(p.severity == "corrupt" for p in problems):
        status = STATUS_CORRUPT
    elif problems:
        status = STATUS_INCOMPLETE
    else:
        status = STATUS_RECOGNIZED

    ignored, ignored_count = _collect_ignored(root, acc.referenced)
    return CaseInspection(
        root=str(root),
        layout=layout,
        status=status,
        case_id=case_id,
        name=name,
        source=source,
        sections=acc.sections(),
        unknowns=tuple(sorted(acc.unknowns)),
        problems=problems,
        ignored_files=ignored,
        ignored_file_count=ignored_count,
    )


def _collect_ignored(root: Path, referenced: set[str]) -> tuple[tuple[str, ...], int]:
    """Files not referenced by any record — extra files never invalidate a case."""
    leftovers: list[str] = []
    count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = _rel(root, path)
        if rel in referenced:
            continue
        count += 1
        if len(leftovers) < _IGNORED_FILES_CAP:
            leftovers.append(rel)
    return tuple(leftovers), count


# ── L1: Song Project ──────────────────────────────────────────────────────────

def _inspect_project(root: Path) -> CaseInspection:
    acc = _Acc()
    try:
        manifest = load_project(root)
    except ProjectIntegrityError as exc:
        acc.problem("PROJECT_SOURCE_UNVERIFIED", str(exc), "corrupt")
        return _finish(root, layout=LAYOUT_PROJECT, case_id=None, name=None,
                       source=None, acc=acc)
    except ProjectError as exc:
        acc.problem("PROJECT_MANIFEST_INVALID", str(exc), "corrupt")
        return _finish(root, layout=LAYOUT_PROJECT, case_id=None, name=None,
                       source=None, acc=acc)

    asset = manifest.source
    copy_path = root / asset.logical_path
    source = SourceRef(
        origin="project_copy",
        logical_path=asset.logical_path,
        path=str(copy_path.resolve()),
        original_name=asset.original_name,
        size_bytes=asset.size_bytes,
        recorded_sha256=asset.content_hash,
        verified=True,  # load_project re-verified size and digest just now
    )
    acc.reference(MANIFEST_NAME)
    acc.reference(asset.logical_path)

    populated = [name for name in RESERVED_SECTIONS if getattr(manifest, name)]
    if not populated:
        acc.unknown(
            "moodify.project/0.1 reserves its sections without a schema; all "
            "sections are empty here, so no production artifacts are recorded"
        )
    for name in populated:
        acc.unknown(
            f"project section '{name}' is non-empty, but moodify.project/0.1 "
            f"defines no schema for it; contents are not normalized"
        )
    return _finish(root, layout=LAYOUT_PROJECT, case_id=manifest.project_id,
                   name=manifest.display_name, source=source, acc=acc)


# ── L2/L3: Core case bundle ± Studio subtree ──────────────────────────────────

@dataclass
class _BundleState:
    """Identity accumulated across a bundle's records while reading it."""

    case_id: str | None = None
    recorded_source: str | None = None
    lifecycle: str | None = None


def _read_case_record(acc: _Acc, root: Path, state: _BundleState) -> None:
    """Read case.json — the ProductionCase record."""
    case_json_path = root / "case.json"
    case_record = _read_json(case_json_path) if case_json_path.is_file() else None
    if case_json_path.is_file() and case_record is None:
        acc.problem("CASE_RECORD_UNREADABLE", "case.json exists but does not parse",
                    "corrupt")
    if not isinstance(case_record, dict):
        return
    acc.reference("case.json")
    if isinstance(case_record.get("case_id"), str):
        state.case_id = case_record["case_id"]
    state.recorded_source = _norm_sha(case_record.get("source_id"))
    if state.recorded_source is None:
        acc.problem("SOURCE_RECORD_MALFORMED",
                    "case.json source_id is not a well-formed sha256 digest",
                    "corrupt")
    if isinstance(case_record.get("lifecycle_state"), str):
        state.lifecycle = case_record["lifecycle_state"]
    schema_version = case_record.get("schema_version")
    if schema_version is not None and schema_version != _CASE_SCHEMA_VERSION:
        acc.unknown(
            f"case.json declares schema_version {schema_version!r} (recognised: "
            f"{_CASE_SCHEMA_VERSION!r}); fields are recorded as-is, not interpreted"
        )


def _read_analysis_report(acc: _Acc, root: Path, state: _BundleState) -> Any:
    """Read report.json — the analysis authority — and merge its identity."""
    report_path = root / "report.json"
    if not report_path.is_file():
        code = ("ANALYSIS_NOT_COMPLETED" if state.lifecycle == "ACTIVE"
                else "ANALYSIS_REPORT_MISSING")
        acc.problem(code, "no report.json — the analysis stage has no result on disk",
                    "incomplete")
        return None
    report = _read_json(report_path)
    if report is None:
        acc.problem("ANALYSIS_REPORT_UNREADABLE",
                    "report.json exists but does not parse", "corrupt")
        return None
    _add_artifact(acc, root, "analysis", report_path, "analysis.report")
    if isinstance(report, dict):
        _note_schema(acc, "report.json", report.get("protocol"))
        _merge_report_identity(acc, state, report)
    return report


def _merge_report_identity(acc: _Acc, state: _BundleState, report: dict[str, Any]) -> None:
    """Cross-check the report's case id and source digest against case.json."""
    report_case = report.get("case") if isinstance(report.get("case"), dict) else {}
    report_id = report_case.get("case_id")
    if isinstance(report_id, str):
        if state.case_id is not None and report_id != state.case_id:
            acc.problem("CASE_ID_CONFLICT",
                        f"case.json says {state.case_id!r} but report.json says "
                        f"{report_id!r}", "corrupt")
        state.case_id = state.case_id or report_id
    report_source = (report.get("source")
                     if isinstance(report.get("source"), dict) else {})
    report_sha = _norm_sha(report_source.get("sha256"))
    if state.recorded_source and report_sha and report_sha != state.recorded_source:
        acc.problem("SOURCE_HASH_CONFLICT",
                    "case.json source_id and report.json source.sha256 "
                    "disagree", "corrupt")
    state.recorded_source = state.recorded_source or report_sha


def _read_scan_subtree(acc: _Acc, root: Path, state: _BundleState) -> None:
    """Read scan/ — the artifact hashes live in its scan_manifest.json."""
    scan_dir = root / "scan"
    if not scan_dir.is_dir():
        return
    manifest_path = scan_dir / "scan_manifest.json"
    scan_manifest = _read_json(manifest_path) if manifest_path.is_file() else None
    if isinstance(scan_manifest, dict):
        manifest_input = _norm_sha(scan_manifest.get("input_sha256"))
        if state.recorded_source and manifest_input and manifest_input != state.recorded_source:
            acc.problem("SOURCE_HASH_CONFLICT",
                        "scan_manifest.json input_sha256 disagrees with the case "
                        "source digest", "corrupt")
        state.recorded_source = state.recorded_source or manifest_input
        input_path = scan_manifest.get("input_path")
        if isinstance(input_path, str) and not Path(input_path).is_file():
            acc.unknown(
                "scan_manifest.json input_path is an absolute path from scan "
                "time and does not resolve here; the source is located by "
                "digest, not by that path"
            )
    _verify_scan_dir(acc, root, scan_dir)
    _collect_scan_files(acc, root, scan_dir)


def _collect_scan_files(acc: _Acc, root: Path, scan_dir: Path) -> None:
    """Reference scan/ files the manifest did not already cover."""
    for path in _list_files(scan_dir):
        rel = _rel(root, path)
        if rel in acc.referenced:
            continue
        kind = ("analysis.scan_manifest" if path.name == "scan_manifest.json"
                else "analysis.scan_file")
        _add_artifact(acc, root, "analysis", path, kind)


#: Optional sibling files of the Core bundle (derived renders and record copies).
_BUNDLE_EXTRAS = (
    ("report.md", "analysis.report_markdown"),
    ("report.html", "analysis.report_html"),
    ("measurements.json", "analysis.measurements"),
    ("evidence.json", "analysis.evidence"),
    ("judgment_rules.json", "analysis.judgment_rules"),
    ("auditory_report.json", "analysis.auditory_report"),
)


def _read_bundle_extras(acc: _Acc, root: Path) -> None:
    for name, kind in _BUNDLE_EXTRAS:
        path = root / name
        if path.is_file():
            _add_artifact(acc, root, "analysis", path, kind)


def _case_display_name(report: Any, source: SourceRef | None) -> str | None:
    """The best display name the bundle itself carries (never invented)."""
    if isinstance(report, dict):
        report_source = report.get("source") if isinstance(report.get("source"), dict) else {}
        if isinstance(report_source.get("name"), str):
            return report_source["name"]
    if source is not None:
        return source.original_name or source.logical_path
    return None


def _inspect_case_bundle(root: Path, layout: str) -> CaseInspection:
    acc = _Acc()
    state = _BundleState()
    _read_case_record(acc, root, state)
    report = _read_analysis_report(acc, root, state)
    _read_scan_subtree(acc, root, state)
    _read_bundle_extras(acc, root)
    if layout == LAYOUT_STUDIO_CASE:
        _inspect_studio(acc, root, state.case_id, state.recorded_source)
    source = _resolve_case_source(acc, root, state.recorded_source)
    return _finish(root, layout=layout, case_id=state.case_id,
                   name=_case_display_name(report, source), source=source, acc=acc)


def _read_source_pointer(acc: _Acc, root: Path) -> str | None:
    """Read the desktop-written source_path.json pointer, when usable."""
    sp_path = root / "source_path.json"
    if not sp_path.is_file():
        return None
    sp = _read_json(sp_path)
    if sp is None:
        acc.problem("SOURCE_PATH_UNREADABLE",
                    "source_path.json exists but does not parse", "incomplete")
        return None
    acc.reference("source_path.json")
    if isinstance(sp, dict) and isinstance(sp.get("path"), str) and sp["path"].strip():
        return sp["path"].strip()
    return None


def _resolve_case_source(
    acc: _Acc,
    root: Path,
    recorded_source: str | None,
) -> SourceRef | None:
    """SourceRef for a case bundle: recorded digest + optional external path."""
    recorded_path = _read_source_pointer(acc, root)
    external: Path | None = None
    original_name: str | None = None
    if recorded_path is not None:
        candidate = Path(recorded_path)
        original_name = candidate.name
        if candidate.is_file():
            external = candidate
        else:
            acc.unknown(
                "source_path.json points to a file that no longer exists; the "
                "source cannot be verified, but the recorded digest is preserved"
            )

    verified: bool | None = None
    size: int | None = None
    if external is not None:
        size = external.stat().st_size
        if recorded_source is not None:
            verified = sha256_file(external) == recorded_source
            if not verified:
                acc.problem("SOURCE_HASH_MISMATCH",
                            "the file recorded in source_path.json does not match "
                            "the case's recorded source digest", "corrupt")

    if external is None and recorded_source is None:
        return None

    return SourceRef(
        origin="external_path" if external is not None else "case_record",
        logical_path=None,
        path=str(external.resolve()) if external is not None else recorded_path,
        original_name=original_name,
        size_bytes=size,
        recorded_sha256=recorded_source,
        verified=verified,
    )


#: Typed studio records: file name → artifact kind.
_STUDIO_RECORDS = (
    ("meta.json", "session.meta"),
    ("diagnosis.json", "session.diagnosis"),
    ("context.json", "session.context"),
    ("finish_mode.json", "session.finish_mode"),
    ("pipeline.json", "session.pipeline_record"),
    ("selection.json", "session.selection"),
)

#: Derived records and human decisions worth a note, said once when present.
_STUDIO_RECORD_NOTES = (
    ("pipeline.json",
     "studio/pipeline.json is a derived record, not an authority; the "
     "stage is re-derived from artifacts by its producer and is not "
     "normalized here"),
    ("finish_mode.json",
     "studio/finish_mode.json records an explicit human opt-in "
     "(QUICK_STEREO_ONLY); it is preserved as a human decision, not "
     "re-derived"),
    ("selection.json",
     "studio/selection.json records the human's chosen version; it is "
     "preserved as a decision and never auto-selected here"),
)


def _check_case_binding(acc: _Acc, case_id: str | None, logical_path: str,
                        data: Any) -> None:
    """Note the schema, and refuse a record bound to a different case."""
    if not isinstance(data, dict):
        return
    _note_schema(acc, logical_path, data.get("schema"))
    bound = data.get("case_id")
    if isinstance(bound, str) and case_id is not None and bound != case_id:
        acc.problem("CASE_ID_CONFLICT",
                    f"{logical_path} says case {bound!r} but the case is "
                    f"{case_id!r}", "corrupt")


def _read_studio_records(acc: _Acc, root: Path, case_id: str | None) -> None:
    """Typed studio records, then the decisions/derived state they carry."""
    studio = root / "studio"
    for name, kind in _STUDIO_RECORDS:
        path = studio / name
        if not path.is_file():
            continue
        data = _read_json(path)
        if data is None:
            acc.problem("STUDIO_FILE_UNREADABLE",
                        f"studio/{name} exists but does not parse", "corrupt")
        else:
            _check_case_binding(acc, case_id, f"studio/{name}", data)
        _add_artifact(acc, root, "session", path, kind)
    for name, note in _STUDIO_RECORD_NOTES:
        if (studio / name).is_file():
            acc.unknown(note)


def _read_studio_plans(acc: _Acc, root: Path, case_id: str | None) -> None:
    for path in _list_files(root / "studio" / "plans", (".json",)):
        plan = _read_json(path)
        if plan is None:
            acc.problem("STUDIO_FILE_UNREADABLE",
                        f"{_rel(root, path)} exists but does not parse", "corrupt")
        else:
            _check_case_binding(acc, case_id, _rel(root, path), plan)
        _add_artifact(acc, root, "session", path, "session.plan")


def _read_studio_versions(acc: _Acc, root: Path) -> None:
    """One directory per render version: ``studio/versions/ai_*/``."""
    for version_dir in _list_dirs(root / "studio" / "versions"):
        if not version_dir.name.startswith("ai_"):
            continue
        for audio in _list_files(version_dir / "out", _AUDIO_SUFFIXES):
            _add_artifact(acc, root, "renders", audio, "renders.version_audio")
        evidence = version_dir / "evidence.json"
        if evidence.is_file():
            if _read_json(evidence) is None:
                acc.problem("STUDIO_FILE_UNREADABLE",
                            f"{_rel(root, evidence)} exists but does not parse",
                            "corrupt")
            _add_artifact(acc, root, "renders", evidence, "renders.version_evidence")
        job = version_dir / "job.json"
        if job.is_file():
            _add_artifact(acc, root, "renders", job, "renders.version_job")


def _read_studio_outputs(acc: _Acc, root: Path) -> None:
    for path in _list_files(root / "studio" / "verification", (".json",)):
        _add_artifact(acc, root, "verification", path, "verification.record")
    for path in _list_files(root / "studio" / "export"):
        _add_artifact(acc, root, "exports", path, "exports.file")


def _read_stems(acc: _Acc, root: Path, recorded_source: str | None) -> None:
    for path in _list_files(root / "stems", _AUDIO_SUFFIXES):
        _add_artifact(acc, root, "stems", path, "stems.audio")
    manifest_path = root / "stems" / "manifest.json"
    if not manifest_path.is_file():
        return
    manifest = _read_json(manifest_path)
    if manifest is None:
        acc.problem("STUDIO_FILE_UNREADABLE",
                    "stems/manifest.json exists but does not parse", "corrupt")
    elif isinstance(manifest, dict):
        manifest_sha = _norm_sha(manifest.get("source_sha256"))
        if recorded_source and manifest_sha and manifest_sha != recorded_source:
            acc.problem("SOURCE_HASH_CONFLICT",
                        "stems/manifest.json source_sha256 disagrees with the "
                        "case source digest", "corrupt")
        engine_note = manifest.get("engine_note")
        if isinstance(engine_note, str) and engine_note:
            acc.unknown(
                "stems/manifest.json declares its own grade boundary; the "
                "separator's statement travels with the data and is not "
                "upgraded here"
            )
    _add_artifact(acc, root, "stems", manifest_path, "stems.manifest")


def _read_transcription(acc: _Acc, root: Path) -> None:
    for path in _list_files(root / "midi", (".mid", ".midi")):
        _add_artifact(acc, root, "transcription", path, "transcription.midi")
    for path in _list_files(root / "midi", (".csv",)):
        _add_artifact(acc, root, "transcription", path, "transcription.notes_csv")
    for path in _list_files(root / "score", (".musicxml", ".xml")):
        _add_artifact(acc, root, "score", path, "score.musicxml")


def _read_finishing(acc: _Acc, root: Path) -> None:
    """Preset mix-graph artifacts: graph.json + audio + *.evidence.json."""
    for path in _list_files(root / "finishing"):
        if path.suffix.lower() in AUDIO_EXTENSIONS:
            _add_artifact(acc, root, "renders", path, "renders.mix_graph_audio")
        elif path.name.endswith(".evidence.json"):
            _add_artifact(acc, root, "renders", path, "renders.mix_graph_evidence")
        elif path.suffix.lower() == ".json":
            _add_artifact(acc, root, "renders", path, "renders.mix_graph")


def _count_ledger_decisions(choices: Path) -> int | None:
    """Human A/B decisions in the ledger, or None when a line does not parse."""
    decisions = 0
    try:
        for line in choices.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            json.loads(line)
            decisions += 1
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return decisions


def _read_compare(acc: _Acc, root: Path) -> None:
    """A/B evidence and the human choice ledger."""
    compare_dir = root / "compare"
    artifact = compare_dir / "ab_comparison.json"
    if artifact.is_file():
        _add_artifact(acc, root, "verification", artifact, "verification.ab_comparison")
    choices = compare_dir / "ab_choices.jsonl"
    if not choices.is_file():
        return
    _add_artifact(acc, root, "session", choices, "session.ab_choices")
    decisions = _count_ledger_decisions(choices)
    if decisions is None:
        acc.problem("LEDGER_UNREADABLE",
                    "compare/ab_choices.jsonl contains a line that does not "
                    "parse", "corrupt")
    else:
        acc.unknown(
            f"compare/ab_choices.jsonl records {decisions} human A/B "
            f"decision(s); the decisions are preserved as a ledger, not "
            f"re-interpreted"
        )


def _inspect_studio(acc: _Acc, root: Path, case_id: str | None,
                    recorded_source: str | None) -> None:
    """Read the Studio subtree. Every file stays a reference; nothing moves."""
    _read_studio_records(acc, root, case_id)
    _read_studio_plans(acc, root, case_id)
    _read_studio_versions(acc, root)
    _read_studio_outputs(acc, root)
    _read_stems(acc, root, recorded_source)
    _read_transcription(acc, root)
    _read_finishing(acc, root)
    _read_compare(acc, root)


# ── L4: legacy numbered WSE case ──────────────────────────────────────────────

_LEGACY_SECTIONS = (
    ("01_source_scan", "analysis", "analysis.source_scan"),
    ("02_plans", "session", "session.plan"),
    ("04_after_scan", "analysis", "analysis.candidate_scan"),
    ("05_comparison", "verification", "verification.comparison"),
    ("06_human_review", "session", "session.human_review"),
    ("07_learning", "provenance", "provenance.learning"),
)


def _read_production_case_record(
    acc: _Acc, root: Path
) -> tuple[str | None, list[tuple[str, str]]]:
    """production_case.json — the ProductionCase contract record."""
    case_id: str | None = None
    source_claims: list[tuple[str, str]] = []
    path = root / "production_case.json"
    if not path.is_file():
        return case_id, source_claims
    data = _read_json(path)
    if data is None:
        acc.problem("CASE_RECORD_UNREADABLE",
                    "production_case.json exists but does not parse", "corrupt")
        return case_id, source_claims
    if not isinstance(data, dict):
        return case_id, source_claims
    acc.reference("production_case.json")
    if isinstance(data.get("case_id"), str):
        case_id = data["case_id"]
    claim = _norm_sha(data.get("source_id"))
    if claim:
        source_claims.append(("production_case.json", claim))
    schema_version = data.get("schema_version")
    if schema_version is not None and schema_version != _CASE_SCHEMA_VERSION:
        acc.unknown(
            f"production_case.json declares schema_version "
            f"{schema_version!r} (recognised: {_CASE_SCHEMA_VERSION!r}); "
            f"fields are recorded as-is, not interpreted"
        )
    return case_id, source_claims


def _read_case_manifest_record(
    acc: _Acc, root: Path, case_id: str | None, source_claims: list[tuple[str, str]]
) -> tuple[str | None, Any]:
    """case_manifest.json — this layout's own provenance manifest."""
    path = root / "case_manifest.json"
    if not path.is_file():
        return case_id, None
    case_manifest = _read_json(path)
    if case_manifest is None:
        acc.problem("CASE_RECORD_UNREADABLE",
                    "case_manifest.json exists but does not parse", "corrupt")
        return case_id, None
    acc.reference("case_manifest.json")
    if not isinstance(case_manifest, dict):
        return case_id, case_manifest
    manifest_case_id = case_manifest.get("case_id")
    if isinstance(manifest_case_id, str):
        if case_id is not None and manifest_case_id != case_id:
            acc.problem("CASE_ID_CONFLICT",
                        f"production_case.json says {case_id!r} but "
                        f"case_manifest.json says {manifest_case_id!r}", "corrupt")
        case_id = case_id or manifest_case_id
    claim = _norm_sha(case_manifest.get("source_sha256"))
    if claim:
        source_claims.append(("case_manifest.json", claim))
    return case_id, case_manifest


def _collect_legacy_claims(acc: _Acc, root: Path,
                           source_claims: list[tuple[str, str]]) -> None:
    """Add the 01_source_scan claim (or the 02_plans fallback) as a claim."""
    scan_manifest_path = root / "01_source_scan" / "scan_manifest.json"
    scan_manifest = _read_json(scan_manifest_path) if scan_manifest_path.is_file() else None
    if isinstance(scan_manifest, dict):
        claim = _norm_sha(scan_manifest.get("input_sha256"))
        if claim:
            source_claims.append(("01_source_scan/scan_manifest.json", claim))
        input_path = scan_manifest.get("input_path")
        if isinstance(input_path, str) and not Path(input_path).is_file():
            acc.unknown(
                "01_source_scan/scan_manifest.json input_path is a path from the "
                "machine that produced it and does not resolve here; the source "
                "is verified by digest instead"
            )
    if source_claims:
        return
    # Fallback: plans recorded the source digest they were planned against.
    for plan in _list_files(root / "02_plans", (".json",)):
        data = _read_json(plan)
        if isinstance(data, dict):
            claim = _norm_sha(data.get("source_sha256"))
            if claim:
                source_claims.append((_rel(root, plan), claim))
                break


def _check_claim_conflicts(acc: _Acc, source_claims: list[tuple[str, str]]) -> str | None:
    """Every record that names the source digest must agree.

    A disagreement means one of them is wrong and neither may be trusted
    silently.
    """
    recorded_source = source_claims[0][1] if source_claims else None
    for where, claim in source_claims[1:]:
        if claim != recorded_source:
            acc.problem("SOURCE_HASH_CONFLICT",
                        f"{where} records source digest {claim!r} but "
                        f"{source_claims[0][0]} records {recorded_source!r}", "corrupt")
    return recorded_source


def _resolve_legacy_source(acc: _Acc, root: Path,
                           recorded_source: str | None) -> SourceRef | None:
    """The file inside 00_source/, verified against the recorded digests."""
    source_files = _list_files(root / "00_source", _AUDIO_SUFFIXES)
    if not source_files:
        acc.problem("SOURCE_FILE_MISSING", "00_source/ contains no audio file",
                    "incomplete")
        return None
    primary = source_files[0]
    if len(source_files) > 1:
        acc.unknown(
            f"00_source/ contains {len(source_files)} audio files; the first "
            f"in sorted order is treated as the source and the rest are left "
            f"unreferenced"
        )
    verified: bool | None = None
    if recorded_source is not None:
        verified = sha256_file(primary) == recorded_source
        if not verified:
            acc.problem("SOURCE_HASH_MISMATCH",
                        "00_source file does not match the recorded source "
                        "digest records", "corrupt")
    acc.reference(_rel(root, primary))
    return SourceRef(
        origin="in_case",
        logical_path=_rel(root, primary),
        path=str(primary.resolve()),
        original_name=primary.name,
        size_bytes=primary.stat().st_size,
        recorded_sha256=recorded_source,
        verified=verified,
    )


def _verify_legacy_scan_dirs(acc: _Acc, root: Path) -> None:
    """Recorded scan artifacts: the 01 source scan + per-candidate 04 scans."""
    _verify_scan_dir(acc, root, root / "01_source_scan")
    for candidate_scan in _list_dirs(root / "04_after_scan"):
        _verify_scan_dir(acc, root, candidate_scan)


def _candidate_claims(root: Path,
                      case_manifest: Any) -> tuple[dict[str, str], dict[str, str]]:
    """Candidate digests from the record files and from the case manifest map."""
    records: dict[str, str] = {}
    for record_path in _list_files(root / "03_candidates", (".json",)):
        data = _read_json(record_path)
        if isinstance(data, dict):
            claim = _norm_sha(data.get("candidate_sha256"))
            if claim:
                records[record_path.stem] = claim
    manifest_map: dict[str, str] = {}
    if isinstance(case_manifest, dict) and isinstance(
            case_manifest.get("candidate_sha256"), dict):
        for key, value in case_manifest["candidate_sha256"].items():
            claim = _norm_sha(value)
            if claim:
                name = key if key.startswith("candidate_") else f"candidate_{key}"
                manifest_map[name] = claim
    return records, manifest_map


def _read_legacy_candidates(acc: _Acc, root: Path, case_manifest: Any) -> None:
    """Candidate records, the manifest map and the audio files must agree."""
    candidates_dir = root / "03_candidates"
    records, manifest_map = _candidate_claims(root, case_manifest)
    for name in sorted(set(records) & set(manifest_map)):
        if records[name] != manifest_map[name]:
            acc.problem("CANDIDATE_HASH_CONFLICT",
                        f"{name} digest disagrees between its record file and "
                        f"case_manifest.json", "corrupt")
    for path in _list_files(candidates_dir):
        if path.suffix.lower() in AUDIO_EXTENSIONS:
            recorded = records.get(path.stem) or manifest_map.get(path.stem)
            _add_artifact(acc, root, "renders", path, "renders.candidate_audio",
                          recorded=recorded)
        elif path.suffix.lower() == ".json":
            _add_artifact(acc, root, "renders", path, "renders.candidate_record")


def _collect_legacy_stage_files(acc: _Acc, root: Path) -> None:
    """The numbered stage directories, by the roles their positions imply."""
    for dirname, section, kind in _LEGACY_SECTIONS:
        stage_dir = root / dirname
        if not stage_dir.is_dir():
            continue
        for path in sorted(stage_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = _rel(root, path)
            if rel in acc.referenced:
                continue
            stage_kind = kind
            if path.name == "scan_manifest.json":
                stage_kind = f"{kind}.scan_manifest"
            _add_artifact(acc, root, section, path, stage_kind)


def _collect_legacy_docs(acc: _Acc, root: Path) -> None:
    """Case-level documentation and the reopen/verify tool."""
    readme = root / "README.md"
    if readme.is_file():
        _add_artifact(acc, root, "provenance", readme, "provenance.readme")
    reopen_tool = root / "reopen_golden.py"
    if reopen_tool.is_file():
        _add_artifact(acc, root, "verification", reopen_tool, "verification.reopen_tool")


def _inspect_legacy(root: Path) -> CaseInspection:
    acc = _Acc()
    case_id, source_claims = _read_production_case_record(acc, root)
    case_id, case_manifest = _read_case_manifest_record(acc, root, case_id, source_claims)
    _collect_legacy_claims(acc, root, source_claims)
    recorded_source = _check_claim_conflicts(acc, source_claims)
    source = _resolve_legacy_source(acc, root, recorded_source)
    _verify_legacy_scan_dirs(acc, root)
    _read_legacy_candidates(acc, root, case_manifest)
    _collect_legacy_stage_files(acc, root)
    _collect_legacy_docs(acc, root)
    acc.unknown(
        "artifact roles in the numbered WSE layout come from directory positions; "
        "every JSON payload beyond the recorded digests is preserved as a file "
        "reference, not interpreted"
    )
    name = source.original_name if source is not None else None
    return _finish(root, layout=LAYOUT_LEGACY_WSE, case_id=case_id, name=name,
                   source=source, acc=acc)
