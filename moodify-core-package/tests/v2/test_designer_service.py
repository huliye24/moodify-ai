from datetime import datetime, timedelta, timezone

import pytest

from moodify.domain import (
    AudioProject,
    CreativeBrief,
    ProjectThread,
    ProjectWorkflow,
    ThreadRole,
    ThreadStatus,
    ThreadType,
    WorkflowStage,
)
from moodify.services import DesignerService
from moodify.storage import WorkspaceStore


BASE = datetime(2026, 7, 25, 11, 0, tzinfo=timezone.utc)


def _clock(*times):
    values = iter(times)
    return lambda: next(values)


def _setup(tmp_path, *, health="fair", issues=None, with_brief=True):
    store = WorkspaceStore(tmp_path)
    brief = (
        CreativeBrief(
            goal="温暖、自然且适合流媒体",
            preserve=["自然动态", "人声质感"],
            avoid=["过度压缩"],
            platform="streaming",
            reference=["reference-001"],
        )
        if with_brief
        else None
    )
    store.create_project(
        AudioProject(
            project_id="project-001",
            title="Designer 测试",
            source_audio_ids=["source-001"],
            creative_brief=brief,
            created_at=BASE,
            updated_at=BASE,
        )
    )
    workflow = ProjectWorkflow(
        project_id="project-001",
        created_at=BASE,
        updated_at=BASE,
    )
    for offset in range(1, 4):
        workflow = workflow.advance(at=BASE + timedelta(seconds=offset))
    store.create_workflow(workflow)
    diagnosis = ProjectThread(
        thread_id="diagnosis-001",
        project_id="project-001",
        thread_type=ThreadType.DIAGNOSIS,
        role=ThreadRole.ANALYST,
        status=ThreadStatus.PASSED,
        outputs={
            "diagnosis": {
                "overall_health": health,
                "issues": issues or ["Presence band is forward"],
                "strengths": ["Healthy dynamics"],
                "suggested_presets": ["clean_master"],
            }
        },
        created_at=BASE,
        updated_at=BASE + timedelta(seconds=2),
        started_at=BASE,
        finished_at=BASE + timedelta(seconds=2),
    )
    store.create_thread(diagnosis)
    return store


def _service(store):
    return DesignerService(
        store,
        clock=_clock(
            BASE + timedelta(seconds=4),
            BASE + timedelta(seconds=5),
            BASE + timedelta(seconds=6),
        ),
    )


def test_designer_generates_two_complete_variants_and_advances(tmp_path):
    store = _setup(tmp_path)
    thread = _service(store).generate_plan(
        "project-001", "design-001", "plan-001"
    )

    assert thread.status is ThreadStatus.PASSED
    plan = store.get_plan("project-001", "plan-001")
    assert [variant.label for variant in plan.variants] == ["A", "B"]
    assert all(variant.objective for variant in plan.variants)
    assert all(variant.actions for variant in plan.variants)
    assert all(variant.risks for variant in plan.variants)
    assert all(variant.target_metrics for variant in plan.variants)
    assert store.get_workflow("project-001").stage is WorkflowStage.PROCESS


def test_natural_variant_is_recommended_for_normal_health(tmp_path):
    store = _setup(tmp_path, health="fair")
    _service(store).generate_plan("project-001", "design-001", "plan-001")
    plan = store.get_plan("project-001", "plan-001")

    assert plan.recommended_variant_id == "plan-001-a"
    assert plan.variants[0].preserve == ["自然动态", "人声质感"]
    assert plan.metadata["avoid"] == ["过度压缩"]


def test_focused_variant_is_recommended_for_poor_health(tmp_path):
    store = _setup(
        tmp_path,
        health="poor",
        issues=["harsh", "flat", "too narrow"],
    )
    _service(store).generate_plan("project-001", "design-001", "plan-001")
    plan = store.get_plan("project-001", "plan-001")
    assert plan.recommended_variant_id == "plan-001-b"


def test_plan_actions_have_public_reasons_bounds_and_targets(tmp_path):
    store = _setup(tmp_path)
    _service(store).generate_plan("project-001", "design-001", "plan-001")
    plan = store.get_plan("project-001", "plan-001")

    for variant in plan.variants:
        assert [action.order for action in variant.actions] == [1, 2, 3]
        assert all(action.public_summary for action in variant.actions)
        assert all(action.reason for action in variant.actions)
        assert any(action.parameter_bounds for action in variant.actions)
        assert variant.target_metrics["integrated_lufs"] == -14.0


def test_designer_uses_latest_passed_diagnosis(tmp_path):
    store = _setup(tmp_path)
    newer = ProjectThread(
        thread_id="diagnosis-002",
        project_id="project-001",
        thread_type=ThreadType.DIAGNOSIS,
        role=ThreadRole.ANALYST,
        status=ThreadStatus.PASSED,
        outputs={
            "diagnosis": {
                "overall_health": "poor",
                "issues": ["one", "two", "three"],
            }
        },
        created_at=BASE + timedelta(seconds=2),
        updated_at=BASE + timedelta(seconds=3),
        started_at=BASE + timedelta(seconds=2),
        finished_at=BASE + timedelta(seconds=3),
    )
    store.create_thread(newer)
    _service(store).generate_plan("project-001", "design-001", "plan-001")
    plan = store.get_plan("project-001", "plan-001")
    assert plan.diagnosis_id == "diagnosis-002"
    assert plan.recommended_variant_id == "plan-001-b"


def test_missing_brief_marks_thread_and_workflow_failed(tmp_path):
    store = _setup(tmp_path, with_brief=False)
    service = DesignerService(
        store,
        clock=_clock(
            BASE + timedelta(seconds=4),
            BASE + timedelta(seconds=5),
        ),
    )
    thread = service.generate_plan(
        "project-001", "design-001", "plan-001"
    )
    assert thread.status is ThreadStatus.FAILED
    assert "CreativeBrief" in thread.error
    assert store.get_workflow("project-001").stage is WorkflowStage.FAILED


def test_missing_diagnosis_marks_thread_and_workflow_failed(tmp_path):
    store = _setup(tmp_path)
    path = (
        tmp_path
        / "projects"
        / "project-001"
        / "threads"
        / "diagnosis-001.json"
    )
    path.unlink()
    service = DesignerService(
        store,
        clock=_clock(
            BASE + timedelta(seconds=4),
            BASE + timedelta(seconds=5),
        ),
    )
    thread = service.generate_plan(
        "project-001", "design-001", "plan-001"
    )
    assert thread.status is ThreadStatus.FAILED
    assert "passed Diagnosis" in thread.error


def test_wrong_stage_is_rejected_without_creating_thread(tmp_path):
    store = _setup(tmp_path)
    workflow = store.get_workflow("project-001").advance(
        at=BASE + timedelta(seconds=4)
    )
    store.update_workflow(workflow)

    with pytest.raises(ValueError, match="only during DESIGN"):
        _service(store).generate_plan(
            "project-001", "design-001", "plan-001"
        )
    assert [
        thread.thread_id for thread in store.list_threads("project-001")
    ] == ["diagnosis-001"]


def test_plan_is_create_once_and_project_isolated(tmp_path):
    store = _setup(tmp_path)
    _service(store).generate_plan("project-001", "design-001", "plan-001")
    plan_path = (
        tmp_path / "projects" / "project-001" / "plans" / "plan-001.json"
    )
    assert plan_path.is_file()
    assert not list(tmp_path.rglob("*.tmp"))
