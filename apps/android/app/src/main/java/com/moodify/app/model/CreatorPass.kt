package com.moodify.app.model

enum class CwcStatus { AVAILABLE, REDEEMED, EXPIRED, INVALID }

data class CreatorPass(
    val code: String,
    val inviterName: String,
    val expiresAt: String,
    val status: CwcStatus,
)

/** Benefits granted after a successful CWC activation (front-end demo model). */
data class CwcBenefits(
    val freeFirstWorkOnboarding: Boolean = true,
    val basicCopyrightArchive: Boolean = true,
    val creatorProfileEnabled: Boolean = true,
    val standardProcessingCouponPercent: Int = 20,
)

enum class AuthMode { Login, Onboarding }

sealed interface CwcValidationState {
    data object Idle : CwcValidationState
    data object Loading : CwcValidationState
    data class Valid(val pass: CreatorPass) : CwcValidationState
    data class Error(val message: String) : CwcValidationState
}
