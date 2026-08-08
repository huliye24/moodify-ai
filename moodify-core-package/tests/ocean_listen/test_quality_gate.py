from moodify.adapters.auditory.ocean_listen.quality_gate import evaluate_report


def test_valid_report_warns_only_for_semantics():
    report = {
        "name": "x",
        "duration": 2.0,
        "notes": [{"pitch": 60, "velocity": 80}],
        "total_notes": 1,
    }
    result = evaluate_report(report)
    assert result.verdict == "PASS"
    assert any(issue.code == "OCEAN_VELOCITY_SEMANTICS" for issue in result.issues)


def test_deep_missing_fails():
    result = evaluate_report({"name": "x", "duration": 2.0}, deep_expected=True)
    assert result.verdict == "FAIL"
    assert any(issue.code == "OCEAN_DEEP_OUTPUT_MISSING" for issue in result.issues)


def test_non_finite_fails():
    result = evaluate_report({"name": "x", "duration": 2.0, "bpm": float("nan")})
    assert result.verdict == "FAIL"


def test_low_classification_confidence_warns():
    report = {
        "name": "x",
        "duration": 2.0,
        "classification": {"confidence": 0.3},
    }
    result = evaluate_report(report)
    assert result.verdict == "WARN"
    assert any(issue.code == "OCEAN_LOW_CLASSIFICATION_CONFIDENCE" for issue in result.issues)


def test_missing_duration_fails():
    result = evaluate_report({"name": "x"})
    assert result.verdict == "FAIL"
    assert any(issue.code == "OCEAN_REQUIRED_DURATION" for issue in result.issues)


def test_note_count_mismatch_warns():
    report = {"name": "x", "duration": 2.0, "notes": [{"pitch": 60}], "total_notes": 5}
    result = evaluate_report(report)
    assert result.verdict == "WARN"
    assert any(issue.code == "OCEAN_NOTE_COUNT_MISMATCH" for issue in result.issues)


def test_experimental_labels_warn_only():
    report = {
        "name": "x",
        "duration": 2.0,
        "voiceTexture": "breathy",
        "voiceTimbre": "dark",
    }
    result = evaluate_report(report)
    assert result.verdict == "PASS"
    assert any(issue.code == "OCEAN_EXPERIMENTAL_LABELS" for issue in result.issues)
