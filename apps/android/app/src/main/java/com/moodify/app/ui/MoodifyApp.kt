package com.moodify.app.ui

import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.SizeTransform
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material.icons.outlined.LibraryMusic
import androidx.compose.material.icons.outlined.MusicNote
import androidx.compose.material.icons.outlined.PersonOutline
import androidx.compose.material.icons.rounded.PlayArrow
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.moodify.app.data.PersonalLibraryStore
import com.moodify.app.data.PlaybackManager
import com.moodify.app.data.QueueItem
import com.moodify.app.data.UserPlaylist
import com.moodify.app.ui.components.MoodifyMark
import com.moodify.app.ui.screens.HomeScreen
import kotlinx.coroutines.launch

private val AppNight = Color(0xFF000106)
private val AppText = Color(0xFFF8F7FB)
private val AppMuted = Color(0xFF9798C4)
private val AppPurple = Color(0xFF8139FF)

/** One listening experience with a user-owned library separate from the public catalogue queue. */
@Composable
fun MoodifyApp() {
    val context = LocalContext.current
    PlaybackManager.init(context)
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    val libraryStore = remember { PersonalLibraryStore(context) }
    val library by libraryStore.state.collectAsState()
    var destination by remember { mutableStateOf(DESTINATION_PLAYER) }
    var pendingPlaylistTrack by remember { mutableStateOf<QueueItem?>(null) }

    BackHandler(enabled = destination != DESTINATION_PLAYER) { destination = DESTINATION_PLAYER }

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = true,
        drawerContent = {
            MoodifyDrawerContent(destination) { selected ->
                destination = selected
                scope.launch { drawerState.close() }
            }
        },
        scrimColor = Color(0xB8030615),
    ) {
        AnimatedContent(
            targetState = destination,
            modifier = Modifier.fillMaxSize(),
            transitionSpec = {
                if (targetState == DESTINATION_PLAYER) {
                    (slideInHorizontally(tween(340, easing = FastOutSlowInEasing)) { it / 3 } + fadeIn(tween(220))) togetherWith
                        (slideOutHorizontally(tween(300, easing = FastOutSlowInEasing)) { -it } + fadeOut(tween(180)))
                } else {
                    (slideInHorizontally(tween(280, easing = FastOutSlowInEasing)) { -it / 6 } + fadeIn(tween(220))) togetherWith
                        fadeOut(tween(160))
                }.using(SizeTransform(clip = false))
            },
            label = "Moodify destination",
        ) { targetDestination ->
        when (targetDestination) {
            DESTINATION_PLAYER -> HomeScreen(
                favouritePaths = library.favouritePaths,
                onFavourite = libraryStore::toggleFavourite,
                onAddToPlaylist = { pendingPlaylistTrack = it },
            )
            DESTINATION_PLAYLISTS -> PlaylistsScreen(
                playlists = library.playlists,
                onCreate = { libraryStore.createPlaylist(it) },
                onMenu = { scope.launch { drawerState.open() } },
                onReturnToPlayer = { destination = DESTINATION_PLAYER },
            )
            DESTINATION_FAVOURITES -> LibraryScreen(
                title = "收藏",
                subtitle = "你喜欢的音乐",
                icon = Icons.Outlined.FavoriteBorder,
                tracks = PlaybackManager.state.value.queue.filter { it.path in library.favouritePaths },
                onMenu = { scope.launch { drawerState.open() } },
                onReturnToPlayer = { destination = DESTINATION_PLAYER },
            )
            DESTINATION_PROFILE -> ProfileSurface(
                onMenu = { scope.launch { drawerState.open() } },
                onReturnToPlayer = { destination = DESTINATION_PLAYER },
            )
        }
        }
    }

    pendingPlaylistTrack?.let { track ->
        AddToPlaylistDialog(
            track = track,
            playlists = library.playlists,
            onDismiss = { pendingPlaylistTrack = null },
            onAdd = { playlistId ->
                libraryStore.addToPlaylist(playlistId, track)
                pendingPlaylistTrack = null
            },
            onCreateAndAdd = { name ->
                if (libraryStore.createPlaylist(name, track)) pendingPlaylistTrack = null
            },
        )
    }
}

@Composable
private fun PlaylistsScreen(
    playlists: List<UserPlaylist>,
    onCreate: (String) -> Boolean,
    onMenu: () -> Unit,
    onReturnToPlayer: () -> Unit,
) {
    var newName by remember { mutableStateOf("") }
    var selectedId by remember { mutableStateOf<String?>(null) }
    val selected = playlists.firstOrNull { it.id == selectedId }
    Column(Modifier.fillMaxSize().edgeNavigationGesture(onMenu, onReturnToPlayer).background(AppNight).padding(horizontal = 24.dp)) {
        PageHeader("歌单", "你创建的私人歌单", onMenu)
        if (selected != null) {
            TextButton(onClick = { selectedId = null }) { Text("← 全部歌单", color = AppPurple) }
            Text(selected.name, color = AppText, fontSize = 24.sp, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(18.dp))
            TrackList(selected.tracks)
        } else {
            Row(verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(
                    value = newName,
                    onValueChange = { newName = it },
                    label = { Text("新歌单名称") },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                IconButton(onClick = { if (onCreate(newName)) newName = "" }) {
                    Icon(Icons.Outlined.Add, "创建歌单", tint = AppPurple)
                }
            }
            Spacer(Modifier.height(18.dp))
            if (playlists.isEmpty()) {
                EmptyLibrary(Icons.Outlined.LibraryMusic, "还没有歌单，先创建一个")
            } else {
                LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    items(playlists, key = { it.id }) { playlist ->
                        Row(
                            Modifier.fillMaxWidth().background(Color(0xFF080B18), RoundedCornerShape(18.dp))
                                .clickable { selectedId = playlist.id }.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Icon(Icons.Outlined.LibraryMusic, null, tint = AppPurple, modifier = Modifier.size(30.dp))
                            Column(Modifier.padding(start = 14.dp)) {
                                Text(playlist.name, color = AppText, fontSize = 17.sp)
                                Text("${playlist.tracks.size} 首", color = AppMuted, fontSize = 12.sp)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun AddToPlaylistDialog(
    track: QueueItem,
    playlists: List<UserPlaylist>,
    onDismiss: () -> Unit,
    onAdd: (String) -> Unit,
    onCreateAndAdd: (String) -> Unit,
) {
    var newName by remember(track.path) { mutableStateOf("") }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("加入歌单") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(track.title, maxLines = 1, overflow = TextOverflow.Ellipsis)
                playlists.forEach { playlist ->
                    TextButton(onClick = { onAdd(playlist.id) }, modifier = Modifier.fillMaxWidth()) {
                        Text("${playlist.name} · ${playlist.tracks.size} 首")
                    }
                }
                OutlinedTextField(
                    value = newName,
                    onValueChange = { newName = it },
                    label = { Text("新建歌单") },
                    singleLine = true,
                )
            }
        },
        confirmButton = {
            Button(onClick = { onCreateAndAdd(newName) }, enabled = newName.isNotBlank()) { Text("创建并加入") }
        },
        dismissButton = { TextButton(onClick = onDismiss) { Text("取消") } },
    )
}

@Composable
private fun LibraryScreen(
    title: String,
    subtitle: String,
    icon: ImageVector,
    tracks: List<QueueItem>,
    onMenu: () -> Unit,
    onReturnToPlayer: () -> Unit,
) {
    Column(Modifier.fillMaxSize().edgeNavigationGesture(onMenu, onReturnToPlayer).background(AppNight).padding(horizontal = 24.dp)) {
        PageHeader(title, subtitle, onMenu)
        if (tracks.isEmpty()) EmptyLibrary(icon, "这里还没有歌曲") else TrackList(tracks)
    }
}

@Composable
private fun TrackList(tracks: List<QueueItem>) {
    if (tracks.isEmpty()) {
        EmptyLibrary(Icons.Outlined.MusicNote, "这里还没有歌曲")
        return
    }
    LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        items(tracks, key = { it.path }) { track ->
            Row(
                Modifier.fillMaxWidth().background(Color(0xFF080B18), RoundedCornerShape(18.dp)).clickable {
                    val publicIndex = PlaybackManager.state.value.queue.indexOfFirst { it.path == track.path }
                    if (publicIndex >= 0) PlaybackManager.jumpTo(publicIndex) else PlaybackManager.playQueue(tracks, tracks.indexOf(track))
                }.padding(13.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    Modifier.size(52.dp).background(Brush.linearGradient(listOf(AppPurple, Color(0xFF22BCFF))), RoundedCornerShape(14.dp)),
                    contentAlignment = Alignment.Center,
                ) { Icon(Icons.Rounded.PlayArrow, null, tint = Color.White) }
                Text(track.title, color = AppText, fontSize = 16.sp, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.weight(1f).padding(horizontal = 14.dp))
                Icon(Icons.Outlined.MusicNote, null, tint = AppPurple)
            }
        }
    }
}

@Composable
private fun EmptyLibrary(icon: ImageVector, message: String) {
    Column(Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Icon(icon, null, tint = AppPurple, modifier = Modifier.size(52.dp))
        Text(message, color = AppMuted, fontSize = 15.sp, modifier = Modifier.padding(top = 18.dp))
    }
}

@Composable
private fun ProfileSurface(onMenu: () -> Unit, onReturnToPlayer: () -> Unit) {
    Column(Modifier.fillMaxSize().edgeNavigationGesture(onMenu, onReturnToPlayer).background(AppNight).padding(horizontal = 24.dp)) {
        PageHeader("个人主页", "你的 Moodify", onMenu)
        Column(Modifier.fillMaxWidth().padding(top = 42.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Box(
                Modifier.size(104.dp).background(Brush.linearGradient(listOf(AppPurple, Color(0xFF22BCFF))), CircleShape),
                contentAlignment = Alignment.Center,
            ) { Icon(Icons.Outlined.PersonOutline, null, tint = Color.White, modifier = Modifier.size(62.dp)) }
            Text("Moodify Listener", color = AppText, fontSize = 24.sp, fontWeight = FontWeight.SemiBold, modifier = Modifier.padding(top = 22.dp))
            Text("让每一次聆听，都更接近感动", color = AppMuted, fontSize = 14.sp, modifier = Modifier.padding(top = 9.dp))
        }
    }
}

@Composable
private fun PageHeader(title: String, subtitle: String, onMenu: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(top = 36.dp, bottom = 34.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(52.dp).clickable(onClick = onMenu), contentAlignment = Alignment.Center) {
            MoodifyMark(Modifier.size(44.dp, 29.dp))
        }
        Column(Modifier.padding(start = 12.dp)) {
            Text(title, color = AppText, fontSize = 28.sp, fontWeight = FontWeight.SemiBold)
            Text(subtitle, color = AppMuted, fontSize = 12.sp, modifier = Modifier.padding(top = 3.dp))
        }
        Spacer(Modifier.weight(1f))
    }
}

/** Left edge opens navigation; right edge returns every personal surface to Play. */
private fun Modifier.edgeNavigationGesture(onOpenDrawer: () -> Unit, onReturn: () -> Unit): Modifier =
    pointerInput(onOpenDrawer, onReturn) {
    var startX = 0f
    var totalDragX = 0f
    detectHorizontalDragGestures(
        onDragStart = { offset ->
            startX = offset.x
            totalDragX = 0f
        },
        onHorizontalDrag = { change, dragAmount ->
            totalDragX += dragAmount
            val edgeWidth = 72.dp.toPx()
            val fromLeft = startX <= edgeWidth && totalDragX > 0f
            val fromRight = startX >= size.width - edgeWidth && totalDragX < 0f
            if ((fromLeft || fromRight) && kotlin.math.abs(totalDragX) >= 24.dp.toPx()) change.consume()
        },
        onDragEnd = {
            val edgeWidth = 72.dp.toPx()
            val threshold = 88.dp.toPx()
            when {
                startX <= edgeWidth && totalDragX >= threshold -> onOpenDrawer()
                startX >= size.width - edgeWidth && totalDragX <= -threshold -> onReturn()
            }
            totalDragX = 0f
        },
        onDragCancel = { totalDragX = 0f },
    )
}
