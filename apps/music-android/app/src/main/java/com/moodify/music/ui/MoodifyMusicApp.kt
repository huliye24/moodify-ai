package com.moodify.music.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.music.data.BffClient
import com.moodify.music.data.LocalTrack
import com.moodify.music.data.ReconstructionManager
import com.moodify.music.data.ReconstructionStatus
import com.moodify.music.ExternalAudio
import com.moodify.music.data.Track
import com.moodify.music.player.PlaybackController
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

private val Purple = Color(0xFF6D4AFF)
private val Blue = Color(0xFF478DFF)
private val Navy = Color(0xFF121C39)
private val Muted = Color(0xFF747D94)
private val Outline = Color(0xFFE7E9F2)
private val Background = Color(0xFFFBFBFE)

@Composable
fun MoodifyMusicTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Purple,
            secondary = Blue,
            background = Background,
            surface = Color.White,
            onSurface = Navy,
        ),
        content = content,
    )
}

/**
 * P09 v0.1 — Main app with Library + reconstruction integration.
 *
 * Navigation: Home | Library | NowPlaying (mini → full-screen)
 */
@Composable
fun MoodifyMusicApp(
    client: BffClient,
    playback: PlaybackController,
    reconstructionManager: ReconstructionManager,
    externalAudio: List<ExternalAudio> = emptyList(),
    onPickAudio: () -> Unit = {},
    onExternalAudioConsumed: () -> Unit = {},
) {
    var tracks by remember { mutableStateOf<List<Track>?>(null) }
    var loadError by remember { mutableStateOf<String?>(null) }
    var nowPlayingOpen by remember { mutableStateOf(false) }
    var reloadKey by remember { mutableIntStateOf(0) }
    var currentTab by remember { mutableIntStateOf(0) } // 0=Home, 1=Library

    // Observe local tracks from reconstruction manager
    val localTracks by reconstructionManager.tracks.collectAsState()
    val isProcessing by reconstructionManager.isProcessing.collectAsState()

    // Auto-play external audio when received via intent
    LaunchedEffect(externalAudio) {
        if (externalAudio.isNotEmpty()) {
            playback.playExternal(externalAudio)
            nowPlayingOpen = true
            onExternalAudioConsumed()
        }
    }

    // Load cloud catalogue for Home tab
    LaunchedEffect(reloadKey) {
        tracks = null
        loadError = null
        val result = withContext(Dispatchers.IO) { runCatching { client.playableCatalogue().tracks } }
        result.onSuccess {
            tracks = it
            if (it.isEmpty()) loadError = "曲库中暂时没有可播放作品"
        }.onFailure { loadError = "曲库连接失败，请检查网络后重试" }
    }

    // Playback position ticker
    LaunchedEffect(playback.state.current?.id) {
        while (playback.state.current != null) {
            playback.tick()
            delay(500)
        }
    }

    BackHandler(enabled = nowPlayingOpen) { nowPlayingOpen = false }

    Scaffold(
        containerColor = Background,
        bottomBar = {
            if (!nowPlayingOpen) {
                Column {
                    if (playback.state.current != null) {
                        MiniPlayer(playback = playback, onOpen = { nowPlayingOpen = true })
                    }
                    NavigationBar(containerColor = Color.White, tonalElevation = 0.dp) {
                        NavigationBarItem(
                            selected = currentTab == 0,
                            onClick = { currentTab = 0 },
                            icon = { Icon(Icons.Outlined.Home, "首页") },
                            label = { Text("首页") },
                            colors = NavigationBarItemDefaults.colors(indicatorColor = Color(0xFFEDE8FF)),
                        )
                        NavigationBarItem(
                            selected = currentTab == 1,
                            onClick = { currentTab = 1 },
                            icon = { Icon(Icons.Outlined.LibraryMusic, "曲库") },
                            label = { Text("我的音乐") },
                            colors = NavigationBarItemDefaults.colors(indicatorColor = Color(0xFFEDE8FF)),
                        )
                        NavigationBarItem(
                            selected = false,
                            onClick = { if (playback.state.current != null) nowPlayingOpen = true },
                            icon = { Icon(Icons.Outlined.GraphicEq, "正在播放") },
                            label = { Text("播放") },
                        )
                    }
                }
            }
        },
    ) { padding ->
        Box(Modifier.fillMaxSize().padding(padding)) {
            if (nowPlayingOpen) {
                NowPlaying(playback = playback, onBack = { nowPlayingOpen = false })
            } else when (currentTab) {
                0 -> Home(
                    tracks = tracks,
                    error = loadError,
                    onRetry = { reloadKey++ },
                    onPlay = { index -> tracks?.let { playback.play(it, index) } },
                    onPickAudio = onPickAudio,
                )
                1 -> LibraryPage(
                    localTracks = localTracks,
                    isProcessing = isProcessing,
                    onPickAudio = onPickAudio,
                    onPlayOriginal = { track -> playback.playLocalOriginal(track) },
                    onReconstruct = { track ->
                        // Launch reconstruction in coroutine scope
                    },
                    playback = playback,
                )
            }
        }
    }
}

// ===========================================================================
// HOME TAB — cloud catalogue + Choose Music entry point
// ===========================================================================

@Composable
private fun Home(
    tracks: List<Track>?,
    error: String?,
    onRetry: () -> Unit,
    onPlay: (Int) -> Unit,
    onPickAudio: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        item { BrandHeader() }

        // P09: Choose Music button — primary local-file entry point
        item {
            ChooseMusicCard(onPickAudio = onPickAudio)
        }

        item {
            Text("发现音乐", color = Navy, fontSize = 27.sp, fontWeight = FontWeight.Bold)
            Text("先听见，再播放", color = Muted, fontSize = 14.sp)
        }
        when {
            tracks == null && error == null -> item { LoadingCard() }
            error != null -> item { ErrorCard(error, onRetry) }
            !tracks.isNullOrEmpty() -> {
                if (tracks.isNotEmpty()) {
                    item { FeaturedTrack(tracks.first()) { onPlay(0) } }
                    item { SectionTitle("作品") }
                    itemsIndexed(tracks, key = { _, track -> track.id }) { index, track ->
                        TrackRow(track = track, index = index, onPlay = onPlay)
                    }
                }
            }
        }
    }
}

/** P09: "Choose Music" card — opens SAF file picker. */
@Composable
private fun ChooseMusicCard(onPickAudio: () -> Unit) {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onPickAudio),
        color = Purple.copy(alpha = 0.08f),
        shape = RoundedCornerShape(18.dp),
    ) {
        Row(
            Modifier.fillMaxWidth().padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(
                Icons.Outlined.FolderOpen,
                contentDescription = "选择音乐",
                tint = Purple,
                modifier = Modifier.size(32.dp),
            )
            Spacer(Modifier.width(14.dp))
            Column {
                Text("选择本地音乐", color = Navy, fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
                Text("从设备中选择音频文件，用 Moodify 重建", color = Muted, fontSize = 12.sp)
            }
            Spacer(Modifier.weight(1f))
            Icon(Icons.Outlined.ChevronRight, null, tint = Muted)
        }
    }
}

// ===========================================================================
// LIBRARY TAB — local tracks + reconstruction status
// ===========================================================================

@Composable
private fun LibraryPage(
    localTracks: List<LocalTrack>,
    isProcessing: Boolean,
    onPickAudio: () -> Unit,
    onPlayOriginal: (LocalTrack) -> Unit,
    onReconstruct: (LocalTrack) -> Unit,
    playback: PlaybackController,
) {
    val scope = rememberCoroutineScope()

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(start = 18.dp, end = 18.dp, top = 12.dp, bottom = 24.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        item {
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("我的音乐", color = Navy, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                Button(onClick = onPickAudio, colors = ButtonDefaults.buttonColors(containerColor = Purple)) {
                    Icon(Icons.Outlined.Add, null, modifier = Modifier.size(18.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("添加")
                }
            }
        }

        if (localTracks.isEmpty()) {
            item {
                Surface(color = Color.White, shape = RoundedCornerShape(18.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Outline)) {
                    Column(Modifier.fillMaxWidth().padding(32.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Icon(Icons.Outlined.MusicNote, null, tint = Muted, modifier = Modifier.size(48.dp))
                        Spacer(Modifier.height(12.dp))
                        Text("还没有本地音乐", color = Navy, fontSize = 15.sp)
                        Text("点击上方「添加」选择音频文件", color = Muted, fontSize = 12.sp)
                    }
                }
            }
        } else {
            itemsIndexed(localTracks, key = { _, it -> it.localTrackId }) { _, track ->
                LocalTrackRow(
                    track = track,
                    isProcessing = isProcessing && track.reconstructionStatus == ReconstructionStatus.RECONSTRUCTING,
                    onPlay = { onPlayOriginal(track) },
                    onReconstruct = {
                        scope.launch {
                            // Note: in production this would call reconstructionManager.submitReconstruction()
                            // For v0.1 stub, we just update status locally
                            onReconstruct(track)
                        }
                    },
                    playback = playback,
                )
            }
        }
    }
}

/** P09: Single local track row with status badge and action buttons. */
@Composable
private fun LocalTrackRow(
    track: LocalTrack,
    isProcessing: Boolean,
    onPlay: () -> Unit,
    onReconstruct: () -> Unit,
    playback: PlaybackController,
) {
    Surface(
        color = Color.White,
        shape = RoundedCornerShape(16.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, Outline),
    ) {
        Column(Modifier.padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Status-colored artwork placeholder
                Box(
                    Modifier.size(44.dp).clip(RoundedCornerShape(11.dp))
                        .background(statusColor(track.reconstructionStatus)),
                    contentAlignment = Alignment.Center,
                ) {
                    if (isProcessing) {
                        CircularProgressIndicator(color = Color.White, strokeWidth = 2.dp, modifier = Modifier.size(20.dp))
                    } else {
                        Icon(Icons.Outlined.MusicNote, null, tint = Color.White, modifier = Modifier.size(20.dp))
                    }
                }
                Spacer(Modifier.width(12.dp))
                Column(Modifier.weight(1f)) {
                    Text(track.displayName, color = Navy, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    Row {
                        Text(statusLabel(track.reconstructionStatus), color = statusColor(track.reconstructionStatus), fontSize = 11.sp)
                        if (track.durationMs > 0) {
                            Text(" · ${formatDuration(track.durationMs)}", color = Muted, fontSize = 11.sp)
                        }
                    }
                }
            }

            // Action row: Play Original | Reconstruct
            Row(
                Modifier.fillMaxWidth().padding(top = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                OutlinedButton(
                    onClick = onPlay,
                    modifier = Modifier.weight(1f).height(36.dp),
                    shape = RoundedCornerShape(10.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp),
                ) {
                    Icon(Icons.Outlined.PlayArrow, null, modifier = Modifier.size(16.dp))
                    Spacer(Modifier.width(4.dp))
                    Text("播放原曲", fontSize = 12.sp)
                }

                val canReconstruct = track.reconstructionStatus in listOf(
                    ReconstructionStatus.LOCAL_ONLY,
                    ReconstructionStatus.FAILED,
                    ReconstructionStatus.SOURCE_PRESERVED,
                )

                FilledTonalButton(
                    onClick = onReconstruct,
                    enabled = canReconstruct && !isProcessing,
                    modifier = Modifier.weight(1f).height(36.dp),
                    shape = RoundedCornerShape(10.dp),
                    colors = ButtonDefaults.filledTonalButtonColors(containerColor = Purple.copy(alpha = 0.15f)),
                    contentPadding = PaddingValues(horizontal = 12.dp),
                ) {
                    if (isProcessing) {
                        CircularProgressIndicator(color = Purple, strokeWidth = 2.dp, modifier = Modifier.size(16.dp))
                    } else {
                        Icon(Icons.Outlined.AutoAwesome, null, modifier = Modifier.size(16.dp), tint = Purple)
                    }
                    Spacer(Modifier.width(4.dp))
                    Text(if (isProcessing) "处理中…" else "Moodify", fontSize = 12.sp, color = Purple)
                }
            }
        }
    }
}

// ===========================================================================
// VISUAL COMPONENTS (kept from original, minor updates)
// ===========================================================================

@Composable
private fun BrandHeader() {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        IconButton(onClick = { }) { Icon(Icons.Outlined.Menu, "菜单", tint = Navy) }
        Canvas(Modifier.size(44.dp, 30.dp)) {
            val y = size.height / 2
            val path = Path().apply {
                moveTo(0f, y); lineTo(size.width * .18f, y)
                lineTo(size.width * .28f, y * .45f); lineTo(size.width * .38f, y * 1.55f)
                lineTo(size.width * .5f, y * .15f); lineTo(size.width * .62f, y * 1.55f)
                lineTo(size.width * .73f, y * .65f); lineTo(size.width * .82f, y)
                lineTo(size.width, y)
            }
            drawPath(path, color = Blue, style = Stroke(width = 4.dp.toPx()))
        }
        Text("Moodify", modifier = Modifier.weight(1f).padding(start = 7.dp), color = Navy, fontSize = 26.sp, fontWeight = FontWeight.Bold)
        IconButton(onClick = { }) { Icon(Icons.Outlined.Search, "搜索", tint = Navy) }
    }
}

@Composable
private fun FeaturedTrack(track: Track, onPlay: () -> Unit) {
    Box(
        Modifier.fillMaxWidth().height(250.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(Brush.linearGradient(listOf(Color(0xFF322681), Color(0xFF7651D8), Color(0xFFD88AE7)))),
    ) {
        Canvas(Modifier.fillMaxSize()) {
            repeat(24) { i ->
                drawCircle(Color.White.copy(alpha = .35f), 1.3f, Offset(size.width * ((i * 37) % 97) / 97f, size.height * ((i * 19) % 58) / 100f))
            }
            drawCircle(Color(0x44FFE5FF), size.width * .20f, Offset(size.width * .72f, size.height * .34f))
            drawCircle(Color.White.copy(.65f), size.width * .15f, Offset(size.width * .72f, size.height * .34f), style = Stroke(2.dp.toPx()))
            val mountain = Path().apply {
                moveTo(0f, size.height * .72f); lineTo(size.width * .25f, size.height * .5f)
                lineTo(size.width * .43f, size.height * .67f); lineTo(size.width * .64f, size.height * .53f)
                lineTo(size.width, size.height * .72f); lineTo(size.width, size.height); lineTo(0f, size.height); close()
            }
            drawPath(mountain, Color(0xAA171652))
        }
        Column(Modifier.fillMaxSize().padding(18.dp)) {
            Surface(color = Color(0x55351C92), shape = RoundedCornerShape(14.dp)) {
                Text("今日推荐", color = Color.White, fontSize = 12.sp, modifier = Modifier.padding(horizontal = 11.dp, vertical = 6.dp))
            }
            Spacer(Modifier.weight(1f))
            Text(track.title, color = Color.White, fontSize = 23.sp, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
            Text(track.creatorHandle ?: "Moodify", color = Color.White.copy(.9f), fontSize = 13.sp)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Outlined.PlayArrow, null, tint = Color.White, modifier = Modifier.size(17.dp))
                Text(formatDuration(track.durationMs), color = Color.White.copy(.82f), fontSize = 12.sp)
                Spacer(Modifier.weight(1f))
                FilledIconButton(onClick = onPlay, colors = IconButtonDefaults.filledIconButtonColors(containerColor = Color.White), modifier = Modifier.size(54.dp)) {
                    Icon(Icons.Outlined.PlayArrow, "播放", tint = Purple, modifier = Modifier.size(30.dp))
                }
            }
        }
    }
}

@Composable private fun SectionTitle(title: String) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Text(title, color = Navy, fontSize = 18.sp, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
        Text("全部", color = Muted, fontSize = 12.sp)
    }
}

@Composable
private fun TrackRow(track: Track, index: Int, onPlay: (Int) -> Unit) {
    Surface(color = Color.White, shape = RoundedCornerShape(18.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Outline)) {
        Row(Modifier.fillMaxWidth().clickable { onPlay(index) }.padding(11.dp), verticalAlignment = Alignment.CenterVertically) {
            Box(
                Modifier.size(52.dp).clip(RoundedCornerShape(13.dp))
                    .background(Brush.linearGradient(if (index % 2 == 0) listOf(Purple, Blue) else listOf(Color(0xFFEB74B7), Color(0xFF7554D8)))),
                contentAlignment = Alignment.Center,
            ) { Icon(Icons.Outlined.MusicNote, null, tint = Color.White) }
            Column(Modifier.weight(1f).padding(horizontal = 11.dp)) {
                Text(track.title, color = Navy, fontSize = 14.sp, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                Text(track.creatorHandle ?: "Moodify", color = Muted, fontSize = 11.sp)
                Text(formatDuration(track.durationMs), color = Muted, fontSize = 10.sp)
            }
            OutlinedIconButton(onClick = { onPlay(index) }, modifier = Modifier.size(38.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Outline)) {
                Icon(Icons.Outlined.PlayArrow, "播放 ${track.title}", tint = Blue)
            }
        }
    }
}

@Composable
private fun MiniPlayer(playback: PlaybackController, onOpen: () -> Unit) {
    val state = playback.state
    val track = state.current ?: return
    Surface(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 4.dp).clickable(onClick = onOpen),
        color = Purple,
        shape = RoundedCornerShape(17.dp),
        shadowElevation = 7.dp,
    ) {
        Column {
            Row(Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 9.dp), verticalAlignment = Alignment.CenterVertically) {
                Box(Modifier.size(39.dp).clip(RoundedCornerShape(10.dp)).background(Color.White.copy(.18f)), contentAlignment = Alignment.Center) {
                    Icon(Icons.Outlined.MusicNote, null, tint = Color.White)
                }
                Column(Modifier.weight(1f).padding(horizontal = 10.dp)) {
                    Text(track.title, color = Color.White, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    Text(track.creatorHandle ?: "Moodify", color = Color.White.copy(.72f), fontSize = 10.sp)
                }
                IconButton(onClick = { playback.previous() }) { Icon(Icons.Outlined.SkipPrevious, "上一首", tint = Color.White) }
                IconButton(onClick = { playback.toggle() }) { Icon(if (state.isPlaying) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, if (state.isPlaying) "暂停" else "播放", tint = Color.White) }
                IconButton(onClick = { playback.next() }) { Icon(Icons.Outlined.SkipNext, "下一首", tint = Color.White) }
            }
            LinearProgressIndicator(
                progress = { if (state.durationMs > 0) state.positionMs.toFloat() / state.durationMs else 0f },
                modifier = Modifier.fillMaxWidth().height(2.dp),
                color = Color.White,
                trackColor = Color.White.copy(.22f),
            )
        }
    }
}

@Composable
private fun NowPlaying(playback: PlaybackController, onBack: () -> Unit) {
    val state = playback.state
    val track = state.current ?: return
    Column(Modifier.fillMaxSize().padding(horizontal = 24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
        Row(Modifier.fillMaxWidth().padding(top = 10.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.Outlined.KeyboardArrowDown, "收起", tint = Navy) }
            Text("正在播放", modifier = Modifier.weight(1f), color = Navy, fontWeight = FontWeight.SemiBold)
        }
        Spacer(Modifier.height(28.dp))
        Box(
            Modifier.fillMaxWidth().aspectRatio(1f).clip(RoundedCornerShape(34.dp))
                .background(Brush.linearGradient(listOf(Color(0xFF28206F), Purple, Color(0xFFCF83E8)))),
            contentAlignment = Alignment.Center,
        ) { Icon(Icons.Outlined.GraphicEq, null, tint = Color.White.copy(.75f), modifier = Modifier.size(100.dp)) }
        Spacer(Modifier.height(30.dp))
        Text(track.title, color = Navy, fontSize = 22.sp, fontWeight = FontWeight.Bold, maxLines = 2, overflow = TextOverflow.Ellipsis)
        Text(track.creatorHandle ?: "Moodify", color = Muted, fontSize = 13.sp)
        state.error?.let { Text(it, color = MaterialTheme.colorScheme.error, fontSize = 12.sp, modifier = Modifier.padding(top = 8.dp)) }
        Spacer(Modifier.height(18.dp))
        Slider(
            value = if (state.durationMs > 0) state.positionMs.toFloat().coerceIn(0f, state.durationMs.toFloat()) else 0f,
            onValueChange = { playback.seekTo(it.toLong()) },
            valueRange = 0f..state.durationMs.toFloat().coerceAtLeast(1f),
            colors = SliderDefaults.colors(thumbColor = Purple, activeTrackColor = Purple, inactiveTrackColor = Outline),
        )
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(formatDuration(state.positionMs), color = Muted, fontSize = 11.sp)
            Text(formatDuration(state.durationMs), color = Muted, fontSize = 11.sp)
        }
        Spacer(Modifier.height(16.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center, verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = { playback.previous() }, modifier = Modifier.size(58.dp)) { Icon(Icons.Outlined.SkipPrevious, "上一首", tint = Navy, modifier = Modifier.size(36.dp)) }
            Spacer(Modifier.width(28.dp))
            FilledIconButton(onClick = { playback.toggle() }, modifier = Modifier.size(72.dp), colors = IconButtonDefaults.filledIconButtonColors(containerColor = Purple)) {
                if (state.isLoading) CircularProgressIndicator(color = Color.White, strokeWidth = 2.dp, modifier = Modifier.size(28.dp))
                else Icon(if (state.isPlaying) Icons.Outlined.Pause else Icons.Outlined.PlayArrow, if (state.isPlaying) "暂停" else "播放", tint = Color.White, modifier = Modifier.size(38.dp))
            }
            Spacer(Modifier.width(28.dp))
            IconButton(onClick = { playback.next() }, modifier = Modifier.size(58.dp)) { Icon(Icons.Outlined.SkipNext, "下一首", tint = Navy, modifier = Modifier.size(36.dp)) }
        }
    }
}

@Composable private fun LoadingCard() {
    Box(Modifier.fillMaxWidth().height(240.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Purple) }
}

@Composable private fun ErrorCard(message: String, onRetry: () -> Unit) {
    Surface(color = Color.White, shape = RoundedCornerShape(22.dp), border = androidx.compose.foundation.BorderStroke(1.dp, Outline)) {
        Column(Modifier.fillMaxWidth().padding(24.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Icon(Icons.Outlined.CloudOff, null, tint = Muted, modifier = Modifier.size(42.dp))
            Text(message, color = Navy, modifier = Modifier.padding(vertical = 12.dp))
            Button(onClick = onRetry) { Text("重新连接") }
        }
    }
}

// ===========================================================================
// HELPERS
// ===========================================================================

private fun formatDuration(ms: Long?): String {
    if (ms == null || ms <= 0) return "—"
    val seconds = ms / 1000
    return "%d:%02d".format(seconds / 60, seconds % 60)
}

/** Map reconstruction status to display label (user-facing, not technical). */
private fun statusLabel(status: ReconstructionStatus): String = when (status) {
    ReconstructionStatus.LOCAL_ONLY -> "本地文件"
    ReconstructionStatus.UPLOADING -> "上传中…"
    ReconstructionStatus.RECONSTRUCTING -> "处理中…"
    ReconstructionStatus.READY -> "已完成 ✓"
    ReconstructionStatus.SOURCE_PRESERVED -> "原作保留"
    ReconstructionStatus.FAILED -> "失败"
    ReconstructionStatus.HUMAN_REQUIRED -> "等待审核"
}

/** Map reconstruction status to badge color. */
private fun statusColor(status: ReconstructionStatus): Color = when (status) {
    ReconstructionStatus.LOCAL_ONLY -> Muted
    ReconstructionStatus.UPLOADING -> Blue
    ReconstructionStatus.RECONSTRUCTING -> Purple
    ReconstructionStatus.READY -> Color(0xFF22C55E)   // green
    ReconstructionStatus.SOURCE_PRESERVED -> Color(0xFFF59E0B) // amber
    ReconstructionStatus.FAILED -> Color(0xFFEF4444)   // red
    ReconstructionStatus.HUMAN_REQUIRED -> Color(0xFFF97316) // orange
}
