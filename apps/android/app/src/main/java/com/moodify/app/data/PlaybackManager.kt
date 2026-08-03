package com.moodify.app.data

import android.content.Context
import androidx.media3.common.MediaItem
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/** One playable track in the queue; path is a backend API path. */
data class QueueItem(
    val title: String,
    val subtitle: String = "",
    val path: String,
    val isOriginal: Boolean = false,
    val preset: String = "",
    val mrsDelta: Double? = null,
    val gatePassed: Boolean = false,
)

data class PlaybackState(
    val title: String = "",
    val url: String? = null,
    val playing: Boolean = false,
    val positionMs: Long = 0,
    val durationMs: Long = 0,
    val error: String? = null,
    val queue: List<QueueItem> = emptyList(),
    val queueIndex: Int = -1,
) {
    val current: QueueItem? get() = queue.getOrNull(queueIndex)
}

/**
 * Media3 playback for the demo: streams processed/original audio from the
 * Moodify backend with the pair token attached (the API requires Bearer
 * auth on every endpoint). Queue-aware for continuous playback.
 */
object PlaybackManager {

    private var player: ExoPlayer? = null
    private var dataSourceFactory: DefaultHttpDataSource.Factory? = null
    private var baseUrlProvider: (() -> String)? = null
    private var tokenProvider: (() -> String?)? = null

    private val _state = MutableStateFlow(PlaybackState())
    val state: StateFlow<PlaybackState> = _state.asStateFlow()

    fun init(context: Context) {
        if (player != null) return
        val tokenStore = TokenStore(context.applicationContext)
        val baseUrlStore = BaseUrlStore(context.applicationContext)
        baseUrlProvider = { baseUrlStore.baseUrl }
        tokenProvider = { tokenStore.token() }
        val factory = DefaultHttpDataSource.Factory().apply {
            refreshAuthHeader()
        }
        dataSourceFactory = factory
        player = ExoPlayer.Builder(context.applicationContext)
            .setMediaSourceFactory(DefaultMediaSourceFactory(factory))
            .build()
            .apply {
                addListener(object : Player.Listener {
                    override fun onIsPlayingChanged(isPlaying: Boolean) {
                        _state.value = _state.value.copy(playing = isPlaying)
                    }

                    override fun onPlaybackStateChanged(playbackState: Int) {
                        val s = _state.value
                        val error = if (playbackState == Player.STATE_IDLE && s.url != null && s.error == null) {
                            "播放失败：无法从服务器加载音频"
                        } else null
                        _state.value = s.copy(error = error)
                        if (playbackState == Player.STATE_ENDED && s.queue.size > 1) {
                            next()
                        }
                    }

                    override fun onMediaItemTransition(mediaItem: MediaItem?, reason: Int) {
                        val s = _state.value
                        if (s.queue.isEmpty()) return
                        // derive queueIndex from the media item's custom key (index)
                        val idx = mediaItem?.mediaId?.toIntOrNull() ?: s.queueIndex
                        _state.value = s.copy(queueIndex = idx)
                    }
                })
            }
    }

    /** Load a whole queue and start playing from [startIndex]. */
    fun playQueue(items: List<QueueItem>, startIndex: Int = 0) {
        val p = player ?: return
        if (items.isEmpty()) return
        val idx = startIndex.coerceIn(0, items.size - 1)
        refreshAuthHeader()
        _state.value = PlaybackState(queue = items, queueIndex = idx)
        playItem(items[idx])
    }

    /** Play a single backend endpoint path (kept for simple call sites). */
    fun play(path: String, title: String) {
        playQueue(listOf(QueueItem(title = title, path = path)), 0)
    }

    fun next() {
        val s = _state.value
        if (s.queue.isEmpty()) return
        val idx = (s.queueIndex + 1) % s.queue.size
        jumpTo(idx)
    }

    fun jumpTo(index: Int) {
        val s = _state.value
        if (s.queue.isEmpty()) return
        val idx = index.coerceIn(0, s.queue.size - 1)
        _state.value = s.copy(queueIndex = idx)
        playItem(s.queue[idx])
    }

    fun previous() {
        val s = _state.value
        if (s.queue.isEmpty()) return
        val idx = (s.queueIndex - 1 + s.queue.size) % s.queue.size
        _state.value = s.copy(queueIndex = idx)
        playItem(s.queue[idx])
    }

    private fun playItem(item: QueueItem) {
        val p = player ?: return
        val base = baseUrlProvider?.invoke()?.trimEnd('/') ?: return
        val url = "$base/api/v1${item.path}"
        refreshAuthHeader()
        p.setMediaItem(MediaItem.fromUri(url).buildUpon().setMediaId("${_state.value.queueIndex}").build())
        p.prepare()
        p.play()
        _state.value = _state.value.copy(title = item.title, url = url, playing = true, error = null)
    }

    fun toggle() {
        val p = player ?: return
        if (p.isPlaying) p.pause() else p.play()
    }

    fun seekTo(positionMs: Long) {
        player?.seekTo(positionMs)
    }

    fun stop() {
        player?.stop()
        _state.value = PlaybackState()
    }

    /** Called from a UI ticker to refresh position/duration. */
    fun tick() {
        val p = player ?: return
        val s = _state.value
        if (s.url == null) return
        _state.value = s.copy(
            positionMs = p.currentPosition.coerceAtLeast(0),
            durationMs = p.duration.coerceAtLeast(0),
            playing = p.isPlaying,
        )
    }

    fun release() {
        player?.release()
        player = null
    }

    /** Keep the Bearer header in sync with the current pair token. */
    private fun refreshAuthHeader() {
        val token = tokenProvider?.invoke()
        dataSourceFactory?.setDefaultRequestProperties(
            if (token != null) mapOf("Authorization" to "Bearer $token") else emptyMap()
        )
    }
}
