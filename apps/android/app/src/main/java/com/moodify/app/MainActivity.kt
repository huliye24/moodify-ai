package com.moodify.app

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.layout.Box
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.core.os.LocaleListCompat
import com.moodify.app.data.LocaleKit
import com.moodify.app.ui.LaunchScreen
import com.moodify.app.ui.MoodifyApp
import com.moodify.app.ui.theme.MoodifyTheme
import kotlinx.coroutines.delay
import java.util.Locale

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ensureInitialLocale()
        setContent {
            MoodifyTheme {
                var launching by remember { mutableStateOf(true) }
                LaunchedEffect(Unit) {
                    delay(300)
                    launching = false
                    requestNotificationPermissionIfNeeded()
                }
                Box {
                    // Initialize playback and refresh the cloud catalogue behind
                    // the branded launch layer, avoiding a second loading phase.
                    MoodifyApp()
                    AnimatedVisibility(
                        visible = launching,
                        exit = fadeOut(tween(140)),
                    ) { LaunchScreen() }
                }
            }
        }
    }

    /** Android 13+ requires runtime consent for the media notification. */
    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33 &&
            checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(arrayOf(Manifest.permission.POST_NOTIFICATIONS), 1001)
        }
    }

    /**
     * First launch follows the system language, resolved through LocaleKit's alias table
     * (e.g. zh-HK -> zh-TW) so that resource fallback cannot silently land on English.
     * A user's explicit choice in Settings overrides this because it persists.
     */
    private fun ensureInitialLocale() {
        if (!AppCompatDelegate.getApplicationLocales().isEmpty) return
        val normalized = LocaleKit.normalize(Locale.getDefault().toLanguageTag())
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(normalized))
    }
}
