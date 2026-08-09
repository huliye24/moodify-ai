package com.moodify.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.KeyboardArrowDown
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.Pause
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.SkipNext
import androidx.compose.material.icons.outlined.SkipPrevious
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
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
import com.moodify.app.data.QueueItem
import com.moodify.app.ui.theme.MoodifyBlue
import com.moodify.app.ui.theme.MoodifyMuted
import com.moodify.app.ui.theme.MoodifyNavy
import com.moodify.app.ui.theme.MoodifyOutline
import com.moodify.app.ui.theme.MoodifyPurple
import kotlinx.coroutines.delay

/** Full-screen Now Playing page with track info, seek, controls and queue. */
@Composable
fun NowPlayingScreen(onClose: () -> Unit) {
    val state by PlaybackManager.state.collectAsStateWithLifecycle()
    val current = state.current

    LaunchedEffect(state.url) {
        while (true) {
            PlaybackManager.tick()
            delay(500)
        }
    }

    Column(Modifier.fillMaxSize().background(Color(0xFFF7F8FC)).padding(horizontal = 22.dp)) {
        Spacer(Modifier.height(10.dp))
        IconButton(onClick = onClose, modifier = Modifier.align(Alignment.CenterHorizontally)) {
            Icon(Icons.Outlined.KeyboardArrowDown, stringResource(R.string.player_collapse), tint = MoodifyMuted, modifier = Modifier.size(32.dp))
        }
        Text(stringResource(R.string.player_now_playing), Modifier.fillMaxWidth(), color = MoodifyNavy, fontSize = 18.sp, fontWeight = FontWeight.Bold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
        Spacer(Modifier.height(28.dp))

        // Cover placeholder
        Box(
            Modifier
                .fillMaxWidth()
                .weight(1f)
                .background(
                    Brush.linearGradient(listOf(Color(0xFF7B61FF), Color(0xFF4A9BFF), Color(0xFF25258E))),
                    RoundedCornerShape(28.dp),
                ),
            contentAlignment = Alignment.Center,
        ) {
            Icon(Icons.Outlined.MusicNote, null, tint = Color.White.copy(alpha = 0.85f), modifier = Modifier.size(110.dp))
        }
        Spacer(Modifier.height(26.dp))

        // Track info
        Text(
            current?.title ?: "—",
            color = MoodifyNavy,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
        Spacer(Modifier.height(6.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(current?.preset ?: "Moodify", color = MoodifyMuted, fontSize = 13.sp)
            current?.mrsDelta?.let {
                Spacer(Modifier.width(10.dp))
                Surface(color = Color(0xFFE9F0FF), shape = RoundedCornerShape(8.dp)) {
                    Text("MRS Δ+%.1f".format(it), color = MoodifyBlue, fontSize = 11.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp))
                }
            }
            current?.let {
                Spacer(Modifier.width(8.dp))
                Surface(color = if (it.gatePassed) Color(0xFFE8F8EE) else Color(0xFFFFF2E8), shape = RoundedCornerShape(8.dp)) {
                    Text(if (it.gatePassed) stringResource(R.string.works_gate_passed) else stringResource(R.string.works_gate_failed), color = if (it.gatePassed) Color(0xFF31A35E) else Color(0xFFE08A3C), fontSize = 11.sp, modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp))
                }
            }
        }
        Spacer(Modifier.height(14.dp))

        // A/B switch (original/processed adjacent in queue)
        if (current != null) {
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                AbSwitch(stringResource(R.string.player_listen_before), current.isOriginal, Modifier.weight(1f)) {
                    if (!current.isOriginal) PlaybackManager.previous()
                }
                AbSwitch(stringResource(R.string.work_detail_after), !current.isOriginal, Modifier.weight(1f)) {
                    if (current.isOriginal) PlaybackManager.next()
                }
            }
            Spacer(Modifier.height(18.dp))
        }

        // Seek bar
        Slider(
            value = if (state.durationMs > 0) state.positionMs.toFloat().coerceIn(0f, state.durationMs.toFloat()) else 0f,
            onValueChange = { PlaybackManager.seekTo(it.toLong()) },
            valueRange = 0f..state.durationMs.toFloat().coerceAtLeast(1f),
            colors = SliderDefaults.colors(
                thumbColor = MoodifyPurple,
                activeTrackColor = MoodifyPurple,
                inactiveTrackColor = MoodifyOutline,
            ),
        )
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(fmtTime(state.positionMs), color = MoodifyMuted, fontSize = 11.sp)
            Text(fmtTime(state.durationMs), color = MoodifyMuted, fontSize = 11.sp)
        }
        Spacer(Modifier.height(8.dp))

        // Controls
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = { PlaybackManager.previous() }, modifier = Modifier.size(52.dp)) {
                Icon(Icons.Outlined.SkipPrevious, null, tint = MoodifyNavy, modifier = Modifier.size(34.dp))
            }
            Spacer(Modifier.width(30.dp))
            FilledIconButton(
                onClick = { PlaybackManager.toggle() },
                modifier = Modifier.size(72.dp),
                colors = IconButtonDefaults.filledIconButtonColors(containerColor = MoodifyPurple),
            ) {
                Icon(if (state.playing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, if (state.playing) stringResource(R.string.player_pause) else stringResource(R.string.player_play), tint = Color.White, modifier = Modifier.size(36.dp))
            }
            Spacer(Modifier.width(30.dp))
            IconButton(onClick = { PlaybackManager.next() }, modifier = Modifier.size(52.dp)) {
                Icon(Icons.Outlined.SkipNext, null, tint = MoodifyNavy, modifier = Modifier.size(34.dp))
            }
        }
        Spacer(Modifier.height(18.dp))

        // Queue list
        Text(stringResource(R.string.player_queue), color = MoodifyNavy, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(6.dp))
        if (state.queue.isEmpty()) {
            Text(stringResource(R.string.player_queue_empty), color = MoodifyMuted, fontSize = 12.sp)
        } else {
            Column(Modifier.weight(0.45f)) {
                state.queue.forEachIndexed { index, item ->
                    val active = index == state.queueIndex
                    Row(
                        Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(12.dp))
                            .background(if (active) Color(0xFFF0EDFF) else Color.Transparent)
                            .clickable { if (!active) PlaybackManager.jumpTo(index) }
                            .padding(horizontal = 12.dp, vertical = 9.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(Icons.Outlined.MusicNote, null, tint = if (active) MoodifyPurple else MoodifyMuted, modifier = Modifier.size(16.dp))
                        Column(Modifier.weight(1f).padding(start = 10.dp)) {
                            Text(item.title, color = if (active) MoodifyPurple else MoodifyNavy, fontSize = 13.sp, fontWeight = if (active) FontWeight.SemiBold else FontWeight.Normal, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            Text(if (item.isOriginal) stringResource(R.string.work_detail_before) else item.preset, color = MoodifyMuted, fontSize = 10.sp)
                        }
                        if (active) {
                            Icon(if (state.playing) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, null, tint = MoodifyPurple, modifier = Modifier.size(18.dp))
                        }
                    }
                }
            }
        }
        Spacer(Modifier.height(16.dp))
    }
}

@Composable
private fun AbSwitch(label: String, selected: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Surface(
        onClick = onClick,
        shape = RoundedCornerShape(14.dp),
        color = if (selected) MoodifyPurple else Color.White,
        border = androidx.compose.foundation.BorderStroke(1.dp, if (selected) MoodifyPurple else MoodifyOutline),
        modifier = modifier,
    ) {
        Text(label, Modifier.fillMaxWidth().padding(vertical = 10.dp), color = if (selected) Color.White else MoodifyNavy, fontSize = 13.sp, fontWeight = FontWeight.SemiBold, textAlign = androidx.compose.ui.text.style.TextAlign.Center)
    }
}

private fun fmtTime(ms: Long): String {
    val totalSec = ms / 1000
    return "%d:%02d".format(totalSec / 60, totalSec % 60)
}
