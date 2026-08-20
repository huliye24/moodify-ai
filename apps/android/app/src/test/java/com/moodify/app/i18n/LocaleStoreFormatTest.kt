package com.moodify.app.i18n

import com.moodify.app.data.LocaleKit
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/**
 * Pure-format tests for the persisted locale representation used by LocaleStore.
 * The framework-bound half (AppCompatDelegate state) is covered by the
 * instrumented LanguageSwitchTest.
 */
class LocaleStoreFormatTest {

    @Test
    fun parseStoredTagsPicksFirstTagOfList() {
        assertEquals("zh-CN", LocaleKit.parseStoredTags("zh-CN"))
        assertEquals("zh-CN", LocaleKit.parseStoredTags("zh-CN,en-US"))
    }

    @Test
    fun parseStoredTagsReturnsNullWhenFollowingSystem() {
        assertNull(LocaleKit.parseStoredTags(""))
        assertNull(LocaleKit.parseStoredTags(null))
        assertNull(LocaleKit.parseStoredTags("   "))
    }

    @Test
    fun storedTagSurvivesRoundTripThroughNormalize() {
        val stored = LocaleKit.parseStoredTags("ja-JP")
        assertEquals("ja-JP", LocaleKit.normalize(stored))
    }

    @Test
    fun resolveUsesExplicitChoiceOverSystem() {
        assertEquals("fr-FR", LocaleKit.resolve("fr-FR", "zh-CN"))
        assertEquals("zh-TW", LocaleKit.resolve("zh-TW", "en-US"))
    }

    @Test
    fun resolveFallsBackToSystemWhenExplicitChoiceMissing() {
        assertEquals("zh-TW", LocaleKit.resolve(null, "zh-HK"))
        assertEquals("en-US", LocaleKit.resolve(null, "de-DE"))
    }
}
