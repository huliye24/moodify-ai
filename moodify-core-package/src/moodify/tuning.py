"""tuning.py — paired tier rendering for the Studio tuning stage (EXPERIMENTAL).

CONTRACT: protocol/mips/MIP-0002-stem-tuning-loop.md, **Addendum A** (`FAST_STEREO_ONLY` pair).

WHAT THIS IS
    One call renders **one pair** of complete candidates for a case's own stereo master:

        moodify tuning render-pair --mode fast-stereo-only --source <song.wav>
                                   --output-dir <case>/studio/tuning/<pair_id>

    It reuses the existing `moodify.mix_graph` session for the actual audio work (one DSP
    authority) and adds only: the two tier descriptors, the pair-level bookkeeping, the atomic
    publish, and the per-side evidence wrapper.

WHAT THIS IS NOT
    It does **not** correct pitch or timing, does not touch stems, and does not claim to have
    recovered them. Those are the deep path's promises (same MIP, main specification) and Core
    cannot keep them yet. The two tiers here are whole-track chains with explicit engineering
    defaults whose `calibration_status` is `UNCALIBRATED_ENGINEERING_DEFAULT` — an engineering
    default is not a validated setting, and tier B is "full" (more change), never "better".

WHY THE PUBLISH IS ATOMIC
    A half-written pair is worse than no pair: the Studio stage cursor is derived from artifacts,
    so a directory that looks like a pair decides the pipeline's next step. So both sides are
    rendered inside a temporary sibling attempt directory, and only a complete pair is renamed
    into place. Any failure removes the attempt and leaves no `<pair_id>` behind.
"""

from __future__ import annotations

import hashlib
import os
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np

from moodify.audio_io import load_audio
from moodify.mix_graph.graph import MixGraph
from moodify.mix_graph.providers import get_provider
from moodify.mix_graph.schema import AUDIO_EXTENSIONS, canonical_json
from moodify.mix_graph.session import run_session
from moodify.release import PRODUCT_VERSION

# ── contract constants ──────────────────────────────────────────────────────────

PAIR_SCHEMA = "moodify.studio.tuning-pair/0.1"
TIER_SCHEMA = "moodify.core.tuning-tier/0.1"
EVIDENCE_SCHEMA = "moodify.studio.tier-evidence/0.1"

#: CLI mode values (closed set for this addendum).
MODES = ("fast-stereo-only",)
FAST_MODE = "fast-stereo-only"
#: The label written into artifacts. The CLI spelling and the artifact label are deliberately
#: different vocabularies (kebab for a command line, the V4 mode name for a durable record) and
#: the mapping is explicit here rather than assumed at the edges.
MODE_LABELS = {FAST_MODE: "FAST_STEREO_ONLY"}

#: Tier ids, in side order. A = conservative, B = full. Closed set.
TIER_ORDER = ("conservative", "full")
SIDE_OF_TIER = {"conservative": "A", "full": "B"}
TIER_OF_SIDE = {side: tier for tier, side in SIDE_OF_TIER.items()}

CALIBRATION_STATUS = "UNCALIBRATED_ENGINEERING_DEFAULT"

#: Length gate. This chain is sample-preserving by construction, so the tolerance is exact and
#: stated rather than "close enough". A mismatch is a real failure, not a rounding detail.
LENGTH_TOLERANCE_SAMPLES = 0

#: The evidence's own statement of what the machine did and did not establish.
REVIEW_NOTE = (
    "机器已处理并测量；是否更好只能由人听了再定。"
    "本档参数为工程默认（UNCALIBRATED_ENGINEERING_DEFAULT），B 档代表「变化更充分」，不代表「更好」。"
)

#: Reference-implementation tier defaults, frozen in MIP-0002 Addendum A §A.4.
#: They are whole-track `mix_graph` primitives only. `preserve` is empty because nobody has
#: recorded what to protect for this case — a claim of preservation would be invented.
_TIER_NODES: dict[str, list[dict[str, Any]]] = {
    "conservative": [
        {
            "id": "eq_1",
            "type": "eq",
            "parameters": {"bands": [
                {"type": "highshelf", "freq_hz": 10000.0, "gain_db": 0.5},
            ]},
            "reason": "conservative tier: one gentle high shelf (engineering default, uncalibrated)",
        },
        {
            "id": "comp_1",
            "type": "compressor",
            "parameters": {
                "threshold_db": -14.0, "ratio": 1.2, "attack_ms": 35.0, "release_ms": 250.0,
            },
            "reason": "conservative tier: light dynamics control (engineering default, uncalibrated)",
        },
        {
            "id": "limiter_1",
            "type": "limiter",
            "parameters": {"ceiling_db": -1.0, "input_gain_db": 0.0},
            "reason": "hard ceiling at -1 dBFS with no make-up gain (repo-standard ceiling)",
        },
    ],
    "full": [
        {
            "id": "eq_1",
            "type": "eq",
            "parameters": {"bands": [
                {"type": "highshelf", "freq_hz": 10000.0, "gain_db": 1.5},
                {"type": "peak", "freq_hz": 250.0, "gain_db": -1.0, "q": 0.7},
            ]},
            "reason": "full tier: larger shelf plus a narrow low-mid dip (engineering default, uncalibrated)",
        },
        {
            "id": "comp_1",
            "type": "compressor",
            "parameters": {
                "threshold_db": -18.0, "ratio": 1.5, "attack_ms": 25.0, "release_ms": 220.0,
            },
            "reason": "full tier: firmer dynamics control (engineering default, uncalibrated)",
        },
        {
            "id": "stereo_1",
            "type": "stereo",
            "parameters": {"width": 1.08},
            "reason": "full tier: slight width increase; mono input is an identity no-op",
        },
        {
            "id": "limiter_1",
            "type": "limiter",
            "parameters": {"ceiling_db": -1.0, "input_gain_db": 0.5},
            "reason": "hard ceiling at -1 dBFS with +0.5 dB input gain (repo-standard ceiling)",
        },
    ],
}


class TuningError(ValueError):
    """Raised for any invalid tier/pair request or a failed pair render."""


# ── ids, hashing, small io ──────────────────────────────────────────────────────


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_pair_id(now: datetime | None = None) -> str:
    """`tune_<utcstamp17>_<rand4>` — same shape as the Studio caller's ids.

    Millisecond precision plus a random suffix: uniqueness is load-bearing (a pair directory must
    never collide with an existing one), while ordering is decided by `created_at`, not by the id.
    """
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y%m%d%H%M%S%f")[:17]
    rand = "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(4))
    return f"tune_{stamp}_{rand}"


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(payload), encoding="utf-8")
    return path


# ── tiers ───────────────────────────────────────────────────────────────────────


def tier_descriptor(tier: str) -> dict:
    """The self-describing record of one tier: every value it applies, plus its calibration state.

    A tier that is not in the closed set is refused here, so no downstream consumer can meet an
    unknown tier id and guess what it meant.
    """
    if tier not in TIER_ORDER:
        raise TuningError(f"unknown tier '{tier}'; the closed set is {', '.join(TIER_ORDER)}")
    return {
        "schema": TIER_SCHEMA,
        "tier": tier,
        "side": SIDE_OF_TIER[tier],
        "mode": MODE_LABELS[FAST_MODE],
        "calibration_status": CALIBRATION_STATUS,
        "engine_version": PRODUCT_VERSION,
        # Nobody has told this case what to protect. An empty list is the honest record; claiming
        # preservation of features we were never told about would be an invented fact.
        "preserve": [],
        # Every node the graph will execute, with the same fields the graph carries — including
        # `enabled` and `reason`, which are part of the graph's render identity (its digest). A
        # descriptor that dropped them could not reproduce the digest it is supposed to explain.
        "parameters": {"nodes": [
            {"id": node["id"], "type": node["type"], "enabled": True,
             "parameters": get_provider(node["type"]).validate_parameters(node["parameters"]),
             "reason": node["reason"]}
            for node in _TIER_NODES[tier]
        ]},
    }


def build_tier_graph(tier: str, source: str | Path) -> MixGraph:
    """Build the (validated) mix graph for one tier. Reuses the mix_graph node providers."""
    if tier not in TIER_ORDER:
        raise TuningError(f"unknown tier '{tier}'; the closed set is {', '.join(TIER_ORDER)}")
    nodes: list[dict[str, Any]] = []
    for node in _TIER_NODES[tier]:
        nodes.append({
            "id": node["id"],
            "type": node["type"],
            "enabled": True,
            "parameters": get_provider(node["type"]).validate_parameters(node["parameters"]),
            "reason": node["reason"],
        })
    return MixGraph(
        source=Path(source),
        nodes=nodes,
        intent=f"fast-stereo-only {tier} tier (engineering default, uncalibrated)",
        verification={"max_peak_dbfs": -1.0},
        provenance={"created_by": "moodify.tuning", "notes": f"tier={tier} mode={FAST_MODE}"},
        notes=(
            "Whole-track mix_graph chain only. No per-stem processing, no pitch/timing correction, "
            "no claim about the original stems."
        ),
    )


# ── hard gates ──────────────────────────────────────────────────────────────────


def check_side(source: Path, output: Path) -> list[dict]:
    """The hard gates of MIP-0002 Addendum A §A.8 for one rendered side.

    Every gate is recorded with what was measured, so a reader can recompute rather than trust.
    A failing gate raises: it never becomes a note that the caller might skip.
    """
    source_audio, source_sr = load_audio(str(source), always_2d=True)
    output_audio, output_sr = load_audio(str(output), always_2d=True)
    delta = int(output_audio.shape[0]) - int(source_audio.shape[0])
    peak_ok = bool(np.all(np.isfinite(output_audio))) and float(np.max(np.abs(output_audio))) <= 1.0

    gates = [
        {"gate": "decodable", "passed": True,
         "measured": {"sample_rate": int(output_sr), "channels": int(output_audio.shape[1])}},
        {"gate": "duration_preserved", "passed": abs(delta) <= LENGTH_TOLERANCE_SAMPLES,
         "measured": {"delta_samples": delta, "tolerance_samples": LENGTH_TOLERANCE_SAMPLES}},
        {"gate": "sample_rate_preserved", "passed": int(output_sr) == int(source_sr),
         "measured": {"source": int(source_sr), "output": int(output_sr)}},
        {"gate": "channels_preserved", "passed": int(output_audio.shape[1]) == int(source_audio.shape[1]),
         "measured": {"source": int(source_audio.shape[1]), "output": int(output_audio.shape[1])}},
        {"gate": "finite_output", "passed": bool(np.all(np.isfinite(output_audio))),
         "measured": {"finite": bool(np.all(np.isfinite(output_audio)))}},
        {"gate": "within_full_scale", "passed": peak_ok,
         "measured": {"sample_peak_dbfs": round(
             float(20.0 * np.log10(max(float(np.max(np.abs(output_audio))), 1e-12))), 2)}},
    ]
    failed = [g["gate"] for g in gates if not g["passed"]]
    if failed:
        raise TuningError(f"hard gate failed for {output.name}: {', '.join(failed)}")
    return gates


# ── one side ────────────────────────────────────────────────────────────────────


def _render_side(source: Path, work_dir: Path, final_dir: Path, tier: str, source_sha256: str) -> dict:
    """Render one tier and write its plan + evidence into `work_dir`.

    `work_dir` is the temporary attempt location the bytes are written to; `final_dir` is where
    this side will live once the pair is published. Artifacts record **final** paths (so a
    published pair never cites a directory that no longer exists) while the render-step record
    states plainly that the render happened in the attempt directory and was relocated.
    """
    side = SIDE_OF_TIER[tier]
    descriptor = tier_descriptor(tier)
    graph = build_tier_graph(tier, source)

    render_dir = work_dir / "render"
    render_dir.mkdir(parents=True, exist_ok=True)
    mix_graph_evidence = run_session(graph, render_dir)

    rendered = Path(mix_graph_evidence["output"]["path"])
    if not rendered.is_file():
        raise TuningError(f"tier {tier}: renderer reported success but wrote no output file")

    # Publish layout: mix.wav is the whole-track result, tuned/source.wav is this mode's single
    # "tuned" slot. For a one-track mode the composite step is the identity of the same signal;
    # `plan.json` records that rather than leaving it implied.
    work_dir.mkdir(parents=True, exist_ok=True)
    mix = work_dir / "mix.wav"
    shutil.move(str(rendered), str(mix))
    tuned_dir = work_dir / "tuned"
    tuned_dir.mkdir(parents=True, exist_ok=True)
    tuned = tuned_dir / "source.wav"
    shutil.copyfile(mix, tuned)
    shutil.rmtree(render_dir, ignore_errors=True)

    gates = check_side(source, mix)

    verification = mix_graph_evidence.get("verification") or {}
    after = verification.get("after") or {}
    mix_sha256 = mix_graph_evidence["output"].get("sha256")
    tuned_sha256 = _sha256(tuned)

    plan = {
        **descriptor,
        "graph_digest_sha256": mix_graph_evidence.get("graph_digest_sha256"),
        "composite": "identity_single_track",
        "rationale": "整轨 mix_graph 链；两档为工程默认值，未校准；B 只代表变化更充分。",
        "source": str(source),
        "source_sha256": source_sha256,
        "created_at": _utc_now(),
    }
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "tier": descriptor,
        "mode": MODE_LABELS[FAST_MODE],
        "calibration_status": CALIBRATION_STATUS,
        "engine_version": PRODUCT_VERSION,
        "core_version": PRODUCT_VERSION,
        # Generating is not finishing: the machine processed and measured, a human still listens.
        "review_required": True,
        "status": "rendered_review_required",
        "source": str(source),
        "source_sha256": source_sha256,
        # Final, published locations — never the temporary attempt path.
        "output": {
            "mix_wav": str(final_dir / "mix.wav"),
            "mix_sha256": mix_sha256,
            "tuned_wav": str(final_dir / "tuned" / "source.wav"),
            "tuned_sha256": tuned_sha256,
        },
        "render_step": {
            "rendered_to": str(rendered),
            "relocated_to": str(final_dir),
            "note": "渲染在临时 attempt 目录内完成，发布时整目录重命名；音频内容未变，sha256 未变。",
        },
        "graph_digest_sha256": mix_graph_evidence.get("graph_digest_sha256"),
        "verification": verification,
        "duration_s": after.get("duration_s"),
        "sample_rate": after.get("sample_rate"),
        "channels": after.get("channels"),
        "finite": after.get("finite"),
        "checks": gates,
        "review_note": REVIEW_NOTE,
        # Verbatim, never paraphrased: whoever audits this reads Core's own record, including the
        # attempt path it wrote for the render step (see render_step above).
        "mix_graph_evidence": mix_graph_evidence,
    }
    _write_json(work_dir / "plan.json", plan)
    _write_json(work_dir / "evidence.json", evidence)

    return {
        "side": side,
        "tier": tier,
        "dir": str(final_dir),
        "plan": str(final_dir / "plan.json"),
        "mix_wav": str(final_dir / "mix.wav"),
        "mix_sha256": mix_sha256,
        "tuned_wav": str(final_dir / "tuned" / "source.wav"),
        "tuned_sha256": tuned_sha256,
        "evidence": str(final_dir / "evidence.json"),
        "graph_digest_sha256": mix_graph_evidence.get("graph_digest_sha256"),
        "review_required": True,
        "checks": gates,
    }


# ── the pair ────────────────────────────────────────────────────────────────────


def render_pair(source: str | Path, output_dir: str | Path, *,
                pair_id: str | None = None, mode: str = FAST_MODE) -> dict:
    """Render one complete A/B pair into `output_dir`; return the JSON payload for the CLI.

    Fails without writing anything when: the mode or tier set is unknown, the source is missing or
    not an audio file, `output_dir` already exists, or either side fails to render/verify.
    """
    if mode not in MODES:
        raise TuningError(f"unknown mode '{mode}'; supported: {', '.join(MODES)}")

    source_path = Path(source)
    if not source_path.is_file():
        raise TuningError(f"source is not a file: {source_path}")
    if source_path.suffix.lower() not in AUDIO_EXTENSIONS:
        raise TuningError(f"unsupported audio extension: {source_path.suffix or '(none)'}")

    target = Path(output_dir)
    if target.exists():
        # A pair is a record of one attempt; a second attempt is a new pair, never an overwrite.
        raise TuningError(f"refusing to overwrite existing pair: {target}")

    resolved_pair_id = pair_id or (target.name if target.name else None) or new_pair_id()
    target.parent.mkdir(parents=True, exist_ok=True)

    attempt = target.parent / f".{target.name}.attempt-{uuid4().hex[:8]}"
    if attempt.exists():
        raise TuningError(f"attempt directory already exists: {attempt}")
    attempt.mkdir(parents=True)

    source_sha256 = _sha256(source_path)
    try:
        sides: dict[str, dict] = {}
        for tier in TIER_ORDER:
            side = SIDE_OF_TIER[tier]
            sides[side] = _render_side(
                source_path, attempt / side, target / side, tier, source_sha256)

        if set(sides) != {"A", "B"}:
            raise TuningError("a pair must contain exactly the A and B sides")

        # Two candidates that are byte-identical are not two candidates. This is a stop condition
        # in the Phase 2 brief, not a curiosity: reporting "A / B" over one sound would be the
        # fake-A/B failure the whole stage exists to prevent.
        if sides["A"]["mix_sha256"] == sides["B"]["mix_sha256"]:
            raise TuningError(
                "tiers produced identical output; refusing to publish a pair of identical candidates")

        pair = {
            "schema": PAIR_SCHEMA,
            "pair_id": resolved_pair_id,
            "mode": MODE_LABELS[mode],
            "source": str(source_path),
            "source_sha256": source_sha256,
            "tiers": {side: sides[side]["tier"] for side in ("A", "B")},
            "calibration_status": CALIBRATION_STATUS,
            "engine_version": PRODUCT_VERSION,
            "created_at": _utc_now(),
            "composite": "identity_single_track",
            "note": (
                "两个完整整轨候选（A 保守 / B 充分）；无逐轨处理、无音准/节奏修正、未校准。"
                "仅当 A、B 两侧产物齐备时才发布。"
            ),
        }
        _write_json(attempt / "pair.json", pair)

        # Publish with one rename: until this line there is no <pair_id> on disk at all.
        os.replace(attempt, target)
    except BaseException:
        shutil.rmtree(attempt, ignore_errors=True)
        raise

    return {
        "status": "rendered",
        "pair_id": resolved_pair_id,
        "pair_dir": str(target),
        "pair_json": str(target / "pair.json"),
        "mode": MODE_LABELS[mode],
        "source": str(source_path),
        "source_sha256": source_sha256,
        "calibration_status": CALIBRATION_STATUS,
        "engine_version": PRODUCT_VERSION,
        "review_required": True,
        "tiers": pair["tiers"],
        "sides": sides,
        "checks": {
            "both_sides_published": True,
            # Guaranteed true on the success path: identical candidates are refused above.
            "distinct_outputs": True,
        },
    }
