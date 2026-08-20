package com.moodify.app.data

/**
 * Pure-Kotlin locale normalization and metadata, ported from the
 * DSK-MFY-I18N-001 reference implementation. No android imports so it is JVM-testable.
 */
object LocaleKit {

    data class LocaleMeta(
        val code: String,
        val nativeName: String,
        val englishName: String,
    )

    const val DEFAULT: String = "en-US"

    val SUPPORTED: List<LocaleMeta> = listOf(
        LocaleMeta("zh-CN", "中文（简体）", "Chinese, Simplified"),
        LocaleMeta("zh-TW", "中文（繁體）", "Chinese, Traditional"),
        LocaleMeta("en-US", "English", "English"),
        LocaleMeta("ja-JP", "日本語", "Japanese"),
        LocaleMeta("ko-KR", "한국어", "Korean"),
        LocaleMeta("fr-FR", "Français", "French"),
    )

    private val EXACT_ALIASES: Map<String, String> = mapOf(
        "zh-hans" to "zh-CN",
        "zh-cn" to "zh-CN",
        "zh-sg" to "zh-CN",
        "zh-hant" to "zh-TW",
        "zh-tw" to "zh-TW",
        "zh-hk" to "zh-TW",
        "zh-mo" to "zh-TW",
        "en" to "en-US",
        "en-gb" to "en-US",
        "ja" to "ja-JP",
        "ko" to "ko-KR",
        "fr" to "fr-FR",
        "fr-ca" to "fr-FR",
    )

    /** Maps an IETF tag (e.g. from Locale.toLanguageTag) to a supported code, defaulting to en-US. */
    fun normalize(tag: String?): String {
        if (tag.isNullOrBlank()) return DEFAULT
        val key = tag.trim().replace('_', '-').lowercase()
        EXACT_ALIASES[key]?.let { return it }
        // Loose matching for script/region variants such as "zh-Hans-CN" or "zh-Hant-TW".
        if (key.startsWith("zh-hans")) return "zh-CN"
        if (key.startsWith("zh-hant")) return "zh-TW"
        // Full tags like "fr-FR" or "ko-KR" fall back to their language part.
        return EXACT_ALIASES[key.substringBefore('-')] ?: DEFAULT
    }

    fun metaFor(code: String): LocaleMeta =
        SUPPORTED.firstOrNull { it.code == code } ?: SUPPORTED.first { it.code == DEFAULT }

    fun supportedTags(): List<String> = SUPPORTED.map { it.code }

    /** Resolves the display language: an explicit stored choice wins, otherwise the system locale. */
    fun resolve(storedTag: String?, systemTag: String?): String =
        if (storedTag.isNullOrBlank()) normalize(systemTag) else normalize(storedTag)

    /** Parses LocaleListCompat.toLanguageTags() output ("zh-CN,en-US") into the first tag; null if blank. */
    fun parseStoredTags(tags: String?): String? {
        if (tags.isNullOrBlank()) return null
        return tags.split(",").firstOrNull { it.isNotBlank() }?.trim()
    }
}
