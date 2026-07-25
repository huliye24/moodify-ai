from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from moodify.domain import ProjectThread, ThreadRole, ThreadStatus, ThreadType


BASE_TIME = datetime(2026, 7, 25, 8, 0, tzinfo=timezone.utc)


def make_thread(**overrides):
    data = {
        "thread_id": "THR_001",
        "project_id": "PRJ_001",
        "thread_type": ThreadType.DIAGNOSIS,
        "role": ThreadRole.ANALYST,
        "created_at": BASE_TIME,
        "updated_at": BASE_TIME,
    }
    data.update(overrides)
    return ProjectThread(**data)


def test_project_thread_round_trip_json():
    thread = make_thread(
        current_task_id="TASK_001",
        inputs={"artifact_ids": ["ART_001"]},
    )

    restored = ProjectThread.model_validate_json(thread.model_dump_json())

    assert restored == thread
    assert restored.schema_version == "project_thread.v1"
    assert restored.status is ThreadStatus.PLANNED


@pytest.mark.parametrize(
    ("thread_type", "role"),
    [
        (ThreadType.BRIEF, ThreadRole.PRODUCER),
        (ThreadType.DIAGNOSIS, ThreadRole.ANALYST),
        (ThreadType.DESIGN, ThreadRole.DESIGNER),
        (ThreadType.VOCAL, ThreadRole.WORKER),
        (ThreadType.JUDGE, ThreadRole.JUDGE),
        (ThreadType.ARCHIVE, ThreadRole.ARCHIVE),
    ],
)
def test_thread_type_requires_the_expected_role(thread_type, role):
    thread = make_thread(thread_type=thread_type, role=role)
    assert thread.role is role


def test_thread_rejects_role_mismatch():
    with pytest.raises(ValidationError, match="require role"):
        make_thread(role=ThreadRole.WORKER)


def test_happy_path_state_transitions_are_timestamped():
    queued = make_thread().transition_to(
        ThreadStatus.QUEUED, at=BASE_TIME + timedelta(seconds=1)
    )
    running = queued.transition_to(
        ThreadStatus.RUNNING, at=BASE_TIME + timedelta(seconds=2)
    )
    passed = running.transition_to(
        ThreadStatus.PASSED,
        at=BASE_TIME + timedelta(seconds=3),
        outputs={"report_id": "RPT_001"},
    )

    assert passed.status is ThreadStatus.PASSED
    assert passed.started_at == BASE_TIME + timedelta(seconds=2)
    assert passed.finished_at == BASE_TIME + timedelta(seconds=3)
    assert passed.outputs == {"report_id": "RPT_001"}


def test_awaiting_user_can_resume_running():
    running = (
        make_thread()
        .transition_to(ThreadStatus.QUEUED, at=BASE_TIME + timedelta(seconds=1))
        .transition_to(ThreadStatus.RUNNING, at=BASE_TIME + timedelta(seconds=2))
    )
    waiting = running.transition_to(
        ThreadStatus.AWAITING_USER, at=BASE_TIME + timedelta(seconds=3)
    )
    resumed = waiting.transition_to(
        ThreadStatus.RUNNING, at=BASE_TIME + timedelta(seconds=4)
    )

    assert resumed.status is ThreadStatus.RUNNING
    assert resumed.started_at == running.started_at


def test_illegal_transition_is_rejected():
    with pytest.raises(ValueError, match="illegal thread transition"):
        make_thread().transition_to(
            ThreadStatus.PASSED, at=BASE_TIME + timedelta(seconds=1)
        )


def test_failed_thread_requires_error_and_can_retry():
    running = (
        make_thread(max_retries=1)
        .transition_to(ThreadStatus.QUEUED, at=BASE_TIME + timedelta(seconds=1))
        .transition_to(ThreadStatus.RUNNING, at=BASE_TIME + timedelta(seconds=2))
    )

    with pytest.raises(ValidationError, match="require an error"):
        running.transition_to(
            ThreadStatus.FAILED, at=BASE_TIME + timedelta(seconds=3)
        )

    failed = running.transition_to(
        ThreadStatus.FAILED,
        at=BASE_TIME + timedelta(seconds=3),
        error="analyzer unavailable",
    )
    retried = failed.queue_retry(
        at=BASE_TIME + timedelta(seconds=4), task_id="TASK_002"
    )

    assert retried.status is ThreadStatus.QUEUED
    assert retried.retry_count == 1
    assert retried.error is None
    assert retried.current_task_id == "TASK_002"


def test_retry_limit_is_enforced():
    failed = make_thread(
        status=ThreadStatus.FAILED,
        error="persistent failure",
        max_retries=1,
        retry_count=1,
        started_at=BASE_TIME,
        finished_at=BASE_TIME + timedelta(seconds=1),
        updated_at=BASE_TIME + timedelta(seconds=1),
    )

    with pytest.raises(ValueError, match="retry limit"):
        failed.queue_retry(at=BASE_TIME + timedelta(seconds=2))


def test_thread_timestamps_must_be_aware_and_ordered():
    with pytest.raises(ValidationError, match="timezone-aware"):
        make_thread(created_at=BASE_TIME.replace(tzinfo=None))

    with pytest.raises(ValidationError, match="earlier than created_at"):
        make_thread(updated_at=BASE_TIME - timedelta(seconds=1))


def test_unknown_fields_are_rejected_and_model_is_frozen():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        make_thread(chat_messages=[])

    thread = make_thread()
    with pytest.raises(ValidationError):
        thread.status = ThreadStatus.RUNNING
