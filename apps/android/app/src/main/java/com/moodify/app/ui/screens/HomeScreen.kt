package com.moodify.app.ui.screens

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.awaitEachGesture
import androidx.compose.foundation.gestures.awaitFirstDown
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.pager.VerticalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material.icons.rounded.Pause
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.data.CatalogueClient
import com.moodify.app.data.CatalogueTrack
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.PlaybackState
import com.moodify.app.data.QueueItem
import com.moodify.app.ui.components.MoodifyMark
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.withContext
import kotlin.math.min

private const val AUDIO_BASE = "https://rongjinwenchuan.xyz/audio/"
private val Night = Color(0xFF000106)
private val Ink = Color(0xFFF8F7FB)
private val Muted = Color(0xFF9798C4)
private val Purple = Color(0xFF8139FF)
private val Blue = Color(0xFF22BCFF)

@Composable
fun HomeScreen(
    favouritePaths: Set<String> = emptySet(),
    onFavourite: (QueueItem) -> Unit = {},
    onAddToPlaylist: (QueueItem) -> Unit = {},
) {
    var tracks by remember { mutableStateOf<List<CatalogueTrack>?>(null) }
    var loadFailed by remember { mutableStateOf(false) }
    val playback by PlaybackManager.state.collectAsState()
    val context = androidx.compose.ui.platform.LocalContext.current

    LaunchedEffect(Unit) {
        while (true) {
            PlaybackManager.tick()
            delay(500)
        }
    }
    LaunchedEffect(Unit) {
        CatalogueClient.cached(context)?.let { cached ->
            tracks = cached.tracks
            if (playback.queue.isEmpty()) PlaybackManager.loadQueue(cached.tracks.toQueue())
        }
        val result = withContext(Dispatchers.IO) { runCatching { CatalogueClient().playableCatalogue() } }
        result.onSuccess { catalogue ->
            tracks = catalogue.tracks
            CatalogueClient.cache(context, catalogue)
            val refreshedQueue = catalogue.tracks.toQueue()
            if (refreshedQueue.isNotEmpty() && PlaybackManager.state.value.queue != refreshedQueue) {
                val currentTitle = PlaybackManager.state.value.current?.title
                val refreshedIndex = refreshedQueue.indexOfFirst { it.title == currentTitle }.coerceAtLeast(0)
                PlaybackManager.playQueue(refreshedQueue, refreshedIndex, autoPlay = PlaybackManager.state.value.playWhenReady)
            }
        }.onFailure { if (tracks == null) loadFailed = true }
    }

    Box(Modifier.fillMaxSize().background(Night)) {
        when {
            tracks == null && !loadFailed -> LoadingSurface()
            loadFailed -> MessageSurface("暂时无法连接曲库")
            tracks.isNullOrEmpty() -> MessageSurface("曲库中还没有可播放作品")
            else -> PlayerPager(tracks.orEmpty(), playback, favouritePaths, onFavourite, onAddToPlaylist)
        }
    }
}

@Composable
private fun PlayerPager(
    tracks: List<CatalogueTrack>,
    playback: PlaybackState,
    favouritePaths: Set<String>,
    onFavourite: (QueueItem) -> Unit,
    onAddToPlaylist: (QueueItem) -> Unit,
) {
    val pagerState = rememberPagerState(
        initialPage = playback.queueIndex.coerceAtLeast(0).coerceAtMost(tracks.lastIndex),
        pageCount = { tracks.size },
    )

    LaunchedEffect(pagerState, tracks) {
        // React as soon as the pager commits to a target instead of waiting for
        // the visual page animation to settle. Media3 can then consume its
        // already-prepared next item while the UI finishes moving.
        snapshotFlow { pagerState.targetPage }
            .distinctUntilChanged()
            .collect { page ->
                if (PlaybackManager.state.value.queue.isEmpty()) PlaybackManager.loadQueue(tracks.toQueue(), page)
                else if (PlaybackManager.state.value.queueIndex != page) PlaybackManager.jumpTo(page)
            }
    }
    LaunchedEffect(playback.queueIndex) {
        val index = playback.queueIndex
        if (index in tracks.indices && index != pagerState.currentPage && !pagerState.isScrollInProgress) {
            pagerState.animateScrollToPage(index)
        }
    }

    VerticalPager(
        state = pagerState,
        modifier = Modifier.fillMaxSize().semantics {
            contentDescription = "上下滑动切换歌曲"
        },
        beyondViewportPageCount = 1,
        key = { tracks[it].id },
    ) { page ->
        PlayerPage(
            track = tracks[page],
            state = playback,
            active = page == playback.queueIndex,
            favourite = tracks[page].queueItem()?.path in favouritePaths,
            onFavourite = { tracks[page].queueItem()?.let(onFavourite) },
            onAddToPlaylist = { tracks[page].queueItem()?.let(onAddToPlaylist) },
        )
    }
}

@Composable
private fun PlayerPage(
    track: CatalogueTrack,
    state: PlaybackState,
    active: Boolean,
    favourite: Boolean,
    onFavourite: () -> Unit,
    onAddToPlaylist: () -> Unit,
) {
    val playing = active && state.playWhenReady
    val position = if (active) state.positionMs else 0L
    val duration = if (active && state.durationMs > 0) state.durationMs else track.durationMs ?: 0L
    val titleSize = titleFontSize(track.title)
    val glow = Brush.radialGradient(
        colors = listOf(Color(0x332D36CC), Color.Transparent),
        center = Offset(750f, 1250f),
        radius = 820f,
    )

    Box(Modifier.fillMaxSize().background(glow).padding(horizontal = 26.dp)) {
        Brand(Modifier.align(Alignment.TopStart).padding(top = 42.dp))

        Column(Modifier.fillMaxWidth().align(Alignment.TopStart).padding(top = 150.dp)) {
            Text(
                text = track.title,
                color = Ink,
                fontSize = titleSize.sp,
                lineHeight = (titleSize + 5).sp,
                fontFamily = FontFamily.Serif,
                maxLines = 4,
                overflow = TextOverflow.Clip,
            )
            Spacer(Modifier.height(28.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(14.dp), verticalAlignment = Alignment.CenterVertically) {
                PlayButton(playing) { PlaybackManager.toggle() }
                Box(
                    Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(Color(0x0FFFFFFF))
                        .clickable(onClick = onFavourite),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        if (favourite) Icons.Filled.Favorite else Icons.Outlined.FavoriteBorder,
                        contentDescription = if (favourite) "取消收藏" else "收藏",
                        tint = if (favourite) Color(0xFFFF4B66) else Muted,
                        modifier = Modifier.size(25.dp),
                    )
                }
                Box(
                    Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(Color(0x0FFFFFFF))
                        .clickable(onClick = onAddToPlaylist),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        Icons.Outlined.Add,
                        contentDescription = "加入歌单",
                        tint = Muted,
                        modifier = Modifier.size(27.dp),
                    )
                }
            }
        }

        VinylRecord(
            playing = playing,
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .offset(x = 78.dp, y = (-118).dp)
                .size(310.dp),
        )

        Progress(
            positionMs = position,
            durationMs = duration,
            enabled = active,
            modifier = Modifier.align(Alignment.BottomCenter).padding(bottom = 35.dp),
        )
    }
}

@Composable
private fun Brand(modifier: Modifier = Modifier) {
    Row(modifier, verticalAlignment = Alignment.CenterVertically) {
        MoodifyMark(Modifier.size(45.dp, 30.dp))
        Text(
            "Moodify",
            color = Ink,
            fontSize = 22.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.padding(start = 10.dp),
        )
    }
}

@Composable
private fun PlayButton(playing: Boolean, onClick: () -> Unit) {
    Box(
        Modifier
            .size(width = 92.dp, height = 54.dp)
            .clip(RoundedCornerShape(28.dp))
            .background(Brush.horizontalGradient(listOf(Purple, Blue)))
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(
            if (playing) Icons.Rounded.Pause else Icons.Rounded.PlayArrow,
            contentDescription = if (playing) "暂停" else "播放",
            tint = Color.White,
            modifier = Modifier.size(31.dp),
        )
    }
}

@Composable
private fun VinylRecord(playing: Boolean, modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "record rotation")
    val rotation by transition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(tween(12_000, easing = LinearEasing), RepeatMode.Restart),
        label = "rotation",
    )
    Box(modifier, contentAlignment = Alignment.Center) {
        Canvas(Modifier.fillMaxSize().rotate(if (playing) rotation else 0f)) {
            val r = min(size.width, size.height) / 2f
            val center = this.center
            drawCircle(Color(0x241E55FF), r, center)
            drawCircle(Color(0x66542DFF), r * .87f, center, style = Stroke(r * .035f))
            drawCircle(Color(0xFF05060C), r * .79f, center)
            for (i in 1..18) {
                drawCircle(
                    color = if (i % 4 == 0) Color(0x445B6491) else Color(0x33212636),
                    radius = r * (.18f + i * .032f),
                    center = center,
                    style = Stroke(1.1f),
                )
            }
            drawArc(
                brush = Brush.sweepGradient(listOf(Color.Transparent, Color(0x99AAB8F8), Color.Transparent)),
                startAngle = 8f,
                sweepAngle = 72f,
                useCenter = false,
                topLeft = Offset(r * .27f, r * .27f),
                size = Size(r * 1.46f, r * 1.46f),
                style = Stroke(r * .11f, cap = StrokeCap.Round),
            )
            drawCircle(Color(0xFF121329), r * .25f, center)
        }
        MoodifyMark(Modifier.size(70.dp, 47.dp).rotate(if (playing) rotation else 0f))
    }
}

@Composable
private fun Progress(positionMs: Long, durationMs: Long, enabled: Boolean, modifier: Modifier = Modifier) {
    val safeDuration = durationMs.coerceAtLeast(1L)
    val progress = (positionMs.toFloat() / safeDuration).coerceIn(0f, 1f)
    Column(modifier.fillMaxWidth()) {
        Canvas(
            Modifier
                .fillMaxWidth()
                .height(32.dp)
                .pointerInput(enabled, safeDuration) {
                    if (!enabled) return@pointerInput
                    awaitEachGesture {
                        val down = awaitFirstDown()
                        fun seek(x: Float) {
                            PlaybackManager.seekTo((safeDuration * (x / size.width).coerceIn(0f, 1f)).toLong())
                        }
                        seek(down.position.x)
                        var change = down
                        while (change.pressed) {
                            val event = awaitPointerEvent()
                            change = event.changes.first()
                            seek(change.position.x)
                            change.consume()
                        }
                    }
                }
        ) {
            val y = size.height / 2f
            val x = size.width * progress
            drawLine(Color(0xFF303442), Offset(0f, y), Offset(size.width, y), 3.dp.toPx(), StrokeCap.Round)
            drawLine(
                Brush.horizontalGradient(listOf(Purple, Blue)),
                Offset(0f, y), Offset(x, y), 3.dp.toPx(), StrokeCap.Round,
            )
            drawCircle(Blue, 6.dp.toPx(), Offset(x, y))
            drawCircle(Color.White.copy(alpha = .35f), 2.dp.toPx(), Offset(x, y))
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(formatTime(positionMs), color = Muted, fontSize = 14.sp)
            Text(formatTime(durationMs), color = Muted, fontSize = 14.sp)
        }
    }
}

@Composable
private fun LoadingSurface() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator(color = Purple)
    }
}

@Composable
private fun MessageSurface(message: String) {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Text(message, color = Muted, fontSize = 15.sp)
    }
}

private fun CatalogueTrack.queueItem(): QueueItem? = audioAssetKey?.let { key ->
    QueueItem(title = title, subtitle = "", path = AUDIO_BASE + key)
}

private fun List<CatalogueTrack>.toQueue(): List<QueueItem> = mapNotNull(CatalogueTrack::queueItem)

private fun formatTime(ms: Long): String {
    val totalSeconds = ms.coerceAtLeast(0L) / 1000
    return "%d:%02d".format(totalSeconds / 60, totalSeconds % 60)
}

private fun titleFontSize(title: String): Int = when {
    title.length <= 22 -> 44
    title.length <= 34 -> 38
    else -> 34
}
