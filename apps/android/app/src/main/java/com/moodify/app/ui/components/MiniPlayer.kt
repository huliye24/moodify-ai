package com.moodify.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.moodify.app.data.PlaybackManager
import kotlinx.coroutines.delay

/**
 * Global mini player pinned above the bottom navigation bar.
 * Visible while a track is loaded; tap opens the full Now Playing page.
 */
@Composable
fun MiniPlayer(onOpen: () -> Unit, modifier: Modifier = Modifier) {
    val state by PlaybackManager.state.collectAsStateWithLifecycle()
    val current = state.current ?: return

    LaunchedEffect(state.url) {
        while (true) {
            PlaybackManager.tick()
            delay(500)
        }
    }

    Surface(
        modifier = modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 6.dp),
        shape = RoundedCornerShape(18.dp),
        color = Color.Transparent,
        shadowElevation = 0.dp,
    ) {
        Box(
            Modifier
                .fillMaxWidth()
                .clickable(onClick = onOpen)
                .background(Brush.linearGradient(listOf(Color(0xFF7B61FF), Color(0xFF4A9BFF))), RoundedCornerShape(18.dp))
                .padding(horizontal = 12.dp, vertical = 8.dp),
        ) {
            Column {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        Modifier.size(40.dp).background(Color.White.copy(0.18f), RoundedCornerShape(11.dp)),
                        contentAlignment = Alignment.Center,
                    ) {
                        Icon(Icons.Outlined.MusicNote, null, tint = Color.White, modifier = Modifier.size(22.dp))
                    }
                    Column(Modifier.weight(1f).padding(start = 10.dp)) {
                        Text(
                            current.title,
                            color = Color.White,
                            fontSize = 13.sp,
                            fontWeight = FontWeight.SemiBold,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                        Text(
                            current.subtitle.ifEmpty { current.preset },
                            color = Color.White.copy(alpha = 0.75f),
                            fontSize = 10.sp,
                            maxLines = 1,
                            overflow = TextOverflow.Ellipsis,
                        )
                    }
                    IconButton(onClick = { PlaybackManager.toggle() }) {
                        Icon(
                            if (state.playing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow,
                            contentDescription = if (state.playing) "暂停" else "播放",
                            tint = Color.White,
                            modifier = Modifier.size(26.dp),
                        )
                    }
                }
                if (state.durationMs > 0) {
                    LinearProgressIndicator(
                        progress = { if (state.durationMs > 0) state.positionMs.toFloat() / state.durationMs else 0f },
                        modifier = Modifier.fillMaxWidth().padding(top = 4.dp).height(3.dp),
                        color = Color.White,
                        trackColor = Color.White.copy(alpha = 0.25f),
                    )
                }
            }
        }
    }
}
