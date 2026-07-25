from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from moodify.domain import (
    TreatmentAction,
    TreatmentPlan,
    TreatmentStepType,
    TreatmentVariant,
)


def _action(
    action_id: str = "action-spectrum",
    order: int = 1,
) -> TreatmentAction:
    return TreatmentAction(
        action_id=action_id,
        order=order,
        step_type=TreatmentStepType.SPECTRAL_BALANCE,
        public_summary="柔和控制刺耳频段",
        reason="诊断显示人声存在高频刺激",
        target_metrics={"spectral_harshness": 0.25},
        parameter_bounds={"presence_adjustment_db": (-2.0, 0.0)},
        prerequisites=["diagnosis-ready"],
    )


def _variant(
    variant_id: str = "variant-a",
    label: str = "A",
    actions: list[TreatmentAction] | None = None,
) -> TreatmentVariant:
    return TreatmentVariant(
        variant_id=variant_id,
        label=label,
        name="Natural Repair",
        objective="自然修复并保留原始情绪",
        problems=["高频刺激"],
        preserve=["原始旋律", "自然动态"],
        actions=actions or [_action()],
        risks=["修复不足"],
        expected_output="更平衡但仍保持自然的人声",
        target_metrics={"integrated_lufs": -14.0},
    )


def _plan(**overrides) -> TreatmentPlan:
    data = {
        "plan_id": "plan-001",
        "project_id": "project-001",
        "brief_revision": 1,
        "diagnosis_id": "diagnosis-001",
        "variants": [_variant()],
        "recommended_variant_id": "variant-a",
        "recommendation_reason": "最符合保留自然动态的目标",
        "created_by_thread_id": "thread-design-001",
    }
    data.update(overrides)
    return TreatmentPlan(**data)


def test_treatment_plan_round_trip_json():
    plan = _plan()

    restored = TreatmentPlan.model_validate_json(plan.model_dump_json())

    assert restored == plan
    assert restored.schema_version == "treatment_plan.v1"


def test_plan_supports_ordered_ab_candidates():
    plan = _plan(
        variants=[
            _variant(),
            _variant("variant-b", "B"),
        ],
        recommended_variant_id="variant-b",
        recommendation_reason="更适合叙事型人声",
    )

    assert [variant.label for variant in plan.variants] == ["A", "B"]


def test_plan_requires_one_to_three_candidates():
    with pytest.raises(ValidationError):
        _plan(variants=[])

    with pytest.raises(ValidationError):
        _plan(
            variants=[
                _variant("v-a", "A"),
                _variant("v-b", "B"),
                _variant("v-c", "C"),
                _variant("v-d", "C"),
            ]
        )


def test_variant_labels_must_start_at_a_and_be_unique():
    with pytest.raises(ValidationError):
        _plan(
            variants=[_variant("variant-b", "B")],
            recommended_variant_id=None,
            recommendation_reason=None,
        )

    with pytest.raises(ValidationError):
        _plan(
            variants=[_variant(), _variant("variant-b", "A")],
            recommended_variant_id=None,
            recommendation_reason=None,
        )


def test_recommendation_must_reference_candidate_and_have_reason():
    with pytest.raises(ValidationError):
        _plan(recommended_variant_id="missing")

    with pytest.raises(ValidationError):
        _plan(recommendation_reason=None)

    with pytest.raises(ValidationError):
        _plan(recommended_variant_id=None)


def test_action_order_must_be_contiguous_and_ids_unique():
    with pytest.raises(ValidationError):
        _variant(actions=[_action("one", 1), _action("two", 3)])

    with pytest.raises(ValidationError):
        _variant(actions=[_action("same", 1), _action("same", 2)])


def test_parameter_bounds_must_be_ordered():
    with pytest.raises(ValidationError):
        TreatmentAction(
            action_id="bad-bounds",
            order=1,
            step_type=TreatmentStepType.DYNAMIC_SHAPING,
            public_summary="控制动态",
            reason="避免过度压缩",
            parameter_bounds={"ratio": (4.0, 2.0)},
        )


def test_plan_rejects_secret_parameters_and_source_paths():
    action = _action()
    with pytest.raises(ValidationError):
        TreatmentAction.model_validate(
            {
                **action.model_dump(),
                "private_parameters": {"eq_gain_db": -1.5},
            }
        )

    with pytest.raises(ValidationError):
        TreatmentAction.model_validate(
            {
                **action.model_dump(),
                "source_audio_path": "C:/secret/original.wav",
            }
        )


def test_variant_requires_problem_risk_action_and_expected_output():
    base = _variant().model_dump()
    for field, invalid in [
        ("problems", []),
        ("risks", []),
        ("actions", []),
        ("expected_output", ""),
    ]:
        with pytest.raises(ValidationError):
            TreatmentVariant.model_validate({**base, field: invalid})


def test_text_lists_reject_blanks_and_casefolded_duplicates():
    with pytest.raises(ValidationError):
        _variant().model_copy(
            update={"preserve": ["Natural Dynamics", "natural dynamics"]}
        ).model_validate(
            {
                **_variant().model_dump(),
                "preserve": ["Natural Dynamics", "natural dynamics"],
            }
        )

    with pytest.raises(ValidationError):
        TreatmentVariant.model_validate(
            {**_variant().model_dump(), "risks": [" "]}
        )


def test_created_at_must_be_timezone_aware():
    with pytest.raises(ValidationError):
        _plan(created_at=datetime(2026, 7, 25))

    aware = _plan(created_at=datetime(2026, 7, 25, tzinfo=timezone.utc))
    assert aware.created_at.utcoffset() is not None


def test_models_are_frozen_and_reject_unknown_fields():
    plan = _plan()

    with pytest.raises(ValidationError):
        plan.plan_id = "changed"

    with pytest.raises(ValidationError):
        TreatmentPlan.model_validate({**plan.model_dump(), "unknown": True})
