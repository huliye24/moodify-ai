package com.moodify.music

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.OpenableColumns
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import com.moodify.music.data.BffClient
import com.moodify.music.player.PlaybackController
import com.moodify.music.ui.MoodifyMusicApp
import com.moodify.music.ui.MoodifyMusicTheme

data class ExternalAudio(val uri: Uri, val displayName: String)

class MainActivity : ComponentActivity() {
    private val client = BffClient()
    private lateinit var playback: PlaybackController
    private var externalAudio by mutableStateOf<List<ExternalAudio>>(emptyList())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        playback = PlaybackController(this)
        externalAudio = readExternalAudio(intent)
        setContent {
            MoodifyMusicTheme {
                MoodifyMusicApp(
                    client = client,
                    playback = playback,
                    externalAudio = externalAudio,
                    onExternalAudioConsumed = { externalAudio = emptyList() },
                )
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        externalAudio = readExternalAudio(intent)
    }

    private fun readExternalAudio(intent: Intent?): List<ExternalAudio> {
        if (intent == null) return emptyList()
        val uris = buildList {
            when (intent.action) {
                Intent.ACTION_VIEW -> intent.data?.let(::add)
                Intent.ACTION_SEND -> intent.streamUri()?.let(::add)
                Intent.ACTION_SEND_MULTIPLE -> addAll(intent.streamUris())
            }
            intent.clipData?.let { clip ->
                repeat(clip.itemCount) { index -> clip.getItemAt(index).uri?.let(::add) }
            }
        }.distinct()

        return uris.mapNotNull { uri ->
            if (uri.scheme != "content" && uri.scheme != "file") return@mapNotNull null
            persistReadPermission(uri, intent.flags)
            ExternalAudio(uri, displayName(uri))
        }
    }

    private fun persistReadPermission(uri: Uri, flags: Int) {
        if (uri.scheme != "content") return
        val requested = flags and (Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION)
        if (requested and Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION == 0) return
        runCatching { contentResolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION) }
    }

    private fun displayName(uri: Uri): String {
        if (uri.scheme == "content") {
            runCatching {
                contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { cursor ->
                    if (cursor.moveToFirst()) cursor.getString(0)?.takeIf(String::isNotBlank)?.let { return it }
                }
            }
        }
        return uri.lastPathSegment?.substringAfterLast('/')?.takeIf(String::isNotBlank) ?: "外部音频"
    }

    @Suppress("DEPRECATION")
    private fun Intent.streamUri(): Uri? = if (Build.VERSION.SDK_INT >= 33) {
        getParcelableExtra(Intent.EXTRA_STREAM, Uri::class.java)
    } else {
        getParcelableExtra(Intent.EXTRA_STREAM)
    }

    @Suppress("DEPRECATION")
    private fun Intent.streamUris(): List<Uri> = if (Build.VERSION.SDK_INT >= 33) {
        getParcelableArrayListExtra(Intent.EXTRA_STREAM, Uri::class.java).orEmpty()
    } else {
        getParcelableArrayListExtra<Uri>(Intent.EXTRA_STREAM).orEmpty()
    }

    override fun onDestroy() {
        playback.release()
        super.onDestroy()
    }
}
