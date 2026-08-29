from pathlib import Path

import numpy as np
import soundfile as sf

from moodify.data_factory.intervention import execute_intervention
from moodify.data_factory.models import InterventionPlan, PLAN_GENERATOR_VERSION


def test_intervention_writes_valid_wav(tmp_path: Path):
    sr = 48000
    t = np.arange(sr, dtype=np.float32) / sr
    audio = 0.1 * np.sin(2 * np.pi * 440 * t)
    source = tmp_path / "source.wav"
    sf.write(source, audio, sr)

    plan = InterventionPlan(
        case_id="case_" + "a" * 32,
        plan_id="plan-A",
        candidate_label="A",
        candidate_id="candidate-A",
        strategy="CONSERVATIVE",
        intensity=0.65,
        source_sha256="b" * 64,
        scan_profile_id="profile",
        scan_profile_hash="c" * 64,
        plan_generator_version=PLAN_GENERATOR_VERSION,
        params={
            "P06_compression_ratio": 1.05,
            "P07_compression_attack": 35.0,
            "P08_compression_release": 250.0,
            "P09_compression_threshold": -10.0,
        },
    )
    output = tmp_path / "candidate_A.wav"
    result = execute_intervention(source, output, plan)
    data, out_sr = sf.read(output)
    assert output.is_file()
    assert out_sr == sr
    assert len(data) == sr
    assert len(result.output_sha256) == 64
