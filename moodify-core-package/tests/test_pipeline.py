"""W01-P05 Pipeline tests — TST-01..15 + integration compute run (synthetic wav)."""

from __future__ import annotations

import json
import struct
import wave
from pathlib import Path

import pytest

from moodify.data_plane.adapter import LocalFileAdapter
from moodify.data_plane.control import JobControlPlane
from moodify.data_plane.ids import new_id
from moodify.data_plane.pipeline import (
    PipelineError,
    PipelineRunner,
    ScratchManager,
    production_fingerprint,
)
from moodify.data_plane.repository import DataPlaneRepository


def make_sine_wav(path: Path, *, seconds: float = 1.0, rate: int = 44100) -> None:
    frames = int(seconds * rate)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        data = b"".join(
            struct.pack("<h", int(12000 * (0.5 + 0.5 * __import__("math").sin(2 * 3.14159 * 440 * i / rate))))
            for i in range(frames)
        )
        w.writeframes(data)


class _FakeSeparator:
    """Adapter double: records calls; never actually separates."""

    def __init__(self) -> None:
        self.calls = 0

    def separate(self, input_path, requested_roles):
        self.calls += 1
        return {"provider": "fake-lalal", "provider_job_id": "lalal-job-1",
                "stems": ["vocals", "instrumental"]}


@pytest.fixture()
def env(tmp_path):
    repo = DataPlaneRepository(tmp_path / "plane.sqlite3")
    cp = JobControlPlane(repo)
    store = LocalFileAdapter(tmp_path / "store")
    scratch = ScratchManager(tmp_path / "scratch")
    yield {"repo": repo, "cp": cp, "store": store, "scratch": scratch, "tmp": tmp_path}
    repo.close()


def _setup_job(env, *, with_source=True):
    repo, cp, store = env["repo"], env["cp"], env["store"]
    job_id, track_id = new_id("job"), new_id("track")
    cp.enqueue(job_id=job_id, track_id=track_id, job_type="reconstruction")
    claimed = cp.claim(job_id=job_id, worker_id="worker-a")
    src_obj = None
    if with_source:
        src_obj = new_id("object")
        wav = env["tmp"] / "src.wav"
        make_sine_wav(wav)
        data = wav.read_bytes()
        key = f"moodify/tracks/{track_id}/source/{src_obj}.wav"
        h = store.put("moodify", key, data)
        repo.register_track(track_id=track_id, source_hash=h, source_object_id=src_obj)
        repo.register_object(object_id=src_obj, track_id=track_id, artifact_type="source",
                             bucket="moodify", object_key=key, content_hash=h,
                             byte_size=len(data), producer="test", retention_class="source_long_lived")
    return job_id, track_id, claimed, src_obj


def _runner(env, **kw):
    return PipelineRunner(repo=env["repo"], store_adapter=env["store"],
                          scratch=env["scratch"], **kw)


# ---------- TST-01 — Source integrity ----------
def test_tst01_source_integrity(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"}, profile_id="clean_master")
    runner = _runner(env)
    result = runner.run(ctx)
    assert isinstance(result, object) and hasattr(result, "stage_results")
    acquire = next(s for s in result.stage_results if s["stage"] == "ACQUIRE")
    assert acquire["metrics"]["hash_ok"] is True


# ---------- TST-02 — Invalid audio -> INPUT_INVALID ----------
def test_tst02_invalid_audio(env):
    repo, store = env["repo"], env["store"]
    job_id, track_id, claimed, _ = _setup_job(env, with_source=False)
    # register garbage bytes as source
    src_obj = new_id("object")
    key = f"moodify/tracks/{track_id}/source/{src_obj}.wav"
    garbage = b"not-a-wav-file-at-all" * 100
    h = store.put("moodify", key, garbage)
    repo.register_track(track_id=track_id, source_hash=h, source_object_id=src_obj)
    repo.register_object(object_id=src_obj, track_id=track_id, artifact_type="source",
                         bucket="moodify", object_key=key, content_hash=h,
                         byte_size=len(garbage), producer="test", retention_class="source_long_lived")
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    with pytest.raises(PipelineError) as ei:
        _runner(env).run(ctx)
    assert ei.value.failure_class == "INPUT_INVALID"


# ---------- TST-03 — Optional stem bypass ----------
def test_tst03_optional_stem_bypass(env):
    sep = _FakeSeparator()
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"stem_roles": ["vocals"]})
    result = _runner(env, separator=sep).run(ctx)
    assert sep.calls == 0  # STEM not required by profile -> separator never called
    stem = next(s for s in result.stage_results if s["stage"] == "STEM")
    assert stem["status"] == "BYPASSED"


# ---------- TST-04 — External API transient -> failure class ----------
def test_tst04_external_api_transient(env):
    class _FailSep:
        def separate(self, input_path, requested_roles):
            raise TimeoutError("lalal timeout")

    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"stem_roles": ["vocals"]})
    ctx.stage_overrides = {"STEM": True}
    with pytest.raises(PipelineError) as ei:
        _runner(env, separator=_FailSep()).run(ctx)
    assert ei.value.failure_class == "EXTERNAL_API_TRANSIENT"


# ---------- TST-05 — Judgment BYPASS is legal and continues ----------
def test_tst05_judgment_bypass(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    def judger(metrics):
        return {"action": "BYPASS", "reason": "no_intervention_evidence", "uncertainty": 0.9}
    result = _runner(env, judger=judger).run(ctx)
    intervene = next(s for s in result.stage_results if s["stage"] == "INTERVENE")
    assert intervene["status"] == "BYPASSED"
    assert result.ready_candidate_object_id  # pipeline continued to READY candidate


# ---------- TST-06 — Profile version binding changes fingerprint ----------
def test_tst06_profile_version_binding():
    fp1 = production_fingerprint(pipeline_version="v1", input_hashes=["a"],
                                 stage_config={"x": 1}, profile_version="clean_master@1",
                                 tool_versions={"v01": "1.0"}, render_policy="wav_pcm16_44k")
    fp2 = production_fingerprint(pipeline_version="v1", input_hashes=["a"],
                                 stage_config={"x": 1}, profile_version="clean_master@2",
                                 tool_versions={"v01": "1.0"}, render_policy="wav_pcm16_44k")
    assert fp1 != fp2
    # same semantics -> same fingerprint (TST-10)
    fp3 = production_fingerprint(pipeline_version="v1", input_hashes=["a"],
                                 stage_config={"x": 1}, profile_version="clean_master@1",
                                 tool_versions={"v01": "1.0"}, render_policy="wav_pcm16_44k")
    assert fp1 == fp3


# ---------- TST-07 — Render provenance ----------
def test_tst07_render_provenance(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    result = _runner(env).run(ctx)
    obj = env["repo"].get_object(result.ready_candidate_object_id)
    assert obj["track_id"] == track_id
    assert obj["job_id"] == job_id
    assert obj["pipeline_version"] == "pipeline-v0.1"
    assert result.source_object_id == src_obj


# ---------- TST-08 — Verification failure -> no PASS candidate ----------
def test_tst08_verification_failure(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})

    def bad_renderer(src, profile, out):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"garbage-not-wav")  # render that cannot decode
        return out, {}

    with pytest.raises(PipelineError) as ei:
        _runner(env, renderer=bad_renderer).run(ctx)
    assert ei.value.failure_class == "VERIFICATION_FAILED"


# ---------- TST-09 — Stale lease before upload -> abort ----------
def test_tst09_stale_lease_before_upload(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})

    def lease_check(ctx_):
        # simulate lease expiry mid-run
        from moodify.data_plane.control import TransitionRejected

        raise TransitionRejected("lease expired")

    with pytest.raises(Exception):
        _runner(env, lease_check=lease_check).run(ctx)


# ---------- TST-10 — Duplicate replay same fingerprint ----------
def test_tst10_duplicate_replay_same_fingerprint(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    r1 = _runner(env).run(ctx)
    r2 = _runner(env).run(ctx)
    assert r1.production_fingerprint == r2.production_fingerprint


# ---------- TST-11 — Scratch cleanup ----------
def test_tst11_scratch_cleanup(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    scratch_dir = env["scratch"].job_dir(job_id, claimed["attempt_id"])
    _runner(env).run(ctx)
    assert not scratch_dir.exists()  # cleaned after success


# ---------- TST-12 — No secret logging ----------
def test_tst12_no_secret_logging(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    candidate = _runner(env).run(ctx)
    blob = json.dumps(candidate.to_dict())
    # scratch paths legitimately contain "scratch"; check for actual secret shapes
    assert "api_key=" not in blob.lower() and "bearer " not in blob.lower()
    assert "password=" not in blob.lower() and "accesskey" not in blob.lower()


# ---------- TST-13 — Stage result completeness ----------
def test_tst13_stage_result_completeness(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    result = _runner(env).run(ctx)
    stages = {s["stage"] for s in result.stage_results}
    assert {"ACQUIRE", "VALIDATE", "ANALYZE", "JUDGE", "INTERVENE", "PROFILE", "RENDER", "VERIFY", "REGISTER"} <= stages
    for sr in result.stage_results:
        assert sr["attempt_id"] == claimed["attempt_id"]
        assert sr["status"] in ("SUCCEEDED", "BYPASSED", "FAILED")


# ---------- TST-14 — Durable outputs registered via adapter ----------
def test_tst14_durable_outputs_registered(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    result = _runner(env).run(ctx)
    render = env["repo"].get_object(result.ready_candidate_object_id)
    assert render is not None
    # object physically present in store
    assert env["store"].head(render["bucket"], render["object_key"]) == render["byte_size"]


# ---------- TST-15 — Worker cannot directly write READY ----------
def test_tst15_no_direct_ready_mutation(env):
    repo = env["repo"]
    job_id, track_id, claimed, src_obj = _setup_job(env)

    # pipeline run does not touch job state at all
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"})
    _runner(env).run(ctx)
    job = repo.get_job(job_id)
    assert job["current_state"] == "RUNNING"  # still RUNNING; READY only via control plane


# ---------- Integration: full compute run on synthetic wav ----------
def test_integration_full_compute_run(env):
    job_id, track_id, claimed, src_obj = _setup_job(env)
    from moodify.data_plane.pipeline import JobContext

    ctx = JobContext(job_id=job_id, track_id=track_id, attempt_id=claimed["attempt_id"],
                     lease_id=claimed["lease_id"], worker_id="worker-a",
                     pipeline_version="pipeline-v0.1", source_object_id=src_obj,
                     config={"render_policy": "wav_pcm16_44k"}, profile_id="clean_master",
                     profile_version="clean_master@1")
    candidate = _runner(env).run(ctx)
    assert candidate.verification_result == "PASS"
    assert candidate.ready_candidate_object_id
    # complete via control plane (P04 authority)
    env["cp"].complete(job_id=job_id, lease_id=claimed["lease_id"], worker_id="worker-a",
                       ready_object_id=candidate.ready_candidate_object_id,
                       verification_evidence=True)
    assert repo_job_state(env, job_id) == "READY"


def repo_job_state(env, job_id: str) -> str:
    return env["repo"].get_job(job_id)["current_state"]
