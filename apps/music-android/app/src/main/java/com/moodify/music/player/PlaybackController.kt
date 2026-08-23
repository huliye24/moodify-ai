package com.moodify.music.player

import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import com.moodify.music.data.LocalTrack
import com.moodify.music.data.ReconstructionStatus
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

/**
 * P09 Enhanced PlaybackController — adds:
 *   - Audio Focus management (yields to calls, notifications, other apps)
 *   - MediaSessionService wiring (background playback, lock screen)
 *   - LocalTrack support (offline original playback)
 *   - Reconstructed result playback (authenticated URL)
 */
class PlaybackController(
    context: Context,
    private val delivery: PlaybackDeliveryClient? = null,
) {
    var state by mutableStateOf(PlaybackUiState())
        private set

    private val player = ExoPlayer.Builder(context).build().apply {
        addListener(object : Player.Listener {
            override fun onIsPlayingChanged(isPlaying: Boolean) {
                state = state.copy(isPlaying = isPlaying)
                if (isPlaying) audioFocusManager?.requestFocus()
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

    // P09: Audio focus — yields to phone calls, notifications, other media apps.
    // Initialized in init block after player is fully constructed.
    private lateinit var audioFocusManager: AudioFocusManager

    init {
        // Wire player into MediaSessionService for lock-screen / background playback.
        MoodifyMediaSessionService.setPlayer(player)
        // Audio focus callbacks must be set AFTER player is constructed
        audioFocusManager = AudioFocusManager(context).apply {
            onAudioFocusLost = { player.pause() }
            onAudioFocusLostTransient = { player.pause() }
            onAudioFocusLostTransientCanDuck = { /* v0.1: no ducking; just pause */ }
        }
        try {
            context.startService(Intent(context, MoodifyMediaSessionService::class.java))
        } catch (_: Exception) {
            // Foreground service may fail in some test environments; non-fatal.
        }
    }

    // -----------------------------------------------------------------------
    // Original API (kept for backward compat with existing UI)
    // -----------------------------------------------------------------------

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

    // -----------------------------------------------------------------------
    // P09: LocalTrack playback (original offline + reconstructed result)
    // -----------------------------------------------------------------------

    /**
     * Play a local track's ORIGINAL audio from its content URI.
     * Works fully OFFLINE — no network needed.
     */
    fun playLocalOriginal(track: LocalTrack) {
        val queue = listOf(trackToTrack(track))
        play(queue, 0)
    }

    /**
     * Play a RECONSTRUCTED result from an authenticated URL.
     *
     * @param track the source LocalTrack
     * @param playbackUrl short-lived authenticated URL from P08 API.
     *                   MUST NOT be cached or logged long-term.
     */
    fun playReconstructedResult(track: LocalTrack, playbackUrl: String) {
        val reconstructedTrack = Track(
            id = "recon-${track.localTrackId}",
            title = "${track.displayName} · Moodify",
            creatorId = "moodify",
            creatorHandle = "Moodify",
            status = "reconstructed",
            primaryLanguage = null,
            durationMs = if (track.durationMs > 0) track.durationMs else null,
            publishedAt = null,
            audioAssetKey = null,
            externalUri = playbackUrl,
        )
        play(listOf(reconstructedTrack), 0)
    }

    /**
     * Play either the original or reconstructed version depending on status.
     * This is the primary P09 one-tap method.
     */
    fun playBestAvailable(track: LocalTrack, resultPlaybackUrl: String? = null) {
        when (track.reconstructionStatus) {
            ReconstructionStatus.READY -> {
                if (resultPlaybackUrl != null) {
                    playReconstructedResult(track, resultPlaybackUrl)
                } else {
                    playLocalOriginal(track)
                }
            }
            ReconstructionStatus.SOURCE_PRESERVED -> {
                // Cloud decided original is best — play it
                playLocalOriginal(track)
            }
            else -> {
                // Default: always fall back to original
                playLocalOriginal(track)
            }
        }
    }

    // -----------------------------------------------------------------------
    // Core controls (unchanged)
    // -----------------------------------------------------------------------

    fun toggle() {
        if (state.current == null) return
        if (player.isPlaying) {
            player.pause()
            audioFocusManager.abandonFocus()
        } else {
            player.play()
        }
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

    /** Delivery-first: authorized playback URI from the delivery contract; legacy CDN as fallback. */
    private fun resolvePlaybackUri(track: Track): Uri? {
        if (track.externalUri != null) return Uri.parse(track.externalUri)
        val deliveryClient = delivery
        if (track.audioAssetKey != null && deliveryClient != null) {
            return try {
                Uri.parse(deliveryClient.resolve(track.id).playbackUri)
            } catch (_: DeliveryException) {
                Uri.parse("https://rongjinwenchuan.xyz/audio/${track.audioAssetKey}")
            }
        }
        return track.audioAssetKey?.let { Uri.parse("https://rongjinwenchuan.xyz/audio/$it") }
    }

    private fun load(track: Track) {
        val uri = resolvePlaybackUri(track) ?: run {
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

    /** Convert a LocalTrack to the internal Track format for the queue. */
    private fun trackToTrack(local: LocalTrack): Track = Track(
        id = local.localTrackId,
        title = local.displayName,
        creatorId = "local",
        creatorHandle = null,
        status = "local",
        primaryLanguage = null,
        durationMs = if (local.durationMs > 0) local.durationMs else null,
        publishedAt = null,
        audioAssetKey = null,
        externalUri = local.contentUri.toString(),
    )

    fun release() {
        audioFocusManager.abandonFocus()
        MoodifyMediaSessionService.setPlayer(null)
        player.release()
    }
}
