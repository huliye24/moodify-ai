from datetime import datetime, timedelta, timezone
import shutil

import pytest

from moodify.domain import (
    AudioProject,
    ProjectWorkflow,
    ThreadStatus,
    WorkflowStage,
)
from moodify.services import AnalystService
from moodify.storage import StorageConflict, WorkspaceStore


BASE = datetime(2026, 7, 25, 10, 0, tzinfo=timezone.utc)


def _clock(*times):
    values = iter(times)
    return lambda: next(values)


@pytest.fixture()
def workspace(tmp_path):
    store = WorkspaceStore(tmp_path)
    store.create_project(
        AudioProject(
            project_id="project-001",
            title="Analyst 测试",
            source_audio_ids=["source-001"],
            created_at=BASE,
            updated_at=BASE,
        )
    )
    workflow = ProjectWorkflow(
        project_id="project-001",
        created_at=BASE,
        updated_at=BASE,
    )
    workflow = workflow.advance(at=BASE + timedelta(seconds=1))
    workflow = workflow.advance(at=BASE + timedelta(seconds=2))
    store.create_workflow(workflow)
    source_dir = tmp_path / "projects" / "project-001" / "sources"
    source_dir.mkdir(parents=True)
    (source_dir / "source-001.wav").write_bytes(b"fake-audio")
    return store, tmp_path


def _result(source_path, output_dir):
    assert source_path.name == "source-001.wav"
    assert output_dir.name == "diagnosis-001"
    return {
        "scan": {"exists": True, "readable": True},
        "metrics": {"duration_s": 12.5, "sample_rate": 48000},
        "diagnosis": {
            "overall_health": "fair",
            "issues": ["presence forward"],
            "strengths": ["healthy dynamics"],
            "suggested_presets": ["clean_master"],
        },
        "spectrum_path": "source-001_diagnosis_spectrum.png",
    }


def test_analyst_success_persists_report_and_advances_workflow(workspace):
    store, _ = workspace
    service = AnalystService(
        store,
        runner=_result,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )

    thread = service.run_diagnosis("project-001", "diagnosis-001")

    assert thread.status is ThreadStatus.PASSED
    assert thread.outputs["diagnosis"]["overall_health"] == "fair"
    assert thread.outputs["analyzed_at"].endswith("+00:00")
    assert store.get_thread("project-001", "diagnosis-001") == thread
    assert store.get_workflow("project-001").stage is WorkflowStage.DESIGN


def test_analyst_records_source_id_without_leaking_absolute_path(workspace):
    store, _ = workspace
    service = AnalystService(
        store,
        runner=_result,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )
    thread = service.run_diagnosis("project-001", "diagnosis-001")

    assert thread.inputs == {"source_audio_id": "source-001"}
    assert "source_audio_path" not in thread.outputs


def test_analyst_failure_marks_thread_and_workflow_failed(workspace):
    store, _ = workspace

    def fail_runner(source_path, output_dir):
        raise RuntimeError("decoder unavailable")

    service = AnalystService(
        store,
        runner=fail_runner,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )
    thread = service.run_diagnosis("project-001", "diagnosis-001")

    assert thread.status is ThreadStatus.FAILED
    assert thread.error == "decoder unavailable"
    workflow = store.get_workflow("project-001")
    assert workflow.stage is WorkflowStage.FAILED
    assert workflow.failure_reason == "Analyst failed: decoder unavailable"


def test_missing_source_is_recorded_as_failure(workspace):
    store, root = workspace
    (root / "projects" / "project-001" / "sources" / "source-001.wav").unlink()
    service = AnalystService(
        store,
        runner=_result,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )

    thread = service.run_diagnosis("project-001", "diagnosis-001")

    assert thread.status is ThreadStatus.FAILED
    assert "source audio not found" in thread.error
    assert store.get_workflow("project-001").stage is WorkflowStage.FAILED


def test_analyst_can_select_an_explicit_project_source(workspace):
    store, root = workspace
    source_dir = root / "projects" / "project-001" / "sources"
    (source_dir / "alternate.flac").write_bytes(b"alternate")

    def selected(source_path, output_dir):
        assert source_path.name == "alternate.flac"
        return _result(
            source_dir / "source-001.wav",
            output_dir,
        )

    service = AnalystService(
        store,
        runner=selected,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )
    thread = service.run_diagnosis(
        "project-001",
        "diagnosis-001",
        source_audio_id="alternate",
    )
    assert thread.inputs["source_audio_id"] == "alternate"


def test_analyst_rejects_wrong_workflow_stage_without_thread(workspace):
    store, _ = workspace
    workflow = store.get_workflow("project-001").advance(
        at=BASE + timedelta(seconds=3)
    )
    store.update_workflow(workflow)
    service = AnalystService(store, runner=_result)

    with pytest.raises(ValueError, match="only during DIAGNOSIS"):
        service.run_diagnosis("project-001", "diagnosis-001")
    assert store.list_threads("project-001") == []


def test_duplicate_thread_id_does_not_rerun_analysis(workspace):
    store, _ = workspace
    calls = 0

    def counted(source_path, output_dir):
        nonlocal calls
        calls += 1
        return _result(source_path, output_dir)

    service = AnalystService(
        store,
        runner=counted,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )
    service.run_diagnosis("project-001", "diagnosis-001")

    with pytest.raises(ValueError):
        service.run_diagnosis("project-001", "diagnosis-001")
    assert calls == 1


def test_source_identifier_ambiguity_is_captured(workspace):
    store, root = workspace
    source_dir = root / "projects" / "project-001" / "sources"
    (source_dir / "source-001.flac").write_bytes(b"duplicate")
    service = AnalystService(
        store,
        runner=_result,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )
    thread = service.run_diagnosis("project-001", "diagnosis-001")
    assert thread.status is ThreadStatus.FAILED
    assert "ambiguous" in thread.error


def test_diagnostic_directory_is_project_isolated(workspace):
    store, root = workspace
    service = AnalystService(
        store,
        runner=_result,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )
    service.run_diagnosis("project-001", "diagnosis-001")

    expected = (
        root / "projects" / "project-001" / "diagnostics" / "diagnosis-001"
    )
    assert expected.is_dir()
    assert not list(root.rglob("*.tmp"))


def test_default_adapter_reuses_v01_scan_analyze_and_diagnose(
    workspace, mock_wav
):
    store, root = workspace
    target = (
        root / "projects" / "project-001" / "sources" / "source-001.wav"
    )
    shutil.copyfile(mock_wav, target)
    service = AnalystService(
        store,
        clock=_clock(
            BASE + timedelta(seconds=3),
            BASE + timedelta(seconds=4),
        ),
    )

    thread = service.run_diagnosis("project-001", "diagnosis-001")

    assert thread.status is ThreadStatus.PASSED
    assert thread.outputs["scan"]["readable"] is True
    assert thread.outputs["metrics"]["sample_rate"] == 44100
    assert thread.outputs["diagnosis"]["overall_health"] in {
        "good",
        "fair",
        "poor",
    }
