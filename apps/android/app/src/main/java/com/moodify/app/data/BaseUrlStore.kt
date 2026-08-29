package com.moodify.app.data

import android.content.Context
import com.moodify.app.BuildConfig

/**
 * Base URL policy (ANDROID-003 Stage B/C):
 *  - debug builds: user may enter a LAN address like http://192.168.1.5:8000
 *  - release builds: only localhost (USB `adb reverse tcp:8000 tcp:8000`)
 * The default is the USB reverse address; the release build rejects any
 * non-local plaintext URL at entry time.
 */
object BaseUrlPolicy {
    const val DEFAULT = "http://127.0.0.1:8000"
    private val LOCAL_HOST = setOf("127.0.0.1", "localhost")

    fun sanitize(raw: String, allowDebug: Boolean): String {
        val trimmed = raw.trim().trimEnd('/')
        if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
            return trimmed // invalid; caller validates
        }
        val host = trimmed.removePrefix("http://").removePrefix("https://")
            .substringBefore(":").substringBefore("/")
        if (host in LOCAL_HOST) return trimmed
        if (allowDebug) {
            // LAN plaintext only in debug builds; never in release
            if (trimmed.startsWith("http://")) return trimmed
        }
        return DEFAULT
    }
}

class BaseUrlStore(context: Context) {
    private val prefs = context.getSharedPreferences("moodify_connection", Context.MODE_PRIVATE)

    var baseUrl: String
        get() = prefs.getString("base_url", null)?.takeIf { it.isNotBlank() } ?: BaseUrlPolicy.DEFAULT
        set(value) {
            prefs.edit().putString("base_url", BaseUrlPolicy.sanitize(value, BuildConfig.DEBUG)).apply()
        }
}
