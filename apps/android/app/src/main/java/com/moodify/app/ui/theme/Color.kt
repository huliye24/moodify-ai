package com.moodify.app.ui.theme

import androidx.compose.ui.graphics.Color

// Canonical semantic tokens — single source per docs/design/design_tokens_v1.md
// (MFY_SHARED_DESIGN_SYSTEM_AND_SHELL_001). One value per meaning: evidence
// green for progress/verified, amber for human attention only, red for
// blocking failure only. New colors must be registered in the spec first.
val Evidence = Color(0xFF7FB8A8)
val HumanAttention = Color(0xFFD9A466)
val Blocking = Color(0xFFC87070)
val FocusRing = Color(0xFF6A55FF)

val MoodifyBlue = Color(0xFF4A9BFF)
val MoodifyPurple = Color(0xFF7B61FF)
val MoodifyNavy = Color(0xFF111D3A)
val MoodifyLavender = Color(0xFFEDE8FF)
val MoodifyBackground = Color(0xFFFAFBFF)
val MoodifySurface = Color(0xFFFFFFFF)
val MoodifyMuted = Color(0xFF788198)
val MoodifyOutline = Color(0xFFE7EAF2)

// Canonical auditory-instrument palette (dark-first field). Legacy surfaces
// retain the aliases above until each screen is migrated as a complete,
// readable composition; legacy alias values are unified to the canonical
// tokens so no drifting value sets survive.
val MoodifyInstrumentField = Color(0xFF0B0D0C)
val MoodifyInstrumentSurface = Color(0xFF121513)
val MoodifyInstrumentRaised = Color(0xFF181C19)
val MoodifyInstrumentText = Color(0xFFF0F1EC)
val MoodifyInstrumentMuted = Color(0xFF8D958F)
val MoodifyInstrumentOutline = Color(0xFF2B302C)
val MoodifyInstrumentSignal = Evidence

// Deprecated legacy aliases — migrate screens to canonical names.
val MoodifyGreen = Evidence
val MoodifyOrange = HumanAttention
val MoodifyCritical = Blocking
