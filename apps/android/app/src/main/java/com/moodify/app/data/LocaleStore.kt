package com.moodify.app.data

import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat

/**
 * Facade over AppCompatDelegate's per-app language state, which is the single source
 * of truth and persists the user's explicit choice across restarts.
 */
object LocaleStore {

    fun isExplicit(): Boolean = !AppCompatDelegate.getApplicationLocales().isEmpty

    /** The first tag of the stored locale list, or null when following the system. */
    fun currentTag(): String? = LocaleKit.parseStoredTags(AppCompatDelegate.getApplicationLocales().toLanguageTags())

    fun set(tag: String) {
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tag))
    }

    fun resetToSystem() {
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.getEmptyLocaleList())
    }
}
