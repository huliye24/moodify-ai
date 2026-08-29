"""v01_diagnostics.py — Generate a human-readable diagnosis from AudioMetrics."""

from moodify.v01_types import AudioMetrics, DiagnosisReport


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
