package com.moodify.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

val MoodifyGradient = Brush.horizontalGradient(listOf(MoodifyBlue, MoodifyGreen))

private val MoodifyLightColors = lightColorScheme(
    primary = MoodifyBlue,
    secondary = MoodifyPurple,
    tertiary = Evidence,
    background = MoodifyBackground,
    surface = MoodifySurface,
    onPrimary = Color.White,
    onBackground = MoodifyNavy,
    onSurface = MoodifyNavy,
    outline = MoodifyOutline,
    surfaceVariant = MoodifyLavender,
    onSurfaceVariant = MoodifyMuted,
    error = Blocking,
)

// Instrument palette is the canonical dark-first field (design_tokens_v1 §1.1).
private val MoodifyDarkColors = darkColorScheme(
    primary = Evidence,
    secondary = MoodifyPurple,
    tertiary = Evidence,
    background = MoodifyInstrumentField,
    surface = MoodifyInstrumentSurface,
    onPrimary = Color(0xFF05081E),
    onBackground = MoodifyInstrumentText,
    onSurface = MoodifyInstrumentText,
    outline = MoodifyInstrumentOutline,
    surfaceVariant = MoodifyInstrumentRaised,
    onSurfaceVariant = MoodifyInstrumentMuted,
    error = Blocking,
)

@Composable
fun MoodifyTheme(darkTheme: Boolean = true, content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (darkTheme) MoodifyDarkColors else MoodifyLightColors,
        typography = MoodifyTypography,
        content = content,
    )
}

