from moodify.lyric_align.config import AlignConfig, DEFAULT_CONFIG_PATH, QualityGate


def test_default_config_matches_spec_thresholds() -> None:
    config = AlignConfig()
    assert config.publish_gate.min_coverage == 0.92
    assert config.publish_gate.max_unaligned_token_ratio == 0.05
    assert config.publish_gate.min_mean_word_confidence == 0.72
    assert config.publish_gate.min_line_confidence == 0.55
    assert config.publish_gate.max_line_overlap_seconds == 0.08
    assert config.publish_gate.max_rerun_delta_ms == 80.0
    assert config.sample_rate == 16000


def test_config_from_file_matches_shipped_defaults() -> None:
    config = AlignConfig.from_file(DEFAULT_CONFIG_PATH)
    assert config.sample_rate == 16000
    assert config.separate_vocals == "auto"
    assert config.demucs_model == "htdemucs"
    assert config.publish_gate.min_coverage == 0.92


def test_config_override_persists() -> None:
    gate = QualityGate(min_coverage=0.95, max_rerun_delta_ms=120.0)
    assert gate.min_coverage == 0.95
    assert gate.max_rerun_delta_ms == 120.0
