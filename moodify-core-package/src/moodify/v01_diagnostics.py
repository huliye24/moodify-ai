"""v01_diagnostics.py — Generate a human-readable diagnosis from AudioMetrics."""

from moodify.v01_types import AudioMetrics, DiagnosisReport, ProblemEntry, ProblemVector


def diagnose(metrics: AudioMetrics) -> DiagnosisReport:
    """Generate a diagnosis report from audio metrics.

    Rules are deliberately simple for v0.1.0 — no ML, no RAG, no calibration.
    """
    issues: list[str] = []
    strengths: list[str] = []

    # ── Spectrum checks ──────────────────────────────
    if metrics.rms_sub > -6:
        issues.append("Sub-bass is very prominent — may overwhelm smaller speakers.")
    elif metrics.rms_sub < -30:
        issues.append("Sub-bass is very weak — track may lack physical weight.")

    if metrics.rms_bass > -3:
        issues.append("Bass is very forward — mid-range clarity may suffer.")
    elif metrics.rms_bass < -18:
        issues.append("Bass is very recessed — track may sound thin.")

    if metrics.rms_presence > -6:
        issues.append("Presence band is very forward — may cause listening fatigue.")
    elif metrics.rms_presence < -18:
        issues.append("Presence band is weak — vocals may lack clarity.")

    if metrics.rms_air > -15:
        strengths.append("Good air band energy — track has openness and sparkle.")
    elif metrics.rms_air < -30:
        issues.append("Air band is very weak — track may sound closed-in.")

    # ── Dynamics checks ──────────────────────────────
    if metrics.crest_factor < 2.0:
        issues.append("Very low crest factor — track may be over-compressed (loudness war).")
    elif metrics.crest_factor > 8.0:
        issues.append("Very high crest factor — peaks may clip while body is too quiet.")

    if metrics.dynamic_range_db < 3:
        issues.append("Dynamic range is very narrow — track may feel flat throughout.")
    elif metrics.dynamic_range_db > 20:
        strengths.append("Wide dynamic range — track has natural loudness variation.")

    if 3.0 <= metrics.crest_factor <= 7.0:
        strengths.append("Healthy crest factor — good balance of impact and body.")

    # ── Stereo checks ────────────────────────────────
    if metrics.correlation_lr < 0.2:
        issues.append("Very wide stereo image — check mono compatibility.")
    elif metrics.correlation_lr > 0.95 and metrics.channels == 2:
        issues.append("Almost mono stereo field — consider adding width.")

    if 0.3 <= metrics.correlation_lr <= 0.85:
        strengths.append("Well-balanced stereo image.")

    # ── Overall health ───────────────────────────────
    if len(issues) <= 1:
        overall = "good"
    elif len(issues) <= 3:
        overall = "fair"
    else:
        overall = "poor"

    # ── Suggested presets ────────────────────────────
    suggested = []
    if metrics.rms_presence < -15 or metrics.rms_bass < -15:
        suggested.append("warm_vocal")
    if metrics.crest_factor < 3.0 or metrics.dynamic_range_db < 5:
        suggested.append("clean_master")
    if metrics.correlation_lr > 0.9:
        suggested.append("wide_space")
    if not suggested:
        suggested.append("clean_master")   # safe default

    return DiagnosisReport(
        metrics=metrics,
        overall_health=overall,
        issues=issues,
        strengths=strengths,
        suggested_presets=suggested,
    )


# ═══════════════════════════════════════════════════════════════════════════
# MAP v0.2 Problem Vector (MHP-853 / MHP-866)
# ═══════════════════════════════════════════════════════════════════════════

# Per-category threshold distances for confidence computation
_CONFIDENCE_MARGINS = {
    "spectral": 3.0,   # dB margin for spectral thresholds
    "dynamics": 1.5,   # crest factor margin
    "stereo": 0.15,    # correlation margin
    "overall": 1.0,    # count margin
}

# Problem taxonomy: (problem_id, category, threshold_check, description_template)
_TAXONOMY: list[tuple[str, str, str, str, float]] = [
    # -- Spectral (7 problems) --
    ("sub_overpower",  "spectral", "sub_bass > -6",   "Sub-bass is very prominent — may overwhelm smaller speakers.", 1.0),
    ("sub_weak",       "spectral", "sub_bass < -30",  "Sub-bass is very weak — track may lack physical weight.", 0.8),
    ("bass_forward",   "spectral", "bass > -3",       "Bass is very forward — mid-range clarity may suffer.", 1.0),
    ("bass_recessed",  "spectral", "bass < -18",      "Bass is very recessed — track may sound thin.", 0.8),
    ("presence_harsh", "spectral", "presence > -6",   "Presence band is very forward — may cause listening fatigue.", 1.0),
    ("presence_weak",  "spectral", "presence < -18",  "Presence band is weak — vocals may lack clarity.", 0.8),
    ("air_weak",       "spectral", "air < -30",       "Air band is very weak — track may sound closed-in.", 0.5),

    # -- Dynamics (3 problems) --
    ("over_compressed", "dynamics", "crest_factor < 2.0",       "Very low crest factor — track may be over-compressed.", 1.0),
    ("peak_too_hot",    "dynamics", "crest_factor > 8.0",       "Very high crest factor — peaks may clip while body is too quiet.", 0.8),
    ("flat_dynamics",   "dynamics", "dynamic_range_db < 3",     "Dynamic range is very narrow — track may feel flat throughout.", 1.0),

    # -- Stereo (2 problems) --
    ("ultra_wide", "stereo", "correlation_lr < 0.2",  "Very wide stereo image — check mono compatibility.", 0.7),
    ("near_mono",  "stereo", "correlation_lr > 0.95", "Almost mono stereo field — consider adding width.", 0.5),
]


def _problem_confidence(observed: float, threshold: float, margin: float,
                         direction: str = "above") -> float:
    """Compute confidence [0,1] from distance to threshold."""
    if direction == "above":
        dist = observed - threshold
    else:
        dist = threshold - observed
    if dist <= 0:
        return 0.0
    return round(min(1.0, dist / max(margin, 0.001)), 3)


def to_problem_vector(report: DiagnosisReport) -> "ProblemVector":
    """Convert a human-readable DiagnosisReport to a structured ProblemVector.

    MHP-853 / MHP-866: Maps 13 problem IDs across 4 categories.
    Confidence is computed from threshold distance.
    """
    m = report.metrics
    entries: list[ProblemEntry] = []

    # -- Spectral checks --
    entries.append(ProblemEntry(
        problem_id="sub_overpower", category="spectral", severity="medium",
        confidence=_problem_confidence(m.rms_sub, -6, _CONFIDENCE_MARGINS["spectral"], "above"),
        weight=1.0,
        description="Sub-bass is very prominent — may overwhelm smaller speakers.",
    ))
    entries.append(ProblemEntry(
        problem_id="sub_weak", category="spectral", severity="medium",
        confidence=_problem_confidence(m.rms_sub, -30, _CONFIDENCE_MARGINS["spectral"], "below"),
        weight=0.8,
        description="Sub-bass is very weak — track may lack physical weight.",
    ))
    entries.append(ProblemEntry(
        problem_id="bass_forward", category="spectral", severity="medium",
        confidence=_problem_confidence(m.rms_bass, -3, _CONFIDENCE_MARGINS["spectral"], "above"),
        weight=1.0,
        description="Bass is very forward — mid-range clarity may suffer.",
    ))
    entries.append(ProblemEntry(
        problem_id="bass_recessed", category="spectral", severity="medium",
        confidence=_problem_confidence(m.rms_bass, -18, _CONFIDENCE_MARGINS["spectral"], "below"),
        weight=0.8,
        description="Bass is very recessed — track may sound thin.",
    ))
    entries.append(ProblemEntry(
        problem_id="presence_harsh", category="spectral", severity="high",
        confidence=_problem_confidence(m.rms_presence, -6, _CONFIDENCE_MARGINS["spectral"], "above"),
        weight=1.0,
        description="Presence band is very forward — may cause listening fatigue.",
    ))
    entries.append(ProblemEntry(
        problem_id="presence_weak", category="spectral", severity="medium",
        confidence=_problem_confidence(m.rms_presence, -18, _CONFIDENCE_MARGINS["spectral"], "below"),
        weight=0.8,
        description="Presence band is weak — vocals may lack clarity.",
    ))
    entries.append(ProblemEntry(
        problem_id="air_weak", category="spectral", severity="low",
        confidence=_problem_confidence(m.rms_air, -30, _CONFIDENCE_MARGINS["spectral"], "below"),
        weight=0.5,
        description="Air band is very weak — track may sound closed-in.",
    ))

    # -- Dynamics checks --
    entries.append(ProblemEntry(
        problem_id="over_compressed", category="dynamics", severity="high",
        confidence=_problem_confidence(m.crest_factor, 2.0, _CONFIDENCE_MARGINS["dynamics"], "below"),
        weight=1.0,
        description="Very low crest factor — track may be over-compressed (loudness war).",
    ))
    entries.append(ProblemEntry(
        problem_id="peak_too_hot", category="dynamics", severity="medium",
        confidence=_problem_confidence(m.crest_factor, 8.0, _CONFIDENCE_MARGINS["dynamics"], "above"),
        weight=0.8,
        description="Very high crest factor — peaks may clip while body is too quiet.",
    ))
    entries.append(ProblemEntry(
        problem_id="flat_dynamics", category="dynamics", severity="high",
        confidence=_problem_confidence(m.dynamic_range_db, 3.0, _CONFIDENCE_MARGINS["dynamics"], "below"),
        weight=1.0,
        description="Dynamic range is very narrow — track may feel flat throughout.",
    ))

    # -- Stereo checks --
    if m.channels == 2:
        entries.append(ProblemEntry(
            problem_id="ultra_wide", category="stereo", severity="medium",
            confidence=_problem_confidence(m.correlation_lr, 0.2, _CONFIDENCE_MARGINS["stereo"], "below"),
            weight=0.7,
            description="Very wide stereo image — check mono compatibility.",
        ))
        entries.append(ProblemEntry(
            problem_id="near_mono", category="stereo", severity="low",
            confidence=_problem_confidence(m.correlation_lr, 0.95, _CONFIDENCE_MARGINS["stereo"], "above"),
            weight=0.5,
            description="Almost mono stereo field — consider adding width.",
        ))

    # -- Diagnosis loss --
    active = [e for e in entries if e.confidence > 0.1]
    diagnosis_loss = round(min(1.0, sum(e.weight * e.confidence for e in active) / 10.0), 3)

    return ProblemVector(problems=active, diagnosis_loss=diagnosis_loss)
