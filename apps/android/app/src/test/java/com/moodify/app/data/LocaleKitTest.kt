package com.moodify.app.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/**
 * Ported from the DSK-MFY-I18N-001 reference implementation's normalizeLocale
 * alias contract and English fallback behavior.
 */
class LocaleKitTest {

    @Test
    fun simplifiedChineseAliasesResolveToZhCN() {
        assertEquals("zh-CN", LocaleKit.normalize("zh-Hans"))
        assertEquals("zh-CN", LocaleKit.normalize("zh-CN"))
        assertEquals("zh-CN", LocaleKit.normalize("zh-SG"))
    }

    @Test
    fun traditionalChineseAliasesResolveToZhTW() {
        assertEquals("zh-TW", LocaleKit.normalize("zh-Hant"))
        assertEquals("zh-TW", LocaleKit.normalize("zh-TW"))
        assertEquals("zh-TW", LocaleKit.normalize("zh-HK"))
        assertEquals("zh-TW", LocaleKit.normalize("zh-MO"))
    }

    @Test
    fun englishJapaneseKoreanFrenchAliasesResolve() {
        assertEquals("en-US", LocaleKit.normalize("en"))
        assertEquals("en-US", LocaleKit.normalize("en-GB"))
        assertEquals("ja-JP", LocaleKit.normalize("ja"))
        assertEquals("ko-KR", LocaleKit.normalize("ko"))
        assertEquals("fr-FR", LocaleKit.normalize("fr"))
        assertEquals("fr-FR", LocaleKit.normalize("fr-CA"))
    }

    @Test
    fun normalizationIsCaseInsensitiveAndHandlesUnderscores() {
        assertEquals("zh-CN", LocaleKit.normalize("ZH_cn"))
        assertEquals("zh-TW", LocaleKit.normalize("ZH-HK"))
        assertEquals("en-US", LocaleKit.normalize("EN-us"))
    }

    @Test
    fun scriptVariantTagsResolveByPrefix() {
        assertEquals("zh-CN", LocaleKit.normalize("zh-Hans-CN"))
        assertEquals("zh-TW", LocaleKit.normalize("zh-Hant-TW"))
    }

    @Test
    fun unsupportedLocalesFallBackToEnglish() {
        assertEquals("en-US", LocaleKit.normalize("de-DE"))
        assertEquals("en-US", LocaleKit.normalize("es"))
        assertEquals("en-US", LocaleKit.normalize("xx-YY"))
        assertEquals("en-US", LocaleKit.normalize(null))
        assertEquals("en-US", LocaleKit.normalize(""))
    }

    @Test
    fun resolvePrefersExplicitChoiceOverSystem() {
        assertEquals("zh-TW", LocaleKit.resolve("zh-TW", "en-US"))
        assertEquals("fr-FR", LocaleKit.resolve("fr-FR", "zh-CN"))
    }

    @Test
    fun resolveFallsBackToSystemWhenNothingStored() {
        assertEquals("zh-TW", LocaleKit.resolve(null, "zh-HK"))
        assertEquals("zh-CN", LocaleKit.resolve("", "zh-CN"))
        assertEquals("ja-JP", LocaleKit.resolve(null, "ja-JP"))
    }

    @Test
    fun resolveDefaultsToEnglishWhenUnsupported() {
        assertEquals("en-US", LocaleKit.resolve(null, "de-DE"))
        assertEquals("en-US", LocaleKit.resolve("xx-YY", "fr-FR"))
    }

    @Test
    fun parseStoredTagsPicksFirstTag() {
        assertEquals("zh-CN", LocaleKit.parseStoredTags("zh-CN"))
        assertEquals("zh-CN", LocaleKit.parseStoredTags("zh-CN,en-US"))
        assertEquals("en-US", LocaleKit.parseStoredTags("en-US,zh-TW"))
    }

    @Test
    fun parseStoredTagsHandlesBlankInput() {
        assertNull(LocaleKit.parseStoredTags(null))
        assertNull(LocaleKit.parseStoredTags(""))
        assertNull(LocaleKit.parseStoredTags("   "))
        assertNull(LocaleKit.parseStoredTags(","))
    }

    @Test
    fun supportedListHasExactlySixLanguages() {
        assertEquals(6, LocaleKit.SUPPORTED.size)
        assertEquals("zh-CN", LocaleKit.SUPPORTED[0].code)
        assertEquals("fr-FR", LocaleKit.SUPPORTED[5].code)
    }
}
