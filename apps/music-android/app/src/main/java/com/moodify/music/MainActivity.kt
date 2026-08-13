package com.moodify.music

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import com.moodify.music.data.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {

    private val client = BffClient()
    private var player: ExoPlayer? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                MusicApp(
                    client = client,
                    onPlay = { track -> playTrack(track) },
                    onStop = { player?.stop() },
                )
            }
        }
    }

    private fun playTrack(track: Track) {
        val url = track.audioAssetKey?.let { "https://rongjinwenchuan.xyz/audio/$it" } ?: return
        val p = player ?: ExoPlayer.Builder(this).build().also { player = it }
        p.setMediaItem(MediaItem.fromUri(url))
        p.prepare()
        p.playWhenReady = true
    }

    override fun onDestroy() {
        player?.release()
        player = null
        super.onDestroy()
    }
}

@Composable
fun MusicApp(client: BffClient, onPlay: (Track) -> Unit, onStop: () -> Unit) {
    val scope = rememberCoroutineScope()
    var tracks by remember { mutableStateOf<List<Track>?>(null) }
    var selected by remember { mutableStateOf<Track?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        error = withContext(Dispatchers.IO) {
            try {
                tracks = client.catalogue().tracks
                null
            } catch (e: Exception) {
                e.message ?: "网络错误"
            }
        }
    }

    Scaffold(topBar = {
        CenterAlignedTopAppBar(title = { Text("Moodify Music") })
    }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp)) {
            if (error != null) {
                Text("加载失败：$error（离线时不会展示伪曲库）", color = MaterialTheme.colorScheme.error)
            }
            when {
                selected != null -> TrackDetail(selected!!, onBack = { selected = null }, onPlay = onPlay)
                tracks == null && error == null -> Text("加载中…")
                tracks != null -> LazyColumn {
                    items(tracks!!) { track ->
                        Card(Modifier.fillMaxWidth().padding(vertical = 6.dp)) {
                            Column(Modifier.clickable { selected = track }.padding(12.dp)) {
                                Text(track.title, style = MaterialTheme.typography.titleMedium)
                                Text("${track.creatorHandle ?: "—"} · ${track.primaryLanguage ?: "—"}", style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TrackDetail(track: Track, onBack: () -> Unit, onPlay: (Track) -> Unit) {
    Column {
        TextButton(onClick = onBack) { Text("← 返回") }
        Text(track.title, style = MaterialTheme.typography.headlineSmall)
        Text("${track.creatorHandle ?: "—"} · ${track.primaryLanguage ?: "—"}", style = MaterialTheme.typography.bodyMedium)
        track.durationMs?.let { Text("时长 ${it / 1000}s", style = MaterialTheme.typography.bodySmall) }
        Spacer(Modifier.height(16.dp))
        Button(onClick = { onPlay(track) }) { Text("播放") }
        if (track.audioAssetKey == null) {
            Text("此曲目暂无可播放媒体", style = MaterialTheme.typography.bodySmall)
        }
    }
}
