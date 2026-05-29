"""校准实验模块 — AI 听者 + 代理指标验证。

用法:
  from moodify.calibration.experiment import run_calibration
  from moodify.calibration.listener import DiagnosisListener

  listener = DiagnosisListener()
  report = run_calibration(["song1.wav", "song2.wav"], ["GA", "DR"],
                           listener=listener)
  print(f"Aggregate ρ: {report.aggregate_spearman_rho}")
"""

from moodify.calibration.listener import AudioListener, DiagnosisListener
from moodify.calibration.experiment import (
    run_calibration,
    CalibrationReport,
    SongCalibration,
    VersionResult,
)
from moodify.calibration.online import (
    CalibrationState,
    update_calibration,
    correct_proxy_score,
    get_state,
)
