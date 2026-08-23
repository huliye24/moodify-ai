package com.moodify.music.player

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager
import android.os.Build
import androidx.annotation.RequiresApi

/**
 * P09 Audio Focus Manager — handles Android audio focus correctly.
 *
 * Ensures Moodify yields to phone calls, notifications, and other media apps.
 * Follows Android Media3 / AudioManager best practices.
 */
class AudioFocusManager(private val context: Context) {

    var onAudioFocusGained: (() -> Unit)? = null
    var onAudioFocusLost: (() -> Unit)? = null
    var onAudioFocusLostTransient: (() -> Unit)? = null   // pause, auto-resume later
    var onAudioFocusLostTransientCanDuck: (() -> Unit)? = null  // lower volume

    private val am = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager

    // API 26+ focus request (replaces deprecated requestAudioFocus)
    @RequiresApi(Build.VERSION_CODES.O)
    private var focusRequest: AudioFocusRequest? = null

    /**
     * Request audio focus for music playback.
     * @return true if focus was granted or will be granted.
     */
    fun requestFocus(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            requestFocusO()
        } else {
            requestFocusLegacy()
        }
    }

    @Suppress("DEPRECATION")
    private fun requestFocusLegacy(): Boolean {
        val result = am.requestAudioFocus(
            focusListener,
            AudioManager.STREAM_MUSIC,
            AudioManager.AUDIOFOCUS_GAIN,
        )
        return result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED
    }

    @RequiresApi(Build.VERSION_CODES.O)
    private fun requestFocusO(): Boolean {
        val request = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN)
            .setOnAudioFocusChangeListener(focusListener)
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_MEDIA)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build()
            )
            .build()
        focusRequest = request
        val result = am.requestAudioFocus(request)
        return result == AudioManager.AUDIOFOCUS_REQUEST_GRANTED
    }

    /**
     * Abandon audio focus (e.g. when playback stops completely).
     */
    fun abandonFocus() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            focusRequest?.let { am.abandonAudioFocusRequest(it) }
            focusRequest = null
        } else {
            @Suppress("DEPRECATION") { am.abandonAudioFocus(focusListener) }
        }
    }

    private val focusListener = AudioManager.OnAudioFocusChangeListener { focusChange ->
        when (focusChange) {
            AudioManager.AUDIOFOCUS_GAIN -> onAudioFocusGained?.invoke()
            AudioManager.AUDIOFOCUS_LOSS -> {
                onAudioFocusLost?.invoke()
            }
            AudioManager.AUDIOFOCUS_LOSS_TRANSIENT -> {
                onAudioFocusLostTransient?.invoke()
            }
            AudioManager.AUDIOFOCUS_LOSS_TRANSIENT_CAN_DUCK -> {
                onAudioFocusLostTransientCanDuck?.invoke()
            }
        }
    }

    companion object {
        const val TAG = "AudioFocusManager"
    }
}
