package com.moodify.app.i18n

import android.content.Context
import android.content.Intent
import android.os.PowerManager
import androidx.appcompat.app.AppCompatDelegate
import androidx.compose.ui.test.junit4.createEmptyComposeRule
import androidx.compose.ui.test.onAllNodesWithContentDescription
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onFirst
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.core.os.LocaleListCompat
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.core.app.ActivityScenario
import com.moodify.app.MainActivity
import org.junit.After
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/**
 * DSK-MFY-I18N-001 acceptance on device:
 * - selection moves AppCompatDelegate's per-app language and the current screen
 *   re-renders in the new language (recreate);
 * - the persisted storage record contains the choice (survives restarts).
 *
 * Drives the real MainActivity (AppCompatActivity) because appcompat's locale
 * persistence is triggered from its lifecycle.
 */
@RunWith(AndroidJUnit4::class)
class LanguageSwitchTest {

    @get:Rule
    val rule = createEmptyComposeRule()

    private val appContext: Context
        get() = InstrumentationRegistry.getInstrumentation().targetContext

    private var scenario: ActivityScenario<MainActivity>? = null
    private var wakeLock: PowerManager.WakeLock? = null

    @Before
    fun setup() {
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.getEmptyLocaleList())
        val pm = appContext.getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK or PowerManager.ACQUIRE_CAUSES_WAKEUP, "language-test").apply {
            acquire(10 * 60 * 1000L)
        }
        scenario = ActivityScenario.launch(MainActivity::class.java)
        rule.waitForIdle()
    }

    @After
    fun teardown() {
        try {
            scenario?.close()
        } catch (_: Exception) {
        }
        wakeLock?.let { if (it.isHeld) it.release() }
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.getEmptyLocaleList())
    }

    @Test
    fun selectingJapaneseUpdatesScreenImmediately() {
        openSettings()
        rule.onNodeWithText("语言").performScrollTo().performClick()
        rule.onNodeWithText("日本語").performClick()

        rule.waitUntil(timeoutMillis = 15_000) {
            AppCompatDelegate.getApplicationLocales().toLanguageTags().contains("ja")
        }
        // Recreate replaces the compose tree; assert on the new-tree text.
        rule.waitUntil(timeoutMillis = 15_000) {
            rule.onAllNodesWithText("設定").fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun selectionIsPersistedToDisk() {
        openSettings()
        rule.onNodeWithText("语言").performScrollTo().performClick()
        rule.onNodeWithText("한국어").performClick()

        rule.waitUntil(timeoutMillis = 15_000) {
            AppCompatDelegate.getApplicationLocales().toLanguageTags().contains("ko")
        }
        val record = File(
            appContext.filesDir,
            "androidx.appcompat.app.AppCompatDelegate.application_locales_record_file",
        )
        rule.waitUntil(timeoutMillis = 15_000) {
            record.exists() && record.readText().contains("ko-KR")
        }
        assertTrue(record.readText().contains("ko-KR"))
    }

    private fun openSettings() {
        rule.waitUntil(timeoutMillis = 10_000) {
            rule.onAllNodesWithContentDescription("打开菜单").fetchSemanticsNodes().isNotEmpty()
        }
        rule.onNodeWithContentDescription("打开菜单").performClick()
        rule.waitUntil(timeoutMillis = 10_000) {
            rule.onAllNodesWithText("设置").fetchSemanticsNodes().isNotEmpty()
        }
        rule.onAllNodesWithText("设置").onFirst().performClick()
        rule.waitUntil(timeoutMillis = 10_000) {
            rule.onAllNodesWithText("偏好设置").fetchSemanticsNodes().isNotEmpty()
        }
    }
}
