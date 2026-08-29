"""MFY-DATA-FACTORY-001 shared fixtures.

The full machine loop is run once per module so the scan-heavy integration
tests stay bounded in CI. No copyrighted material; the fixture is synthetic.
"""

from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf

from moodify.data_factory.runner import run_production_case

CASE_ID = "case_" + "f" * 32


@pytest.fixture(scope="module")
def completed_case_dir(tmp_path_factory):
    """One real machine loop: run_production_case with algorithmic review."""
    root = tmp_path_factory.mktemp("data_factory")
    sr = 48000
    t = np.arange(sr * 2) / sr
    x = (
        0.25 * np.sin(2 * np.pi * 80 * t)
        + 0.20 * np.sin(2 * np.pi * 440 * t)
        + 0.10 * np.sin(2 * np.pi * 3000 * t)
        + 0.03 * np.sin(2 * np.pi * 12000 * t)
    )
    x = (x * 0.5).astype(np.float32)
    x = np.stack([x, x * 0.9], axis=1)
    source = root / "fixture.wav"
    sf.write(source, x, sr)

    return run_production_case(source, root / "out", case_id=CASE_ID)
