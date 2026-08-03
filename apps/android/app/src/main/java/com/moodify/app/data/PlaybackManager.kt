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

data class PlaybackState(
    val title: String = "",
    val url: String? = null,
    val playing: Boolean = false,
    val positionMs: Long = 0,
    val durationMs: Long = 0,
    val error: String? = null,
)

/**
 * Minimal Media3 playback for the demo: streams processed/original audio
 * from the Moodify backend with the pair token attached (the API requires
 * Bearer auth on every endpoint).
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
                    }
                })
            }
    }

    /** Play a backend audio endpoint like /api/v1/artifacts/{id}/download. */
    fun play(path: String, title: String) {
        val p = player ?: return
        val base = baseUrlProvider?.invoke()?.trimEnd('/') ?: return
        val url = "$base/api/v1$path"
        refreshAuthHeader()
        p.setMediaItem(MediaItem.fromUri(url))
        p.prepare()
        p.play()
        _state.value = PlaybackState(title = title, url = url, playing = true)
    }

    /** Keep the Bearer header in sync with the current pair token. */
    private fun refreshAuthHeader() {
        val token = tokenProvider?.invoke()
        dataSourceFactory?.setDefaultRequestProperties(
            if (token != null) mapOf("Authorization" to "Bearer $token") else emptyMap()
        )
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
}
