package com.moodify.music.data

import kotlinx.serialization.Serializable

/**
 * P11 Reconstruction Commerce — Android Display DTOs
 *
 * CRITICAL: These are READ-ONLY display objects.
 * Android MUST NEVER:
 *   - Fabricate prices or amounts
 *   - Self-declare payment status
 *   - Modify billing decisions
 *   - Cache payment secrets
 *
 * Authority:
 *   Price truth   = server pricing policy
 *   Payment truth = verified provider / server
 *   Android is NEVER payment authority
 */

// ---------------------------------------------------------------------------
// Quote Display
// ---------------------------------------------------------------------------

@Serializable
data class QuoteDisplay(
    val quoteId: String = "",
    val currency: String = "CNY",
    val unitAmountMinor: Int = 0,       // in fen (分)
    val quantity: Int = 1,
    val totalAmountMinor: Int = 0,
    val pricingVersion: String = "",
    val reconstructionVersion: String = "",
    val expiresAtMs: Long = 0,          // epoch millis
    val createdAtMs: Long = 0,
) {
    /** Human-readable total, e.g. "¥1.00" */
    val formattedTotal: String get() = formatCny(totalAmountMinor)

    val isExpired: Boolean get() =
        if (expiresAtMs <= 0) false else System.currentTimeMillis() > expiresAtMs

    companion object {
        fun formatCny(amountMinor: Int): String {
            val yuan = amountMinor / 100.0
            return "¥%.2f".format(yuan)
        }
    }
}

// ---------------------------------------------------------------------------
// Order Status (mirrors server OrderStatus but as sealed interface for Compose)
// ---------------------------------------------------------------------------

sealed class OrderDisplayStatus(val value: String) {
    data object Created : OrderDisplayStatus("CREATED")
    data object PaymentPending : OrderDisplayStatus("PAYMENT_PENDING")
    data object Authorized : OrderDisplayStatus("AUTHORIZED")
    data object JobCreated : OrderDisplayStatus("JOB_CREATED")
    data object Processing : OrderDisplayStatus("PROCESSING")
    data object SettlementPending : OrderDisplayStatus("SETTLEMENT_PENDING")
    data object Paid : OrderDisplayStatus("PAID")
    data object NoCharge : OrderDisplayStatus("NO_CHARGE")
    data object RefundPending : OrderDisplayStatus("REFUND_PENDING")
    data object Refunded : OrderDisplayStatus("REFUNDED")
    data object Failed : OrderDisplayStatus("FAILED")
    data object Cancelled : OrderDisplayStatus("CANCELLED")

    /** User-facing label */
    val label: String
        get() = when (this) {
            Created -> "已创建"
            PaymentPending -> "待支付"
            Authorized -> "已授权"
            JobCreated -> "任务已创建"
            Processing -> "处理中"
            SettlementPending -> "待结算"
            Paid -> "已支付"
            NoCharge -> "免费"
            RefundPending -> "退款中"
            Refunded -> "已退款"
            Failed -> "失败"
            Cancelled -> "已取消"
        }

    /** Whether this status indicates an active/in-progress order */
    val isActive: Boolean
        get() = this in setOf(
            Created, PaymentPending, Authorized, JobCreated,
            Processing, SettlementPending,
        )

    companion object {
        fun fromValue(value: String): OrderDisplayStatus = when (value) {
            "CREATED" -> Created
            "PAYMENT_PENDING" -> PaymentPending
            "AUTHORIZED" -> Authorized
            "JOB_CREATED" -> JobCreated
            "PROCESSING" -> Processing
            "SETTLEMENT_PENDING" -> SettlementPending
            "PAID" -> Paid
            "NO_CHARGE" -> NoCharge
            "REFUND_PENDING" -> RefundPending
            "REFUNDED" -> Refunded
            "FAILED" -> Failed
            "CANCELLED" -> Cancelled
            else -> Created // default fallback
        }
    }
}

// ---------------------------------------------------------------------------
// Order Display
// ---------------------------------------------------------------------------

@Serializable
data class OrderDisplay(
    val orderId: String = "",
    val quoteId: String = "",
    val jobId: String = "",
    val sourceSha256: String = "",
    val currency: String = "CNY",
    val amountMinor: Int = 0,
    val status: OrderDisplayStatus = OrderDisplayStatus.Created,
    val paymentProvider: String = "",
    val createdAtMs: Long = 0,
    val settledAtMs: Long = 0,
    val failureReason: String = "",
    val outcome: String = "",           // SUCCEEDED, SOURCE_WINS, etc.
    val billingDecision: String = "",   // CHARGE, NO_CHARGE, NO_CHARGE_YET
) {
    val formattedAmount: String get() = QuoteDisplay.formatCny(amountMinor)

    /** User-friendly outcome description */
    val outcomeLabel: String
        get() = when (outcome) {
            "SUCCEEDED" -> "重建成功"
            "SOURCE_WINS" -> "原曲保留"
            "HUMAN_REQUIRED" -> "待人工审核"
            "TECHNICAL_FAILED" -> "技术故障"
            "UNSUPPORTED" -> "不支持"
            "ENCRYPTION_FAILED" -> "加密失败"
            "PLAYBACK_VERIFY_FAILED" -> "验证失败"
            else -> ""
        }
}

// ---------------------------------------------------------------------------
// Payment State (for UI progress indicator)
// ---------------------------------------------------------------------------

sealed class PaymentState {
    data object Idle : PaymentState()
    data object Processing : PaymentState()
    data class Success(val providerOrderId: String) : PaymentState()
    data class Failure(val errorCode: String, val message: String) : PaymentState()
    data object Refunded : PaymentState()

    val isInProgress: Boolean get() = this is Processing
    val isTerminal: Boolean get() = this is Success || this is Failure || this is Refunded
}

// ---------------------------------------------------------------------------
// Receipt Display
// ---------------------------------------------------------------------------

@Serializable
data class ReceiptDisplay(
    val orderId: String = "",
    val settlementId: String = "",
    val amountMinor: Int = 0,
    val currency: String = "CNY",
    val billingDecision: String = "",   // CHARGE or NO_CHARGE
    val outcome: String = "",
    val settledAtMs: Long = 0,
    val refundId: String? = null,
    val refundReason: String? = null,
) {
    val formattedAmount: String get() = QuoteDisplay.formatCny(amountMinor)

    val isCharged: Boolean get() = billingDecision == "CHARGE"

    val summaryText: String
        get() = when {
            refundId != null -> "已退款: $formattedAmount"
            isCharged -> "已支付: $formattedAmount"
            else -> "免费"
        }
}

// ---------------------------------------------------------------------------
// Commerce Intent (what Android sends to server)
// ---------------------------------------------------------------------------

/**
 * Request to create a quote. Server returns actual price.
 * Android NEVER suggests amounts.
 */
@Serializable
data class QuoteRequest(
    val owner_id: String = "",
    val reconstruction_version: String = "v0.1.0",
    val source_sha256: String = "",     // track fingerprint for dedup
)

/**
 * Request to create an order from a quote.
 * idempotency_key prevents double-charge on duplicate taps.
 */
@Serializable
data class OrderRequest(
    val quote_id: String = "",
    val source_sha256: String = "",
    val reconstruction_version: String = "v0.1.0",
    val idempotency_key: String = "",   // client-generated dedup key
    val platform: String = "ANDROID_PROVIDER",
)

/**
 * Request a refund.
 */
@Serializable
data class RefundRequest(
    val order_id: String = "",
    val reason: String = "",
    val idempotency_key: String = "",   // dedup key for refund
)
