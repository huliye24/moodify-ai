package com.moodify.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color

val MoodifyGradient = Brush.horizontalGradient(listOf(MoodifyBlue, MoodifyGreen))

private val MoodifyColors = lightColorScheme(
    primary = MoodifyBlue,
    secondary = MoodifyPurple,
    tertiary = MoodifyGreen,
    background = MoodifyBackground,
    surface = MoodifySurface,
    onPrimary = Color.White,
    onBackground = MoodifyNavy,
    onSurface = MoodifyNavy,
    outline = MoodifyOutline,
    surfaceVariant = MoodifyLavender,
    onSurfaceVariant = MoodifyMuted,
    error = MoodifyCritical,
)

@Composable
fun MoodifyTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = MoodifyColors,
        typography = MoodifyTypography,
        content = content,
    )
}

