package com.moodify.music.player

import android.app.PendingIntent
import android.content.ComponentName
import android.content.Intent
import android.os.Build
import androidx.annotation.OptIn
import androidx.media3.common.Player
import androidx.media3.common.util.UnstableApi
import androidx.media3.session.MediaSession
import androidx.media3.session.MediaSessionService

/**
 * P09 Moodify Media Session Service — enables:
 *   - Background playback (process survives when UI is backgrounded)
 *   - Lock-screen controls
 *   - Bluetooth headset / wired headset button controls (play/pause/next/prev)
 *
 * This service is declared in AndroidManifest.xml and must be started
 * before or at the same time as the first playback begins.
 *
 * Lifecycle: startService → create session → bind ExoPlayer → update state → stopSelf.
 */
class MoodifyMediaSessionService : MediaSessionService() {

    private var mediaSession: MediaSession? = null

    // The player is set from PlaybackController once it's created.
    // We keep a static reference so the service can access it.
    companion object {
        var playerRef: Player? = null
            private set

        fun setPlayer(player: Player?) {
            playerRef = player
        }
    }

    @OptIn(UnstableApi::class)
    override fun onCreate() {
        super.onCreate()
        val session = MediaSession.Builder(this, playerRef!!)
            .setCallback(MoodifySessionCallback())
            .setSessionActivity(sessionActivityPendingIntent())
            .build()
        mediaSession = session
    }

    override fun onGetSession(controllerInfo: MediaSession.ControllerInfo): MediaSession? =
        mediaSession

    override fun onDestroy() {
        mediaSession?.release()
        mediaSession = null
        super.onDestroy()
    }

    /**
     * Tap on lock-screen notification opens MainActivity.
     */
    private fun sessionActivityPendingIntent(): PendingIntent {
        val intent = packageManager.getLaunchIntentForPackage(packageName)?.apply {
            action = Intent.ACTION_MAIN
            addCategory(Intent.CATEGORY_LAUNCHER)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        } ?: return PendingIntent.getActivity(this, 0, Intent(),
            if (Build.VERSION.SDK_INT >= 23) PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            else PendingIntent.FLAG_UPDATE_CURRENT)

        @Suppress("DEPRECATION")
        return PendingIntent.getActivity(this, 0, intent,
            if (Build.VERSION.SDK_INT >= 23) PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            else PendingIntent.FLAG_UPDATE_CURRENT)
    }
}

/**
 * Handles media button events (Bluetooth headset, lock screen).
 */
@OptIn(UnstableApi::class)
private class MoodifySessionCallback : MediaSession.Callback {
    // Default implementations in MediaSession.Callback handle play/pause/seek/next/prev
    // by delegating to the bound Player.  We only override for custom behavior.
}
