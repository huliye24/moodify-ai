"""A/B listening comparison sessions for a finishing case — CLI-first.

One Core, Multiple Interfaces: this module is the single A/B authority for
"keep A (source) or keep B (rendered finishing artifact)". It does not
implement a second compare engine:

- loudness / peak / geometry measurements come from the mix-graph
  verification authority (``moodify.mix_graph.verify.measure_audio``, whose
  LUFS path is ``processing.pedalboard_chain._measure_lufs``);
- B is a Mix Graph render, and its evidence (graph digest, operator chain,
  before/after verification) is read back from the render's own evidence
  document, never recomputed here;
- spectral delta / paired analysis of two *analyses* stays with the MSP/0.2
  ``compare`` job (``moodify.auditory.comparison``). This module is about a
  listening pair tied to a production case, not about analyzing two cases.

Honesty rules (v0.1):

- loudness is measured, never faked. v0.1 produces no loudness-matched
  proxy, so ``matching_status`` is ``NOT_MATCHED`` or ``UNAVAILABLE`` —
  never ``MATCHED`` — and the artifact says so explicitly. No calibrated
  loudness-match threshold is introduced (0 calibrated thresholds exist).
- a missing / unresolvable A or B is ``HUMAN_REQUIRED``, a confounded pair
  is ``INCONCLUSIVE``; neither is ever reported as a ready success.
- the machine never decides which version is better: ``choose`` records a
  human decision (role + time + evidence references) into an append-only
  ledger and re-verifies the recorded hashes before accepting it.

Artifacts (all inside the case directory, never beside the source audio):

- ``compare/ab_comparison.json`` — the prepared pair (A/B paths, sha256,
  provenance, loudness measurements, matching status);
- ``compare/ab_choices.jsonl`` — append-only human choices (no update or
  delete path exists by design).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from moodify.auditory.manifests import sha256_file
from moodify.mix_graph.schema import canonical_json

SCHEMA_ID = "moodify.ab_compare/0.1"
CHOICE_SCHEMA_ID = "moodify.ab_compare.choice/0.1"
COMPARE_DIRNAME = "compare"
ARTIFACT_NAME = "ab_comparison.json"
CHOICES_NAME = "ab_choices.jsonl"
RENDER_DIRNAME = "finishing"
RENDER_SUFFIX = "_mixgraph_"
EVIDENCE_SUFFIX = ".evidence.json"

# Closed enumerations — the same values the CLI and every interface accept.
KEEP_VALUES = ("A", "B")
ROLES = ("creator", "listener", "pro")
KEPT = {"A": "source", "B": "rendered"}

# Deterministic process exit codes shared by prepare/choose/show.
EXIT_OK = 0
EXIT_FAILED = 2
EXIT_HUMAN_REQUIRED = 3
EXIT_INCONCLUSIVE = 4

STATUS_EXIT = {
    "READY": EXIT_OK,
    "HUMAN_REQUIRED": EXIT_HUMAN_REQUIRED,
    "INCONCLUSIVE": EXIT_INCONCLUSIVE,
}


class CompareError(Exception):
    """A refusable request (bad case, bad path, stale evidence).

    Always carries a stable machine ``code`` so an agent (or the Studio shell)
    can branch on the failure instead of parsing prose.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code

    def payload(self) -> dict[str, Any]:
        return {"status": "error", "code": self.code, "error": str(self)}


# ——— path guards ————————————————————————————————————————————————————————


def resolve_case_dir(case_dir: str | Path, cases_root: str | Path | None = None) -> Path:
    """Resolve and validate a case directory; optionally bound it to a root.

    A case directory is a directory produced by the analysis path, i.e. it
    carries ``case.json``. When ``cases_root`` is given the case must live
    inside it — the CLI never reads a case from outside its stated root.
    """
    root = Path(case_dir)
    try:
        resolved = root.resolve(strict=True)
    except OSError as exc:
        raise CompareError("CASE_NOT_FOUND", f"case directory not found: {case_dir}") from exc
    if not resolved.is_dir():
        raise CompareError("NOT_A_CASE", f"case path is not a directory: {resolved}")
    if not (resolved / "case.json").is_file():
        raise CompareError("NOT_A_CASE", f"not a Moodify case (case.json missing): {resolved}")
    if cases_root is not None:
        allowed = Path(cases_root).expanduser().resolve()
        try:
            resolved.relative_to(allowed)
        except ValueError as exc:
            raise CompareError(
                "CASE_OUTSIDE_ROOT",
                f"case directory is outside the allowed cases root: {resolved}") from exc
    return resolved


def _inside(base: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(base)
        return True
    except ValueError:
        return False


def _resolve_inside(base: Path, value: str | Path, what: str, code: str) -> Path:
    """Resolve a caller-supplied path and require it inside ``base``."""
    anchor = base.resolve()
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = anchor / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise CompareError(f"{code}_NOT_FOUND", f"{what} not found: {value}") from exc
    if not _inside(anchor, resolved):
        raise CompareError(f"{code}_OUTSIDE_CASE",
                           f"{what} is outside the case directory: {resolved}")
    return resolved


def _sha256(path: Path) -> str:
    return sha256_file(path)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CompareError("UNREADABLE_JSON", f"cannot read {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise CompareError("UNREADABLE_JSON", f"{path.name} is not a JSON object")
    return data


# ——— resolution of A (source) and B (render) ——————————————————————————————


def _resolve_source(case_root: Path, explicit: str | Path | None) -> tuple[Path | None, str]:
    """Resolve the A side; returns (path, resolution_rule) with path None when
    nothing can be resolved. Order: explicit --a, the shell's source_path.json,
    then the source recorded in a finishing graph."""
    candidates: list[tuple[str, Path]] = []
    if explicit is not None:
        candidates.append(("explicit", Path(explicit)))
    sp = case_root / "source_path.json"
    if sp.is_file():
        try:
            recorded = json.loads(sp.read_text(encoding="utf-8")).get("path")
        except (OSError, UnicodeError, json.JSONDecodeError):
            recorded = None
        if isinstance(recorded, str) and recorded.strip():
            candidates.append(("source_path.json", Path(recorded)))
    graph_source = _graph_source_from_case(case_root)
    if graph_source is not None:
        candidates.append(("finishing_graph", graph_source))
    for rule, path in candidates:
        try:
            resolved = path.resolve(strict=True)
        except OSError:
            continue
        if resolved.is_file():
            return resolved, rule
    return None, "unresolved"


def _graph_source_from_case(case_root: Path) -> Path | None:
    """Read the source path a finishing graph in this case targets."""
    render_dir = case_root / RENDER_DIRNAME
    if not render_dir.is_dir():
        return None
    graphs = sorted(render_dir.glob("*__graph.json"), key=lambda p: p.name)
    for graph_path in reversed(graphs):
        try:
            data = json.loads(graph_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        source = data.get("source")
        if not isinstance(source, str) or not source.strip():
            continue
        candidate = Path(source)
        if not candidate.is_absolute():
            candidate = graph_path.parent / candidate
        if candidate.is_file():
            return candidate
    return None


def _render_candidates(case_root: Path) -> list[dict[str, Any]]:
    """All Mix Graph renders in the case, newest first (mtime, then name)."""
    render_dir = case_root / RENDER_DIRNAME
    if not render_dir.is_dir():
        return []
    found: list[dict[str, Any]] = []
    for path in render_dir.glob(f"*{RENDER_SUFFIX}*.wav"):
        try:
            stat = path.stat()
        except OSError:
            continue
        found.append({
            "path": path,
            "name": path.name,
            "mtime": stat.st_mtime,
            "sha256": _sha256(path),
        })
    found.sort(key=lambda item: (item["mtime"], item["name"]), reverse=True)
    return found


def _load_render_evidence(wav: Path) -> dict[str, Any] | None:
    """Read the render's own evidence document (never recomputed here)."""
    candidate = wav.with_name(wav.name[: -len(".wav")] + EVIDENCE_SUFFIX)
    if not candidate.is_file():
        return None
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _match_graph(case_root: Path, evidence: dict[str, Any] | None) -> dict[str, Any]:
    """Locate the Mix Graph document behind the selected render.

    Matching is by graph digest recorded in the render evidence — the graph
    identity the render was actually produced from — with a filename
    fallback. ``available`` is False when neither path resolves: the pair is
    still measurable, but its provenance is then honestly reported missing.
    """
    render_dir = case_root / RENDER_DIRNAME
    digest = (evidence or {}).get("graph_digest_sha256")
    graphs = sorted(render_dir.glob("*__graph.json"), key=lambda p: p.name) \
        if render_dir.is_dir() else []
    if digest:
        for graph_path in graphs:
            try:
                from moodify.mix_graph.graph import load_graph

                graph = load_graph(graph_path)
            except Exception:  # unreadable / invalid graph is simply not a match
                continue
            if graph.digest() == digest:
                return _graph_facts(graph_path, graph, matched_by="graph_digest")
    return {"available": False, "matched_by": None, "graph_path": None,
            "graph_digest_sha256": digest, "preset": None, "operator_chain": None,
            "intent": None}


def _graph_facts(graph_path: Path, graph: Any, matched_by: str) -> dict[str, Any]:
    preset = None
    provenance = graph.provenance if isinstance(graph.provenance, dict) else {}
    notes = provenance.get("notes")
    if isinstance(notes, str) and notes.startswith("preset="):
        preset = notes[len("preset="):].strip() or None
    chain = [{"id": node["id"], "type": node["type"], "enabled": node["enabled"]}
             for node in graph.nodes]
    return {
        "available": True,
        "matched_by": matched_by,
        "graph_path": str(graph_path),
        "graph_digest_sha256": graph.digest(),
        "preset": preset,
        "operator_chain": chain,
        "intent": graph.intent,
    }


# ——— measurement —————————————————————————————————————————————————————————


def _measure(path: Path) -> tuple[dict[str, Any], str | None]:
    """Measure one side with the Core verification authority.

    Returns (measurement, failure_code). A measurement failure never raises:
    the caller reports it as an unresolved fact rather than guessing.
    """
    from moodify.audio_io import load_audio
    from moodify.mix_graph.verify import measure_audio

    try:
        audio, sr = load_audio(str(path), always_2d=True)
    except Exception as exc:  # decode failures must not crash the CLI
        return {}, f"AUDIO_UNREADABLE:{type(exc).__name__}"
    try:
        metrics = measure_audio(audio, sr)
    except Exception as exc:  # a meter may refuse very short / silent input
        return {}, f"MEASUREMENT_FAILED:{type(exc).__name__}"
    metrics["samples"] = int(audio.shape[0])
    return metrics, None


def _loudness_block(a_metrics: dict, b_metrics: dict,
                    a_fail: str | None, b_fail: str | None, *,
                    a_present: bool, b_present: bool) -> dict[str, Any]:
    """Loudness facts + matching status. v0.1 measures only: the honest
    values are NOT_MATCHED (measured difference) or UNAVAILABLE — a matched
    proxy is never claimed, and no calibrated threshold is applied.

    ``unavailable_reason`` names the actual cause so an agent reading the
    artifact is never sent after the wrong problem: a side that does not
    exist is ``MISSING_SIDE``, not a meter failure.
    """
    a_lufs = a_metrics.get("integrated_loudness_lufs")
    b_lufs = b_metrics.get("integrated_loudness_lufs")
    missing = [side for side, present in (("A", a_present), ("B", b_present)) if not present]
    if missing:
        return {
            "method": "measurement_only",
            "matched_proxy_available": False,
            "matching_status": "UNAVAILABLE",
            "matching_threshold_lu": None,
            "threshold_status": "NO_CALIBRATED_THRESHOLD",
            "a_integrated_lufs": a_lufs if a_present else None,
            "b_integrated_lufs": b_lufs if b_present else None,
            "delta_lu": None,
            "gain_to_match_a_db": None,
            "unavailable_reason": "MISSING_SIDE:" + ",".join(missing),
            "note": (f"A/B 未同时存在（缺 {'/'.join(missing)}）：没有可比较的响度。"
                     "（v0.1 只测量，不生成响度匹配代理。）"),
        }
    if a_fail or b_fail:
        return {
            "method": "measurement_only",
            "matched_proxy_available": False,
            "matching_status": "UNAVAILABLE",
            "matching_threshold_lu": None,
            "threshold_status": "NO_CALIBRATED_THRESHOLD",
            "a_integrated_lufs": None if a_fail else a_lufs,
            "b_integrated_lufs": None if b_fail else b_lufs,
            "delta_lu": None,
            "gain_to_match_a_db": None,
            "unavailable_reason": a_fail or b_fail,
            "note": ("响度无法在两侧同时测量；本对 A/B 不能用于响度受控的听感判断。"
                     "（v0.1 只测量，不生成响度匹配代理。）"),
        }
    if not isinstance(a_lufs, (int, float)) or not isinstance(b_lufs, (int, float)):
        return {
            "method": "measurement_only",
            "matched_proxy_available": False,
            "matching_status": "UNAVAILABLE",
            "matching_threshold_lu": None,
            "threshold_status": "NO_CALIBRATED_THRESHOLD",
            "a_integrated_lufs": a_lufs,
            "b_integrated_lufs": b_lufs,
            "delta_lu": None,
            "gain_to_match_a_db": None,
            "unavailable_reason": "LOUDNESS_NOT_NUMERIC",
            "note": "响度计没有给出数值；不判断是否匹配。（v0.1 只测量，不生成响度匹配代理。）",
        }
    delta = round(float(b_lufs) - float(a_lufs), 3)
    return {
        "method": "measurement_only",
        "matched_proxy_available": False,
        "matching_status": "NOT_MATCHED",
        "matching_threshold_lu": None,
        "threshold_status": "NO_CALIBRATED_THRESHOLD",
        "a_integrated_lufs": a_lufs,
        "b_integrated_lufs": b_lufs,
        "delta_lu": delta,
        "gain_to_match_a_db": round(-delta, 3),
        "unavailable_reason": None,
        "note": ("已测量两侧响度；v0.1 不生成响度匹配代理，因此本对 A/B 一律记为"
                 " NOT_MATCHED —— 界面不得显示为「已匹配」，人也必须知道 B 更响/更轻。"
                 "（未引入任何未经校准的匹配阈值。）"),
    }


def comparison_artifact_path(case_root: Path) -> Path:
    return case_root / COMPARE_DIRNAME / ARTIFACT_NAME


def choices_path(case_root: Path) -> Path:
    return case_root / COMPARE_DIRNAME / CHOICES_NAME


# ——— prepare —————————————————————————————————————————————————————————————


def prepare_comparison(case_dir: str | Path, *, cases_root: str | Path | None = None,
                       a_path: str | Path | None = None,
                       b_path: str | Path | None = None) -> dict[str, Any]:
    """Build (or refresh) the A/B comparison artifact for one case.

    Returns the artifact document. ``status`` is READY (0), HUMAN_REQUIRED
    (3) when a side is missing, or INCONCLUSIVE (4) when the pair cannot
    support a comparison (geometry mismatch / unmeasurable loudness).
    """
    case_root = resolve_case_dir(case_dir, cases_root)
    case_meta = _read_json(case_root / "case.json")
    case_id = case_meta.get("case_id") or case_root.name
    declared_source = case_meta.get("source_id")
    if isinstance(declared_source, str) and declared_source.startswith("sha256:"):
        declared_source = declared_source[len("sha256:"):]
    else:
        declared_source = None

    reasons: list[dict[str, str]] = []
    a_resolved, a_rule = _resolve_source(case_root, a_path)

    b_facts = None
    selected_b: Path | None = None
    candidates: list[dict[str, Any]] = []
    if b_path is not None:
        selected_b = _resolve_inside(case_root / RENDER_DIRNAME, b_path, "B (render)", "B")
        if selected_b.suffix.lower() != ".wav":
            raise CompareError("B_NOT_WAV", f"B must be a WAV render: {selected_b}")
    else:
        candidates = _render_candidates(case_root)
        if candidates:
            selected_b = candidates[0]["path"]

    a_block: dict[str, Any] | None = None
    a_metrics: dict[str, Any] = {}
    a_fail: str | None = None
    if a_resolved is not None:
        a_sha = _sha256(a_resolved)
        # A must be the recording this case actually analyzed; hash equality
        # is the only accepted proof (no arbitrary audio may enter a pair).
        if declared_source and a_sha != declared_source:
            raise CompareError(
                "A_SOURCE_MISMATCH",
                f"A (source) sha256 does not match the analyzed source of case {case_id}")
        a_metrics, a_fail = _measure(a_resolved)
        a_block = {
            "role": "source_before_finishing",
            "path": str(a_resolved),
            "name": a_resolved.name,
            "sha256": a_sha,
            "sha256_matches_case": bool(declared_source) and a_sha == declared_source,
            "resolution_rule": a_rule,
            "measurement": a_metrics or None,
            "measurement_failure": a_fail,
        }
    else:
        reasons.append({"code": "A_SOURCE_UNRESOLVED", "message":
                        "源音频（A）无法定位：提供 --a，或在 case 内保留 source_path.json / finishing 图。"})

    b_evidence = _load_render_evidence(selected_b) if selected_b else None
    if selected_b is not None:
        b_metrics, b_fail = _measure(selected_b)
        graph_facts = _match_graph(case_root, b_evidence)
        b_facts = {
            "role": "rendered_after_finishing",
            "path": str(selected_b),
            "name": selected_b.name,
            "sha256": _sha256(selected_b),
            "selection_rule": "explicit" if b_path is not None else "newest_mtime",
            "candidates": [
                {"path": str(item["path"]), "sha256": item["sha256"],
                 "selected": item["path"] == selected_b}
                for item in candidates
            ] if b_path is None else [
                {"path": str(selected_b), "sha256": _sha256(selected_b), "selected": True},
            ],
            "measurement": b_metrics or None,
            "measurement_failure": b_fail,
            "render_evidence": _render_evidence_block(selected_b, b_evidence),
            "mix_graph": graph_facts,
        }
        if b_evidence is None:
            reasons.append({"code": "B_EVIDENCE_MISSING", "message":
                            "B 缺少渲染证据（*.evidence.json）：预设 / Mix Graph 溯源不可得。"})
        if not graph_facts["available"]:
            reasons.append({"code": "B_GRAPH_UNMATCHED", "message":
                            "B 的 Mix Graph 文档未在 case 内匹配到（按图摘要匹配）。"})
    else:
        b_metrics, b_fail = {}, None
        reasons.append({"code": "B_RENDER_MISSING", "message":
                        "修音产物（B）不存在：先运行 moodify finishing new/render 产出 B。"})

    loudness = _loudness_block(a_metrics, b_metrics, a_fail, b_fail,
                               a_present=a_block is not None, b_present=b_facts is not None)

    geometry: dict[str, Any] = {
        "sample_rate_match": None,
        "lengths_equal": None,
        "duration_delta_s": None,
        "channels_equal": None,
    }
    if a_metrics and b_metrics:
        a_sr, b_sr = a_metrics.get("sample_rate"), b_metrics.get("sample_rate")
        a_len, b_len = a_metrics.get("samples"), b_metrics.get("samples")
        geometry = {
            "sample_rate_match": a_sr == b_sr,
            "lengths_equal": a_len == b_len,
            "duration_delta_s": round(
                float(b_metrics.get("duration_s", 0.0)) - float(a_metrics.get("duration_s", 0.0)), 3),
            "channels_equal": a_metrics.get("channels") == b_metrics.get("channels"),
            "a_sample_rate": a_sr,
            "b_sample_rate": b_sr,
            "a_channels": a_metrics.get("channels"),
            "b_channels": b_metrics.get("channels"),
        }
        if not geometry["sample_rate_match"] or not geometry["lengths_equal"]:
            reasons.append({"code": "PAIR_GEOMETRY_MISMATCH", "message":
                            "A/B 采样率或长度不同：同位置切换不可靠，比较不可结论。"})
    if loudness["matching_status"] == "UNAVAILABLE" and a_block is not None and b_facts is not None:
        # both sides exist, so this is a real measurement gap — not just the
        # consequence of a missing artifact (already reported above)
        reasons.append({"code": "LOUDNESS_UNAVAILABLE", "message": loudness["note"]})

    status = _status_for(a_block, b_facts, geometry, loudness)
    artifact = {
        "schema": SCHEMA_ID,
        "status": status,
        "core_version": _core_version(),
        "prepared_at": _now(),
        "case_id": case_id,
        "case_root": str(case_root),
        "a": a_block,
        "b": b_facts,
        "loudness": loudness,
        "geometry": geometry,
        "reasons": reasons,
        "human_required": status == "HUMAN_REQUIRED",
        "review_required": True,
        "decision_authority": "human",
        "machine_verdict": None,
        "note": ("机器只准备事实与证据，不判断哪个版本更好；"
                 "保留 A 或 B 由人通过 `moodify compare choose` 记录。"),
    }
    previous = comparison_artifact_path(case_root)
    if previous.is_file():
        try:
            artifact["previous_prepared_at"] = json.loads(
                previous.read_text(encoding="utf-8")).get("prepared_at")
        except (OSError, UnicodeError, json.JSONDecodeError):
            pass
    _write_json(previous, artifact)
    return artifact


def _status_for(a_block: dict | None, b_facts: dict | None,
                geometry: dict, loudness: dict) -> str:
    if a_block is None or b_facts is None:
        return "HUMAN_REQUIRED"
    if a_block.get("measurement_failure") or b_facts.get("measurement_failure"):
        return "INCONCLUSIVE"
    if geometry.get("sample_rate_match") is False or geometry.get("lengths_equal") is False:
        return "INCONCLUSIVE"
    if loudness.get("matching_status") == "UNAVAILABLE":
        return "INCONCLUSIVE"
    return "READY"


def _render_evidence_block(wav: Path, evidence: dict[str, Any] | None) -> dict[str, Any]:
    if evidence is None:
        return {"available": False, "path": None}
    verification = evidence.get("verification") if isinstance(evidence.get("verification"), dict) else {}
    output = evidence.get("output") if isinstance(evidence.get("output"), dict) else {}
    expected = wav.with_name(wav.name[: -len(".wav")] + EVIDENCE_SUFFIX)
    return {
        "available": True,
        "path": str(expected),
        "schema": evidence.get("schema"),
        "core_version": evidence.get("core_version"),
        "status": evidence.get("status"),
        "graph_digest_sha256": evidence.get("graph_digest_sha256"),
        "source_sha256": evidence.get("source_sha256"),
        "output_sha256": output.get("sha256"),
        "output_sha256_matches_file": output.get("sha256") == _sha256(wav),
        "verification": {
            "before": verification.get("before"),
            "after": verification.get("after"),
            "deltas": verification.get("deltas"),
            "invariants": verification.get("invariants"),
            "peak_gate": verification.get("peak_gate"),
        } if verification else None,
        "node_count": len(evidence.get("nodes") or []),
    }


# ——— choose ——————————————————————————————————————————————————————————————


def record_choice(case_dir: str | Path, *, keep: str, role: str, notes: str | None = None,
                  request_id: str | None = None,
                  cases_root: str | Path | None = None) -> dict[str, Any]:
    """Append one human A/B decision to the case's choice ledger.

    The choice is only accepted against a READY artifact whose recorded A/B
    hashes still match the files on disk — a stale pair is refused, never
    silently recorded. Recording is append-only; nothing can rewrite or
    delete a recorded human decision.

    ``request_id`` makes a retry safe: an agent that re-sends the same
    request (timeout, reconnect) must not record the same human decision
    twice. A repeated ``request_id`` is refused, not appended again.
    """
    if keep not in KEEP_VALUES:
        raise CompareError("BAD_KEEP", f"--keep must be one of: {', '.join(KEEP_VALUES)}")
    if role not in ROLES:
        raise CompareError("BAD_ROLE", f"--role must be one of: {', '.join(ROLES)}")
    if request_id is not None:
        request_id = request_id.strip()
        if not request_id or len(request_id) > 128:
            raise CompareError("BAD_REQUEST_ID",
                               "--request-id must be 1..128 characters")
    case_root = resolve_case_dir(case_dir, cases_root)
    artifact_path = comparison_artifact_path(case_root)
    if not artifact_path.is_file():
        raise CompareError(
            "COMPARISON_NOT_PREPARED",
            "no prepared comparison for this case; run `moodify compare prepare` first")
    artifact = _read_json(artifact_path)
    status = artifact.get("status")
    if status != "READY":
        raise NotReadyError(status, artifact)

    if request_id is not None:
        existing = _find_request(case_root, request_id)
        if existing is not None:
            raise CompareError(
                "DUPLICATE_REQUEST",
                f"request_id {request_id!r} was already recorded as "
                f"{existing.get('choice_id')} ({existing.get('keep')}); "
                f"the ledger is append-only, nothing was written")

    a_block = artifact.get("a") or {}
    b_block = artifact.get("b") or {}
    for side, block in (("A", a_block), ("B", b_block)):
        path = Path(block.get("path", ""))
        if not path.is_file():
            raise CompareError(f"{side}_FILE_GONE", f"{side} file is gone: {path}")
        if _sha256(path) != block.get("sha256"):
            raise CompareError(
                "COMPARISON_STALE",
                f"{side} changed since the comparison was prepared; re-run "
                f"`moodify compare prepare` (recorded hash mismatch)")

    entry = {
        "schema": CHOICE_SCHEMA_ID,
        "choice_id": f"abch_{uuid4().hex}",
        "request_id": request_id,
        "created_at": _now(),
        "case_id": artifact.get("case_id") or case_root.name,
        "keep": keep,
        "kept": KEPT[keep],
        "role": role,
        "notes": (notes or "").strip()[:500] or None,
        "reviewer_kind": "human",
        "recorded_by": "moodify.compare",
        "evidence": {
            "comparison_path": str(artifact_path),
            "comparison_sha256": _sha256(artifact_path),
            "a_path": a_block.get("path"),
            "a_sha256": a_block.get("sha256"),
            "b_path": b_block.get("path"),
            "b_sha256": b_block.get("sha256"),
            "render_evidence_path": (b_block.get("render_evidence") or {}).get("path"),
            "graph_digest_sha256": (b_block.get("mix_graph") or {}).get("graph_digest_sha256"),
            "preset": (b_block.get("mix_graph") or {}).get("preset"),
        },
        "loudness": {
            "matching_status": (artifact.get("loudness") or {}).get("matching_status"),
            "delta_lu": (artifact.get("loudness") or {}).get("delta_lu"),
            "matched_proxy_available": (artifact.get("loudness") or {}).get(
                "matched_proxy_available", False),
        },
    }
    ledger = choices_path(case_root)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as stream:
        stream.write(_jsonl(entry))
    return {
        "status": "recorded",
        "choice": entry,
        "choice_id": entry["choice_id"],
        "keep": keep,
        "kept": KEPT[keep],
        "role": role,
        "created_at": entry["created_at"],
        "count": _count_choices(case_root),
        "choices_path": str(ledger),
        "loudness_matched": False,
        "review_required": True,
    }


class NotReadyError(Exception):
    """The artifact exists but is not READY — nothing may be recorded."""

    def __init__(self, status: str | None, artifact: dict) -> None:
        super().__init__(f"comparison is not READY (status={status})")
        self.status = status
        self.artifact = artifact

    @property
    def exit_code(self) -> int:
        return STATUS_EXIT.get(self.status or "", EXIT_FAILED)

    def payload(self) -> dict[str, Any]:
        return {
            "status": self.status or "FAILED",
            "error": f"comparison is {self.status or 'unusable'}; nothing recorded",
            "reasons": self.artifact.get("reasons", []),
            "case_id": self.artifact.get("case_id"),
            "case_root": self.artifact.get("case_root"),
        }


def _count_choices(case_root: Path) -> int:
    ledger = choices_path(case_root)
    if not ledger.is_file():
        return 0
    return sum(1 for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip())


def _find_request(case_root: Path, request_id: str) -> dict[str, Any] | None:
    """The ledger entry already carrying ``request_id``, if any."""
    ledger = choices_path(case_root)
    if not ledger.is_file():
        return None
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict) and entry.get("request_id") == request_id:
            return entry
    return None


# ——— show —————————————————————————————————————————————————————————————————


def load_comparison(case_dir: str | Path, *,
                    cases_root: str | Path | None = None) -> dict[str, Any]:
    """Read the prepared artifact plus its ledger summary (read-only)."""
    case_root = resolve_case_dir(case_dir, cases_root)
    artifact_path = comparison_artifact_path(case_root)
    if not artifact_path.is_file():
        raise CompareError(
            "COMPARISON_NOT_PREPARED",
            "no prepared comparison for this case; run `moodify compare prepare` first")
    artifact = _read_json(artifact_path)
    source_status = {
        "artifact_path": str(artifact_path),
        "artifact_sha256": _sha256(artifact_path),
        "choices_path": str(choices_path(case_root)),
        "choice_count": _count_choices(case_root),
        "a_sha256_current": _current_sha(artifact.get("a")),
        "b_sha256_current": _current_sha(artifact.get("b")),
    }
    source_status["a_matches_artifact"] = _hashes_match(artifact.get("a"))
    source_status["b_matches_artifact"] = _hashes_match(artifact.get("b"))
    return {"status": artifact.get("status"), "artifact": artifact,
            "freshness": source_status}


def _current_sha(block: dict | None) -> str | None:
    if not block or not block.get("path"):
        return None
    path = Path(block["path"])
    if not path.is_file():
        return None
    return _sha256(path)


def _hashes_match(block: dict | None) -> bool | None:
    if not block:
        return None
    current = _current_sha(block)
    if current is None:
        return False
    return current == block.get("sha256")


# ——— small helpers ————————————————————————————————————————————————————————


def _now() -> str:
    from moodify.contracts.base import utc_now

    return utc_now().isoformat()


def _core_version() -> str:
    from moodify.release import PRODUCT_VERSION

    return PRODUCT_VERSION


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Atomic write: a half-written artifact must never be readable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(canonical_json(data), encoding="utf-8")
    os.replace(tmp, path)


def _jsonl(data: dict[str, Any]) -> str:
    """One line per record — the ledger is append-only JSONL."""
    return json.dumps(data, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")) + "\n"
