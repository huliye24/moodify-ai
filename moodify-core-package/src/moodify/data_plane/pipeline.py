"""Moodify Cloud Audio Compute Pipeline (W01-P05).

内部生产线（非用户 UI）：ACQUIRE → VALIDATE → STEM(optional) → ANALYZE → JUDGE
→ INTERVENE/BYPASS → PROFILE → RENDER → VERIFY → REGISTER → CompletionCandidate。

- Worker 尊重 P04 lease/fencing，不直接写 READY（complete 由上层经 JobControlPlane）。
- 所有 durable output 经 P03 repository.register_object + adapter 注册。
- 所有失败映射到 P04 failure taxonomy（不发明第二套）。
- stage 是进度描述；state 权威仍在 control plane。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
import wave
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

STAGES = ("ACQUIRE", "VALIDATE", "STEM", "ANALYZE", "JUDGE", "INTERVENE", "PROFILE", "RENDER", "VERIFY", "REGISTER")
STAGE_STATUS = ("SUCCEEDED", "BYPASSED", "FAILED")
VERIFY_RESULTS = ("PASS", "FAIL", "HUMAN_REVIEW_REQUIRED")

# artifact types for registration (P03 convention)
ARTIFACT_TYPE_MAP = {
    "STEM": "stems",
    "ANALYZE": "analysis",
    "INTERVENE": "intermediate",
    "RENDER": "renders",
    "VERIFY": "evidence",
}


class PipelineError(Exception):
    """Pipeline failure carrying a P04 failure class."""

    def __init__(self, failure_class: str, failure_code: str, summary: str = "") -> None:
        super().__init__(f"{failure_class}: {failure_code}: {summary}")
        self.failure_class = failure_class
        self.failure_code = failure_code
        self.summary = summary


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _copy_wav(src: Path, dst: Path) -> None:
    dst.write_bytes(src.read_bytes())


@dataclass
class StageResult:
    stage: str
    status: str
    attempt_id: str
    input_objects: list[str] = field(default_factory=list)
    output_objects: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    decision: Any = None
    failure: dict | None = None
    producer_version: str | None = None
    started_at: str = field(default_factory=_now_iso)
    finished_at: str | None = None

    def to_dict(self) -> dict:
        return {
            "stage": self.stage, "status": self.status, "attempt_id": self.attempt_id,
            "input_objects": self.input_objects, "output_objects": self.output_objects,
            "evidence_refs": self.evidence_refs, "metrics": self.metrics,
            "decision": self.decision, "failure": self.failure,
            "producer_version": self.producer_version,
            "started_at": self.started_at, "finished_at": self.finished_at,
        }


@dataclass
class JobContext:
    """Explicit run inputs (no global/implicit discovery)."""
    job_id: str
    track_id: str
    attempt_id: str
    lease_id: str
    worker_id: str
    pipeline_version: str
    source_object_id: str
    config: dict
    profile_id: str | None = None
    profile_version: str | None = None
    stage_overrides: dict | None = None  # e.g. {"STEM": "bypass"}
    correlation_id: str | None = None

    def stage_enabled(self, stage: str, default: bool = True) -> bool:
        if self.stage_overrides and stage in self.stage_overrides:
            return self.stage_overrides[stage] is True
        return default


@dataclass
class CompletionCandidate:
    job_id: str
    track_id: str
    attempt_id: str
    lease_id: str
    pipeline_version: str
    production_fingerprint: str
    source_object_id: str
    ready_candidate_object_id: str
    supporting_object_ids: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    verification_result: str = "PASS"
    resource_summary: dict = field(default_factory=dict)
    stage_results: list[dict] = field(default_factory=list)
    completed_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id, "track_id": self.track_id, "attempt_id": self.attempt_id,
            "lease_id": self.lease_id, "pipeline_version": self.pipeline_version,
            "production_fingerprint": self.production_fingerprint,
            "source_object_id": self.source_object_id,
            "ready_candidate_object_id": self.ready_candidate_object_id,
            "supporting_object_ids": self.supporting_object_ids,
            "evidence_refs": self.evidence_refs, "verification_result": self.verification_result,
            "resource_summary": self.resource_summary, "stage_results": self.stage_results,
            "completed_at": self.completed_at,
        }


# ---------------------------------------------------------------------------
# Production fingerprint (deterministic; not a job id)
# ---------------------------------------------------------------------------

def production_fingerprint(*, pipeline_version: str, input_hashes: list[str],
                           stage_config: dict, profile_version: str | None,
                           tool_versions: dict, render_policy: str) -> str:
    """Stable SHA-256 of the production semantics (TST-06/10)."""
    blob = json.dumps({
        "pipeline_version": pipeline_version,
        "input_hashes": sorted(input_hashes),
        "stage_config": stage_config,
        "profile_version": profile_version,
        "tool_versions": tool_versions,
        "render_policy": render_policy,
    }, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Scratch manager (local disk is scratch, never long-term authority)
# ---------------------------------------------------------------------------

class ScratchManager:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def job_dir(self, job_id: str, attempt_id: str) -> Path:
        d = self.root / job_id / attempt_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def cleanup(self, job_id: str, attempt_id: str, *, keep: bool = False) -> None:
        d = self.root / job_id / attempt_id
        if d.exists() and not keep:
            shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# Pipeline runner
# ---------------------------------------------------------------------------

class PipelineRunner:
    """Run the unified compute pipeline for one claimed job.

    Dependencies are injected via adapters; the runner itself does not touch
    the control plane state machine (complete is called by the caller).
    """

    def __init__(
        self,
        *,
        repo,
        store_adapter,
        scratch: ScratchManager,
        lease_check: Callable[[JobContext], None] | None = None,
        analyzer: Callable[[Path, Path], dict] | None = None,
        judger: Callable[[dict], dict] | None = None,
        renderer: Callable[[Path, dict, Path], tuple[Path, dict]] | None = None,
        separator: Any | None = None,
        logger: Callable[[str, dict], None] | None = None,
    ) -> None:
        self.repo = repo
        self.store = store_adapter
        self.scratch = scratch
        self.lease_check = lease_check
        self.analyzer = analyzer
        self.judger = judger
        self.renderer = renderer
        self.separator = separator
        self.log = logger or (lambda msg, ctx: None)

    # ---------- helpers ----------

    def _checkpoint(self, ctx: JobContext, point: str) -> None:
        self.log(f"lease_checkpoint:{point}", {"job_id": ctx.job_id})
        if self.lease_check is not None:
            self.lease_check(ctx)

    def _sha256(self, p: Path) -> str:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def _register_durable(self, ctx: JobContext, *, artifact_type: str, path: Path,
                          artifact_role: str, mime: str) -> str:
        from moodify.data_plane.ids import new_id
        from moodify.data_plane.object_key import build_object_key

        obj_id = new_id("object")
        key = build_object_key(track_id=ctx.track_id, job_id=ctx.job_id, object_id=obj_id,
                               artifact_type=artifact_type, filename=path.name)
        data = path.read_bytes()
        content_hash = self.store.put(key.bucket, key.key, data)
        self.repo.register_object(
            object_id=obj_id, track_id=ctx.track_id, job_id=ctx.job_id,
            artifact_type=artifact_type, artifact_role=artifact_role, bucket=key.bucket,
            object_key=key.key, content_hash=content_hash, byte_size=len(data),
            mime_type=mime, producer="moodify-pipeline",
            producer_version=ctx.pipeline_version, pipeline_version=ctx.pipeline_version,
            retention_class="render_versioned" if artifact_type == "renders" else "intermediate_short",
        )
        return obj_id

    # ---------- run ----------

    def run(self, ctx: JobContext) -> CompletionCandidate | StageResult:
        results: list[StageResult] = []
        scratch_dir = self.scratch.job_dir(ctx.job_id, ctx.attempt_id)
        try:
            # ACQUIRE
            self._checkpoint(ctx, "before_acquire")
            src = self._stage_acquire(ctx, scratch_dir)
            results.append(src)

            # VALIDATE
            v = self._stage_validate(ctx, scratch_dir)
            results.append(v)

            # STEM (optional)
            if ctx.stage_enabled("STEM", default=False):
                s = self._stage_stem(ctx, scratch_dir)
                results.append(s)
            else:
                results.append(StageResult(stage="STEM", status="BYPASSED", attempt_id=ctx.attempt_id,
                                           decision={"reason": "stem_not_required_by_profile"}))

            # ANALYZE
            a = self._stage_analyze(ctx, scratch_dir)
            results.append(a)

            # JUDGE
            j = self._stage_judge(ctx, results)
            results.append(j)

            # INTERVENE or BYPASS
            if j.decision and j.decision.get("action") == "INTERVENE":
                inter = self._stage_intervene(ctx, scratch_dir, results)
                results.append(inter)
            else:
                results.append(StageResult(stage="INTERVENE", status="BYPASSED", attempt_id=ctx.attempt_id,
                                           decision={"reason": j.decision.get("reason", "no_intervention_evidence")
                                                     if j.decision else "no_judgment"}))

            # PROFILE
            p = self._stage_profile(ctx)
            results.append(p)

            # RENDER
            r = self._stage_render(ctx, scratch_dir, results)
            results.append(r)

            # VERIFY
            vres = self._stage_verify(ctx, results, scratch_dir)
            results.append(vres)
            if vres.decision != "PASS":
                return vres  # verification failed -> no candidate

            # REGISTER (render object + evidence)
            self._checkpoint(ctx, "before_register")
            reg = self._stage_register(ctx, results)
            results.append(reg)

            fp = production_fingerprint(
                pipeline_version=ctx.pipeline_version,
                input_hashes=[self._sha256(scratch_dir / "source" / "input.wav")
                              if (scratch_dir / "source" / "input.wav").exists() else ctx.source_object_id],
                stage_config=ctx.config,
                profile_version=ctx.profile_version,
                tool_versions={"ffmpeg": "system", "v01": "1.0"},
                render_policy=str(ctx.config.get("render_policy", "wav_pcm16_44k")),
            )
            return CompletionCandidate(
                job_id=ctx.job_id, track_id=ctx.track_id, attempt_id=ctx.attempt_id,
                lease_id=ctx.lease_id, pipeline_version=ctx.pipeline_version,
                production_fingerprint=fp, source_object_id=ctx.source_object_id,
                ready_candidate_object_id=reg.decision["render_object_id"],
                supporting_object_ids=reg.decision["supporting_object_ids"],
                evidence_refs=[e for sr in results for e in sr.evidence_refs],
                stage_results=[sr.to_dict() for sr in results],
            )
        finally:
            self.scratch.cleanup(ctx.job_id, ctx.attempt_id)

    # ---------- stages ----------

    def _stage_acquire(self, ctx: JobContext, scratch_dir: Path) -> StageResult:
        sr = StageResult(stage="ACQUIRE", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        try:
            obj = self.repo.get_object(ctx.source_object_id)
            if obj is None:
                raise PipelineError("STORAGE_PERMANENT", "SOURCE_OBJECT_NOT_FOUND", ctx.source_object_id)
            data = self.store.get(obj["bucket"], obj["object_key"])
            dest = scratch_dir / "source" / "input.wav"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            got = self._sha256(dest)
            if got != obj["content_hash"]:
                raise PipelineError("INPUT_INVALID", "SOURCE_HASH_MISMATCH", f"{got} != {obj['content_hash']}")
            sr.input_objects = [ctx.source_object_id]
            sr.metrics = {"byte_size": len(data), "hash_ok": True}
            sr.finished_at = _now_iso()
            return sr
        except PipelineError:
            raise
        except Exception as e:  # noqa: BLE001
            raise PipelineError("STORAGE_TRANSIENT", "ACQUIRE_FAILED", str(e)) from e

    def _stage_validate(self, ctx: JobContext, scratch_dir: Path) -> StageResult:
        sr = StageResult(stage="VALIDATE", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        src = scratch_dir / "source" / "input.wav"
        try:
            with wave.open(str(src), "rb") as w:
                frames = w.getnframes()
                rate = w.getframerate()
                channels = w.getnchannels()
            if frames <= 0:
                raise PipelineError("INPUT_INVALID", "EMPTY_AUDIO", "zero frames")
            duration_ms = int(frames / rate * 1000)
            sr.metrics = {"frames": frames, "sample_rate": rate, "channels": channels,
                          "duration_ms": duration_ms}
            sr.finished_at = _now_iso()
            return sr
        except wave.Error as e:
            raise PipelineError("INPUT_INVALID", "DECODE_FAILED", str(e)) from e

    def _stage_stem(self, ctx: JobContext, scratch_dir: Path) -> StageResult:
        sr = StageResult(stage="STEM", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        if self.separator is None:
            raise PipelineError("EXTERNAL_API_PERMANENT", "SEPARATOR_UNAVAILABLE", "no separator adapter")
        self._checkpoint(ctx, "before_external_submit")
        try:
            res = self.separator.separate(
                scratch_dir / "source" / "input.wav",
                requested_roles=ctx.config.get("stem_roles", ["vocals", "instrumental"]),
            )
            sr.evidence_refs = [res.get("provider_job_id", "")] if res.get("provider_job_id") else []
            sr.metrics = {"provider": res.get("provider"), "stems": len(res.get("stems", []))}
            sr.finished_at = _now_iso()
            return sr
        except PipelineError:
            raise
        except Exception as e:  # noqa: BLE001
            raise PipelineError("EXTERNAL_API_TRANSIENT", "STEM_FAILED", str(e)) from e

    def _stage_analyze(self, ctx: JobContext, scratch_dir: Path) -> StageResult:
        sr = StageResult(stage="ANALYZE", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        src = scratch_dir / "source" / "input.wav"
        try:
            if self.analyzer is None:
                metrics = {"sample_rate": self._quick_rate(src)}
            else:
                out_dir = scratch_dir / "analyze"
                out_dir.mkdir(exist_ok=True)
                metrics = self.analyzer(str(src), str(out_dir))
            sr.metrics = metrics if isinstance(metrics, dict) else {"value": metrics}
            sr.finished_at = _now_iso()
            return sr
        except Exception as e:  # noqa: BLE001
            raise PipelineError("INTERNAL_BUG", "ANALYZE_FAILED", str(e)) from e

    @staticmethod
    def _quick_rate(path: Path) -> int:
        with wave.open(str(path), "rb") as w:
            return w.getframerate()

    def _stage_judge(self, ctx: JobContext, results: list[StageResult]) -> StageResult:
        sr = StageResult(stage="JUDGE", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        analyze = next(r for r in results if r.stage == "ANALYZE")
        try:
            if self.judger is not None:
                judgment = self.judger(analyze.metrics)
            else:
                judgment = {"action": "BYPASS", "reason": "no_intervention_evidence",
                            "observations": [], "uncertainty": 1.0}
            sr.decision = judgment
            sr.metrics = {"action": judgment.get("action")}
            sr.finished_at = _now_iso()
            return sr
        except Exception as e:  # noqa: BLE001
            raise PipelineError("INTERNAL_BUG", "JUDGE_FAILED", str(e)) from e

    def _stage_intervene(self, ctx: JobContext, scratch_dir: Path, results: list[StageResult]) -> StageResult:
        sr = StageResult(stage="INTERVENE", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        src = scratch_dir / "source" / "input.wav"
        try:
            if self.renderer is None:
                raise PipelineError("INTERNAL_BUG", "RENDERER_UNAVAILABLE", "intervene requires renderer")
            out = scratch_dir / "intervene" / "processed.wav"
            out.parent.mkdir(exist_ok=True)
            profile = {"preset": ctx.profile_id, "params": ctx.config.get("intervention_params", {})}
            out_path, params = self.renderer(src, profile, out)
            sr.metrics = {"params": params}
            sr.output_objects = [str(out_path)]
            sr.finished_at = _now_iso()
            return sr
        except PipelineError:
            raise
        except Exception as e:  # noqa: BLE001
            raise PipelineError("PROCESS_CRASH", "INTERVENE_FAILED", str(e)) from e

    def _stage_profile(self, ctx: JobContext) -> StageResult:
        sr = StageResult(stage="PROFILE", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        sr.decision = {
            "profile_id": ctx.profile_id,
            "profile_version": ctx.profile_version,
            "reason": ctx.config.get("profile_reason", "profile_selected"),
            "parameters": ctx.config.get("intervention_params", {}),
        }
        sr.finished_at = _now_iso()
        return sr

    def _stage_render(self, ctx: JobContext, scratch_dir: Path, results: list[StageResult]) -> StageResult:
        sr = StageResult(stage="RENDER", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        src = scratch_dir / "source" / "input.wav"
        inter = next((r for r in results if r.stage == "INTERVENE"), None)
        try:
            out = scratch_dir / "render" / "candidate.wav"
            out.parent.mkdir(parents=True, exist_ok=True)
            source_for_render = Path(inter.output_objects[0]) if inter and inter.output_objects else src
            if self.renderer is None:
                # identity render: preserve original signal (BYPASS semantics)
                _copy_wav(source_for_render, out)
                params = {"render": "identity_copy"}
            else:
                out_path, params = self.renderer(source_for_render, {"preset": ctx.profile_id, "render": True}, out)
                out = out_path
            sr.output_objects = [str(out)]
            sr.metrics = {"params": params}
            sr.finished_at = _now_iso()
            return sr
        except PipelineError:
            raise
        except Exception as e:  # noqa: BLE001
            raise PipelineError("PROCESS_CRASH", "RENDER_FAILED", str(e)) from e

    def _stage_verify(self, ctx: JobContext, results: list[StageResult], scratch_dir: Path) -> StageResult:
        sr = StageResult(stage="VERIFY", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        render = next(r for r in results if r.stage == "RENDER")
        src = scratch_dir / "source" / "input.wav"
        try:
            out_path = Path(render.output_objects[0]) if render.output_objects else src
            with wave.open(str(out_path), "rb") as w:
                frames = w.getnframes()
                rate = w.getframerate()
            if frames <= 0:
                raise PipelineError("VERIFICATION_FAILED", "EMPTY_RENDER", "render produced zero frames")
            if not out_path.exists() or out_path.stat().st_size == 0:
                raise PipelineError("VERIFICATION_FAILED", "RENDER_MISSING", "no render file")
            sr.decision = "PASS"
            sr.metrics = {"render_frames": frames, "render_rate": rate}
            sr.finished_at = _now_iso()
            return sr
        except PipelineError:
            raise
        except Exception as e:  # noqa: BLE001
            raise PipelineError("VERIFICATION_FAILED", "RENDER_UNDECODABLE", str(e)) from e

    def _stage_register(self, ctx: JobContext, results: list[StageResult]) -> StageResult:
        self._checkpoint(ctx, "before_durable_upload")
        sr = StageResult(stage="REGISTER", status="SUCCEEDED", attempt_id=ctx.attempt_id)
        render = next(r for r in results if r.stage == "RENDER")
        out_path = Path(render.output_objects[0])
        render_obj_id = self._register_durable(
            ctx, artifact_type="renders", path=out_path,
            artifact_role="render_candidate", mime="audio/wav",
        )
        # evidence object: verification stage result as json
        ev_path = Path(str(out_path) + ".verify.json")
        ev_path.write_text(json.dumps(render.to_dict(), ensure_ascii=False), encoding="utf-8")
        ev_obj_id = self._register_durable(
            ctx, artifact_type="evidence", path=ev_path,
            artifact_role="verification", mime="application/json",
        )
        self.repo.register_evidence(
            evidence_id=uuid.uuid4().hex[:24], track_id=ctx.track_id, job_id=ctx.job_id,
            evidence_type="pipeline_verification", claim="render candidate passed technical verification",
            evidence_object_id=ev_obj_id,
        )
        sr.decision = {"render_object_id": render_obj_id, "supporting_object_ids": [ev_obj_id]}
        sr.finished_at = _now_iso()
        return sr
