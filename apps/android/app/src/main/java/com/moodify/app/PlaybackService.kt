package com.moodify.app

import androidx.media3.session.MediaSession
import androidx.media3.session.MediaSessionService
import com.moodify.app.data.PlaybackManager

/**
 * Foreground media service: drives the notification bar / lock-screen controls
 * and keeps playback alive when the UI is not visible. The player and session
 * live in [PlaybackManager] so UI and service share one instance.
 */
class PlaybackService : MediaSessionService() {

    private var session: MediaSession? = null

    override fun onCreate() {
        super.onCreate()
        PlaybackManager.init(this)
        session = PlaybackManager.mediaSession
        session?.let { addSession(it) }
    }

    override fun onGetSession(controllerInfo: MediaSession.ControllerInfo): MediaSession? = session

    override fun onDestroy() {
        session?.let { removeSession(it) }
        session = null
        super.onDestroy()
    }
}
