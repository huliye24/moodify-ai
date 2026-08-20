package com.moodify.app.data

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.annotation.OptIn
import androidx.core.content.ContextCompat
import androidx.media3.common.MediaItem
import androidx.media3.common.MediaMetadata
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.datasource.DefaultHttpDataSource
import androidx.media3.exoplayer.DefaultLoadControl
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.exoplayer.source.DefaultMediaSourceFactory
import androidx.media3.session.MediaSession
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * One playable track in the queue.
 * [path] is either an absolute http(s) URL (public audio asset) or a
 * backend API path (resolved as <base>/api/v1<path> with Bearer auth).
 */
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
    /** Stable user intent; unlike [playing], this stays true while a new track buffers. */
    val playWhenReady: Boolean = false,
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
@OptIn(androidx.media3.common.util.UnstableApi::class)
object PlaybackManager {

    private var player: ExoPlayer? = null
    private var session: MediaSession? = null
    private var dataSourceFactory: DefaultHttpDataSource.Factory? = null
    private var audioCache: PlaybackAudioCache? = null
    private var baseUrlProvider: (() -> String)? = null
    private var tokenProvider: (() -> String?)? = null
    private var userWantsPlayback = false
    private var artworkUri: Uri? = null

    private val _state = MutableStateFlow(PlaybackState())
    val state: StateFlow<PlaybackState> = _state.asStateFlow()

    /** The MediaSession backing [PlaybackService]'s notification/controls. */
    internal val mediaSession: MediaSession?
        get() = session

    fun init(context: Context) {
        if (player != null) return
        artworkUri = Uri.parse("android.resource://${context.packageName}/drawable/moodify_lockscreen_artwork")
        val tokenStore = TokenStore(context.applicationContext)
        val baseUrlStore = BaseUrlStore(context.applicationContext)
        baseUrlProvider = { baseUrlStore.baseUrl }
        tokenProvider = { tokenStore.token() }
        val factory = DefaultHttpDataSource.Factory().apply {
            refreshAuthHeader()
        }
        dataSourceFactory = factory
        audioCache = PlaybackAudioCache(context.applicationContext, factory)
        val loadControl = DefaultLoadControl.Builder()
            .setBufferDurationsMs(
                20_000, // Keep enough audio ahead for an immediate swipe transition.
                90_000,
                100,
                250,
            )
            .setBackBuffer(5_000, true)
            .setPrioritizeTimeOverSizeThresholds(true)
            .build()
        player = ExoPlayer.Builder(context.applicationContext)
            .setMediaSourceFactory(DefaultMediaSourceFactory(audioCache!!.dataSourceFactory))
            .setLoadControl(loadControl)
            .build()
            .apply {
                repeatMode = Player.REPEAT_MODE_ALL
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

                    override fun onPlayerError(error: PlaybackException) {
                        _state.value = _state.value.copy(
                            playing = false,
                            error = "播放失败：无法从服务器加载音频",
                        )
                    }

                    override fun onMediaItemTransition(mediaItem: MediaItem?, reason: Int) {
                        val s = _state.value
                        if (s.queue.isEmpty()) return
                        // derive queueIndex from the media item's custom key (index)
                        val idx = mediaItem?.mediaId?.toIntOrNull() ?: s.queueIndex
                        val current = s.queue.getOrNull(idx)
                        _state.value = s.copy(
                            queueIndex = idx,
                            title = current?.title.orEmpty(),
                            url = current?.let(::resolveUrl),
                        )
                    }
                })
            }
        session = MediaSession.Builder(context.applicationContext, player!!).build()
        // The service drives the notification bar / lock-screen controls and
        // keeps the session alive when the UI is not visible.
        ContextCompat.startForegroundService(
            context.applicationContext,
            Intent(context.applicationContext, com.moodify.app.PlaybackService::class.java),
        )
    }

    /** Load a whole queue and start playing from [startIndex]. */
    fun playQueue(items: List<QueueItem>, startIndex: Int = 0, autoPlay: Boolean = true) {
        val p = player ?: return
        if (items.isEmpty()) return
        val idx = startIndex.coerceIn(0, items.size - 1)
        refreshAuthHeader()
        userWantsPlayback = autoPlay
        _state.value = PlaybackState(queue = items, queueIndex = idx, playWhenReady = autoPlay)
        p.setMediaItems(items.mapIndexed(::mediaItem), idx, 0L)
        p.playWhenReady = autoPlay
        p.prepare()
        val orderedForPrefetch = items.drop(idx + 1) + items.take(idx + 1)
        audioCache?.prefetch(orderedForPrefetch.map(::resolveUrl))
        val current = items[idx]
        _state.value = _state.value.copy(
            title = current.title,
            url = resolveUrl(current),
            playing = autoPlay,
            error = null,
        )
    }

    /** Populate the public catalogue without starting sound before the user's first Play tap. */
    fun loadQueue(items: List<QueueItem>, startIndex: Int = 0) = playQueue(items, startIndex, autoPlay = false)

    /** Play a single backend endpoint path (kept for simple call sites). */
    fun play(path: String, title: String) {
        playQueue(listOf(QueueItem(title = title, path = path)), 0)
    }

    fun next() {
        val s = _state.value
        if (s.queue.isEmpty()) return
        player?.seekToNextMediaItem()
    }

    fun jumpTo(index: Int) {
        val s = _state.value
        if (s.queue.isEmpty()) return
        val idx = index.coerceIn(0, s.queue.size - 1)
        player?.seekToDefaultPosition(idx)
        _state.value = s.copy(
            queueIndex = idx,
            title = s.queue[idx].title,
            url = resolveUrl(s.queue[idx]),
            playWhenReady = userWantsPlayback,
        )
    }

    fun previous() {
        val s = _state.value
        if (s.queue.isEmpty()) return
        player?.seekToPreviousMediaItem()
    }

    private fun resolveUrl(item: QueueItem): String {
        val base = baseUrlProvider?.invoke()?.trimEnd('/').orEmpty()
        return if (item.path.startsWith("http://") || item.path.startsWith("https://")) {
            item.path
        } else {
            "$base/api/v1${item.path}"
        }
    }

    private fun mediaItem(index: Int, item: QueueItem): MediaItem = MediaItem.Builder()
        .setUri(resolveUrl(item))
        .setCustomCacheKey(resolveUrl(item))
        .setMediaId(index.toString())
        .setMediaMetadata(
            MediaMetadata.Builder()
                .setTitle(item.title)
                .setArtworkUri(artworkUri)
                .apply { if (item.subtitle.isNotBlank()) setArtist(item.subtitle) }
                .build()
        )
        .build()

    fun toggle() {
        val p = player ?: return
        userWantsPlayback = !userWantsPlayback
        if (userWantsPlayback) p.play() else p.pause()
        _state.value = _state.value.copy(playWhenReady = userWantsPlayback, playing = userWantsPlayback && p.isPlaying)
    }

    fun seekTo(positionMs: Long) {
        player?.seekTo(positionMs)
    }

    fun stop() {
        userWantsPlayback = false
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
        session?.release()
        session = null
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
