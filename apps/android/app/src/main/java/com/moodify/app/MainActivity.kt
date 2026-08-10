package com.moodify.app

import android.os.Bundle
import androidx.activity.compose.setContent
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
        setContent {
            MoodifyTheme {
                MoodifyApp()
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
}
