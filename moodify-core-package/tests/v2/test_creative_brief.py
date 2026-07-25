import pytest
from pydantic import ValidationError

from moodify.domain import AudioProject, CreativeBrief


def make_brief(**overrides):
    data = {
        "goal": "温暖、靠近的人声，同时保留梦幻氛围",
        "preserve": ["原始旋律", "自然动态"],
        "avoid": ["高频刺耳", "过度压缩"],
        "platform": "streaming",
        "reference": ["Reference Track A"],
    }
    data.update(overrides)
    return CreativeBrief(**data)


def test_creative_brief_round_trip_supports_chinese_and_english():
    brief = make_brief()

    restored = CreativeBrief.model_validate_json(brief.model_dump_json())

    assert restored == brief
    assert restored.schema_version == "creative_brief.v1"
    assert restored.goal.startswith("温暖")
    assert restored.reference == ["Reference Track A"]


def test_creative_brief_can_be_updated_with_assignment_validation():
    brief = make_brief()

    brief.goal = "Warm, intimate vocals with a dream-like atmosphere"
    brief.platform = "short-video"
    brief.reference = ["参考曲 B"]

    assert brief.goal.startswith("Warm")
    assert brief.platform == "short-video"
    assert brief.reference == ["参考曲 B"]


@pytest.mark.parametrize("field", ["goal", "platform"])
def test_creative_brief_requires_goal_and_platform(field):
    with pytest.raises(ValidationError):
        make_brief(**{field: "   "})


@pytest.mark.parametrize("field", ["preserve", "avoid", "reference"])
def test_creative_brief_rejects_blank_or_duplicate_list_items(field):
    with pytest.raises(ValidationError):
        make_brief(**{field: ["Item", " item "]})

    with pytest.raises(ValidationError):
        make_brief(**{field: ["valid", "   "]})


def test_preserve_and_avoid_cannot_conflict():
    with pytest.raises(ValidationError, match="must not contain the same item"):
        make_brief(preserve=["Natural Dynamics"], avoid=["natural dynamics"])


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        make_brief(private_dsp_parameters={"ratio": 4})


def test_audio_project_coerces_brief_dict_to_creative_brief():
    project = AudioProject(
        project_id="PRJ_001",
        title="Golden Path Song",
        source_audio_ids=["ART_001"],
        creative_brief={
            "goal": "Release-ready balance",
            "preserve": ["emotion"],
            "avoid": ["clipping"],
            "platform": "streaming",
            "reference": [],
        },
    )

    assert isinstance(project.creative_brief, CreativeBrief)
    assert project.model_dump()["creative_brief"]["goal"] == "Release-ready balance"
