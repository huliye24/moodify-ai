"""Identity Guard policy and versioned budgets (MFY-CR-P05).

Budgets are PROVISIONAL in v0.1 (synthetic perturbation + candidate set basis,
per 01_TASK.md §11). Every budget records its source class:
PROVISIONAL / CALIBRATED / EXPERIMENTAL.
"""

from __future__ import annotations

IDENTITY_GUARD_POLICY_V1 = {
    "version": "identity-guard-policy-v1",
    "schema_version": "1.0",
    "budget_class": "PROVISIONAL",
    "dimensions": {
        "IG-01": {
            "capability": "PROXY",
            "budgets": {
                # mid/vocal-band proxies: drift beyond these needs human ears
                "mid_energy_ratio_abs": {"value": 0.05, "class": "PROVISIONAL"},
                "presence_2000_5000_hz_abs": {"value": 0.03, "class": "PROVISIONAL"},
                "core_mid_500_2000_hz_abs": {"value": 0.05, "class": "PROVISIONAL"},
                "spectral_centroid_hz_abs": {"value": 300.0, "class": "PROVISIONAL"},
            },
            "state_on_drift": "HUMAN_REQUIRED",
        },
        "IG-02": {
            "capability": "MEASURABLE",
            "budgets": {
                # dynamic flattening (negative deltas)
                "loudness_range_lu": {"value": -4.0, "class": "PROVISIONAL"},
                "crest_factor_db": {"value": -3.0, "class": "PROVISIONAL"},
                "plr_db": {"value": -3.0, "class": "PROVISIONAL"},
            },
            "caution_factor": 0.6,
            "reject_any": True,  # beyond budget on any dynamic metric -> REJECT
        },
        "IG-03": {
            "capability": "NOT_MEASURABLE",
            "budgets": {},
            "state": "NOT_MEASURABLE",
            "critical_unmeasured": True,
        },
        "IG-04": {
            "capability": "MEASURABLE",
            "budgets": {
                # artificial widening (positive deltas)
                "stereo_width_proxy": {"value": 0.25, "class": "PROVISIONAL"},
                "side_to_mid_db": {"value": 4.0, "class": "PROVISIONAL"},
            },
            "mono_guard": {
                # mono/narrow source becoming wide is never a default improvement
                "source_correlation_min": 0.999,
                "candidate_correlation_max": 0.95,
            },
        },
        "IG-05": {
            "capability": "MEASURABLE",
            "budgets": {
                # modern bass inflation (positive deltas)
                "sub_20_60_hz": {"value": 0.03, "class": "PROVISIONAL"},
                "bass_60_120_hz": {"value": 0.04, "class": "PROVISIONAL"},
            },
        },
        "IG-06": {
            "capability": "MEASURABLE",
            "budgets": {
                # loudness war behaviour (absolute LUFS delta)
                "integrated_lufs": {"value": 3.0, "class": "PROVISIONAL"},
                "caution_lufs": {"value": 1.5, "class": "PROVISIONAL"},
            },
            "clipping_guard": {
                # new clipping in candidate is a hard reject
                "new_clipping_min_ratio": 0.00005,
            },
        },
    },
}
