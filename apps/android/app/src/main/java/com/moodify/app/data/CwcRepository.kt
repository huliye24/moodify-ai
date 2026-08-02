package com.moodify.app.data

import android.content.Context
import com.moodify.app.model.CwcBenefits
import com.moodify.app.model.CwcStatus
import com.moodify.app.model.CwcValidationState
import com.moodify.app.model.CreatorPass
import kotlinx.coroutines.delay

/**
 * Local demo CWC repository. Validation rules are intentionally client-side
 * for this milestone only — the production build MUST validate and redeem
 * atomically on the server to prevent duplicate activation.
 */
class CwcRepository(context: Context) {

    // Lazy so pure-logic methods (normalize/validate) stay JVM-testable without Android.
    private val prefs by lazy { context.getSharedPreferences("moodify_cwc", Context.MODE_PRIVATE) }

    val demoPasses = listOf(
        CreatorPass("CWC-XZ7M-42KP", "泫榛", "2027-12-31", CwcStatus.AVAILABLE),
        CreatorPass("CWC-USED-0001", "泫榛", "2027-12-31", CwcStatus.REDEEMED),
        CreatorPass("CWC-OLD0-0001", "泫榛", "2026-01-01", CwcStatus.EXPIRED),
    )

    /** CWC codes are 3-4-4: e.g. CWC-XZ7M-42KP. Works for both raw and formatted input. */
    fun normalize(code: String): String {
        val cleaned = code.trim().uppercase().filter { it.isLetterOrDigit() }
        return when {
            cleaned.length <= 3 -> cleaned
            cleaned.length <= 7 -> "${cleaned.take(3)}-${cleaned.drop(3)}"
            else -> "${cleaned.take(3)}-${cleaned.substring(3, 7)}-${cleaned.drop(7)}"
        }
    }

    /** Demo validation with a short artificial delay so the loading state is visible. */
    suspend fun validate(code: String): CwcValidationState {
        delay(600)
        val normalized = normalize(code)
        if (normalized.length < 8) return CwcValidationState.Error("请输入完整的 CWC 通行码")
        val pass = demoPasses.find { it.code == normalized }
        return when (pass?.status) {
            CwcStatus.AVAILABLE -> CwcValidationState.Valid(pass)
            CwcStatus.REDEEMED -> CwcValidationState.Error("该通行码已被使用")
            CwcStatus.EXPIRED -> CwcValidationState.Error("该通行码已过期")
            else -> CwcValidationState.Error("该通行码不存在")
        }
    }

    fun statusLabel(pass: CreatorPass): String = when (pass.status) {
        CwcStatus.AVAILABLE -> "可使用"
        CwcStatus.REDEEMED -> "已激活"
        CwcStatus.EXPIRED -> "已过期"
        CwcStatus.INVALID -> "无效"
    }

    fun activate(code: String): CwcBenefits {
        prefs.edit()
            .putString("activated_code", normalize(code))
            .putBoolean("cwc_activated", true)
            .putLong("activated_at", System.currentTimeMillis())
            .apply()
        return CwcBenefits()
    }

    fun isActivated(): Boolean = prefs.getBoolean("cwc_activated", false)

    fun activatedCode(): String? = prefs.getString("activated_code", null)

    fun resetDemoSession() {
        prefs.edit().remove("cwc_activated").remove("activated_code").remove("activated_at").apply()
    }
}
