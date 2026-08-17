package com.moodify.music.player

import android.content.Context
import android.net.Uri
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import com.moodify.music.data.Track
import com.moodify.music.ExternalAudio

data class PlaybackUiState(
    val queue: List<Track> = emptyList(),
    val index: Int = -1,
    val isPlaying: Boolean = false,
    val isLoading: Boolean = false,
    val positionMs: Long = 0,
    val durationMs: Long = 0,
    val error: String? = null,
) {
    val current: Track? get() = queue.getOrNull(index)
}

class PlaybackController(context: Context) {
    var state by mutableStateOf(PlaybackUiState())
        private set

    private val player = ExoPlayer.Builder(context).build().apply {
        addListener(object : Player.Listener {
            override fun onIsPlayingChanged(isPlaying: Boolean) {
                state = state.copy(isPlaying = isPlaying)
            }

            override fun onPlaybackStateChanged(playbackState: Int) {
                state = state.copy(
                    isLoading = playbackState == Player.STATE_BUFFERING,
                    durationMs = duration.coerceAtLeast(0),
                )
                if (playbackState == Player.STATE_ENDED) next()
            }

            override fun onPlayerError(error: PlaybackException) {
                state = state.copy(isLoading = false, error = "暂时无法播放，请稍后重试")
            }
        })
    }

    fun play(queue: List<Track>, index: Int) {
        if (queue.isEmpty()) return
        val safeIndex = index.coerceIn(queue.indices)
        state = PlaybackUiState(queue = queue, index = safeIndex, isLoading = true)
        load(queue[safeIndex])
    }

    fun playExternal(audio: List<ExternalAudio>) {
        if (audio.isEmpty()) return
        val queue = audio.mapIndexed { index, item ->
            Track(
                id = "external-$index-${item.uri}",
                title = item.displayName.substringBeforeLast('.').ifBlank { item.displayName },
                creatorId = "external",
                creatorHandle = "本地音频",
                status = "external",
                primaryLanguage = null,
                durationMs = null,
                publishedAt = null,
                audioAssetKey = null,
                externalUri = item.uri.toString(),
            )
        }
        play(queue, 0)
    }

    fun toggle() {
        if (state.current == null) return
        if (player.isPlaying) player.pause() else player.play()
    }

    fun previous() = move(-1)
    fun next() = move(1)

    fun seekTo(positionMs: Long) {
        player.seekTo(positionMs.coerceAtLeast(0))
        tick()
    }

    fun tick() {
        state = state.copy(
            positionMs = player.currentPosition.coerceAtLeast(0),
            durationMs = player.duration.coerceAtLeast(0),
            isPlaying = player.isPlaying,
        )
    }

    private fun move(delta: Int) {
        val queue = state.queue
        if (queue.isEmpty()) return
        val nextIndex = (state.index + delta + queue.size) % queue.size
        state = state.copy(index = nextIndex, positionMs = 0, error = null, isLoading = true)
        load(queue[nextIndex])
    }

    private fun load(track: Track) {
        val uri = track.externalUri?.let(Uri::parse) ?: track.audioAssetKey?.let {
            Uri.parse("https://rongjinwenchuan.xyz/audio/$it")
        } ?: run {
            state = state.copy(isLoading = false, error = "这首作品暂时没有可播放音频")
            return
        }
        val item = MediaItem.Builder()
            .setMediaId(track.id)
            .setUri(uri)
            .build()
        player.setMediaItem(item)
        player.prepare()
        player.play()
    }

    fun release() = player.release()
}
