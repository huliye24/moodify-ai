package com.moodify.app

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import com.moodify.app.data.LocaleKit
import com.moodify.app.ui.MoodifyApp
import com.moodify.app.ui.theme.MoodifyTheme
import java.util.Locale

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ensureInitialLocale()
        enableEdgeToEdge()
        val deepLinkCode = parseDeepLink(intent?.dataString)
        setContent {
            MoodifyTheme {
                MoodifyApp(pendingCwcCode = deepLinkCode)
            }
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

    /** Deep link reserved: moodify://cwc/CWC-XZ7M-42KP → gift landing page. */
    private fun parseDeepLink(data: String?): String? {
        if (data == null || !data.startsWith("moodify://cwc/")) return null
        return data.removePrefix("moodify://cwc/")
    }
}
