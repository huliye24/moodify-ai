package com.moodify.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.moodify.app.R
import com.moodify.app.data.PlaybackManager
import com.moodify.app.ui.theme.MoodifyBlue
import com.moodify.app.ui.theme.MoodifyMuted
import com.moodify.app.ui.theme.MoodifyNavy
import kotlinx.coroutines.delay

/** Bottom playback bar shown while a track is loaded. */
@Composable
fun PlaybackBar(modifier: Modifier = Modifier) {
    val state by PlaybackManager.state.collectAsStateWithLifecycle()
    if (state.url == null) return

    LaunchedEffect(state.url) {
        while (true) {
            PlaybackManager.tick()
            delay(500)
        }
    }

    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = Color.Transparent,
        shadowElevation = 0.dp,
    ) {
        Row(
            Modifier
                .fillMaxWidth()
                .background(Brush.linearGradient(listOf(Color(0xFF7B61FF), Color(0xFF4A9BFF))), RoundedCornerShape(20.dp))
                .padding(horizontal = 14.dp, vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(onClick = { PlaybackManager.toggle() }) {
                Icon(
                    if (state.playing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow,
                    contentDescription = if (state.playing) stringResource(R.string.player_pause) else stringResource(R.string.player_play),
                    tint = Color.White,
                    modifier = Modifier.size(30.dp),
                )
            }
            Column(Modifier.weight(1f)) {
                Text(
                    state.title,
                    color = Color.White,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
                Spacer(Modifier.height(4.dp))
                if (state.durationMs > 0) {
                    Slider(
                        value = state.positionMs.toFloat().coerceIn(0f, state.durationMs.toFloat()),
                        onValueChange = { PlaybackManager.seekTo(it.toLong()) },
                        valueRange = 0f..state.durationMs.toFloat().coerceAtLeast(1f),
                        modifier = Modifier.fillMaxWidth().height(24.dp),
                        colors = SliderDefaults.colors(
                            thumbColor = Color.White,
                            activeTrackColor = Color.White,
                            inactiveTrackColor = Color.White.copy(alpha = 0.35f),
                        ),
                    )
                } else {
                    LinearProgressIndicator(
                        modifier = Modifier.fillMaxWidth().height(3.dp),
                        color = Color.White,
                        trackColor = Color.White.copy(alpha = 0.3f),
                    )
                }
            }
            Text(
                "${(state.positionMs / 1000) / 60}:${(state.positionMs / 1000) % 60}".let { mmss ->
                    val m = mmss.substringBefore(':').padStart(2, '0')
                    val s = mmss.substringAfter(':').padStart(2, '0')
                    "$m:$s"
                },
                color = Color.White.copy(alpha = 0.85f),
                fontSize = 11.sp,
            )
        }
    }
}
