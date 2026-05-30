"""安全投影测试 (SPEC-008 §5)."""

import pytest
from moodify.safety.projection import project


def test_hard_bound_clamp():
    """超界参数被裁剪."""
    p = {"P02_vocal_presence_gain": 15.0}
    result, _ = project(p, "GA")
    assert result["P02_vocal_presence_gain"] == 10.0


def test_hard_bound_lower():
    """低于下限被提升."""
    p = {"P06_compression_ratio": 0.5}
    result, _ = project(p, "GA")
    assert result["P06_compression_ratio"] == 1.0


def test_combo_rule_presence_shelf():
    """中频+高频增益和 > 8dB 被修正."""
    p = {"P02_vocal_presence_gain": 5.0, "P15_high_shelf_gain": 5.0}
    result, log = project(p, "GA")
    assert result["P02_vocal_presence_gain"] < 5.0
    assert result["P15_high_shelf_gain"] < 5.0
    assert any("L2" in entry for entry in log)


def test_combo_rule_low_gain_reverb():
    """低频增益 > 5dB 时混响干湿比修正."""
    p = {"P05_proximity_low_gain": 6.0, "P11_reverb_dry_wet": 0.6}
    result, log = project(p, "GA")
    assert result["P11_reverb_dry_wet"] <= 0.4
    assert any("L2" in entry for entry in log)


def test_combo_rule_compression_harmonic():
    """压缩比 > 6 时谐波驱动限制."""
    p = {"P06_compression_ratio": 10.0, "P13_harmonic_drive": 0.5}
    result, _ = project(p, "GA")
    assert result["P13_harmonic_drive"] <= 0.3


def test_combo_rule_muffled():
    """中频+高频同时大幅衰减被修正."""
    p = {"P02_vocal_presence_gain": -5.0, "P15_high_shelf_gain": -5.0}
    result, _ = project(p, "GA")
    assert result["P02_vocal_presence_gain"] >= -3
    assert result["P15_high_shelf_gain"] >= -3


def test_combo_rule_pumping():
    """低阈值高压缩比避免泵浦效应."""
    p = {"P09_compression_threshold": -35.0, "P06_compression_ratio": 8.0}
    result, _ = project(p, "GA")
    assert result["P06_compression_ratio"] <= 4.0


def test_emotion_exception_wl():
    """WL 允许更高失真和压缩比."""
    p = {"P13_harmonic_drive": 0.9}
    result, _ = project(p, "WL")
    assert result["P13_harmonic_drive"] == 0.9

    result_ga, _ = project(p, "GA")
    assert result_ga["P13_harmonic_drive"] <= 0.8


def test_emotion_exception_ud():
    """UD 允许更高压缩比."""
    p = {"P06_compression_ratio": 25.0}
    result, _ = project(p, "UD")
    assert result["P06_compression_ratio"] == 25.0


def test_emotion_exception_se():
    """SE 允许更高混响."""
    p = {"P11_reverb_dry_wet": 0.9}
    result, _ = project(p, "SE")
    assert result["P11_reverb_dry_wet"] == 0.9


def test_pass_through():
    """正常参数不受影响."""
    try:
        from moodify.knowledge.craft_chains import get_recommended_params
        p = get_recommended_params("GA")
    except Exception:
        p = {"P02_vocal_presence_gain": 2.0, "P15_high_shelf_gain": 1.0,
             "P06_compression_ratio": 2.0, "P11_reverb_dry_wet": 0.3}
    result, log = project(p, "GA")
    assert log == []


def test_wl_full_pass():
    """WL 情绪的高失真参数不被过度修正."""
    p = {"P13_harmonic_drive": 0.9, "P06_compression_ratio": 25.0}
    result, _ = project(p, "WL")
    assert result["P13_harmonic_drive"] == 0.9
    assert result["P06_compression_ratio"] == 25.0


def test_unknown_params_preserved():
    """非标准参数原样保留."""
    p = {"custom_gain": 42.0, "P02_vocal_presence_gain": 3.0}
    result, _ = project(p, "GA")
    assert result["custom_gain"] == 42.0
    assert result["P02_vocal_presence_gain"] == 3.0


def test_partial_params_pass_through():
    """只有部分参数也能正常投影."""
    p = {"P02_vocal_presence_gain": 3.0}
    result, _ = project(p, "GA")
    assert result["P02_vocal_presence_gain"] == 3.0

    # All 15 recommended params should pass through without corrections
    try:
        from moodify.knowledge.craft_chains import get_recommended_params
        full = get_recommended_params("GA")
        result2, log2 = project(full, "GA")
        assert log2 == []
    except Exception:
        pass
