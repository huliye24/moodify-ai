# MFY-CR-P11 Reconstruction Commerce v0.1 — BASELINE

## Architecture Summary

P11 establishes an independent **Reconstruction Commerce Layer** with the following flow:

```
Quote → Order → PaymentAttempt → ReconstructionJob → PrivateAudioObject → Settlement → Receipt
```

### Authority Boundaries
| Truth Source | Authority |
|---|---|
| Price | Server-side `PricingPolicy` (versioned) |
| Payment | Verified provider / server |
| Job | `ReconstructionJob` |
| Audio Result | `PrivateAudioObject` |
| Android | **NEVER** payment authority |

### Modules Created

#### Server-side Python (`moodify_runtime/p11_commerce/`)

| Module | Purpose | Key Classes/Functions |
|---|---|---|
| `models.py` | All commerce data objects | `ReconstructionQuote`, `ReconstructionOrder`, `PaymentAttempt`, `Settlement`, `RefundRecord`, `ExternalCostLedger`, `AuditEntry` |
| `pricing.py` | Server-side configurable pricing | `PricingPolicy`, `PricingRule` — versioned, singleton |
| `billing_matrix.py` | Outcome → billing decision + settlement gate | `resolve_billing()`, `SettlementGate.check()`, `can_settle()` |
| `order_service.py` | Idempotent order creation + job binding | `OrderService`, `OrderCreateRequest` — dedup by idempotency key + source hash |
| `provider.py` | Payment provider abstraction | `PaymentProvider` (ABC), `FakePaymentProvider` (sandbox), `ProviderRegistry` |
| `settlement.py` | Settlement execution | `SettlementService` — gate-enforced, no double-settle |
| `refund.py` | Idempotent refund processing | `RefundService` — server-verified, audit-logged |
| `audit.py` | Immutable audit trail | `AuditLog` — 12 event types, queryable, JSON-exportable |
| `reconciliation.py` | Orders vs payments vs settlements | `ReconciliationService`, `format_currency()` |
| `metrics.py` | Commerce metrics for unit economics | `MetricsCollector`, `CommerceMetrics` — revenue/cost/margin tracking |

#### Android-side Kotlin (`apps/music-android/.../data/CommerceDto.kt`)

| Component | Purpose |
|---|---|
| `QuoteDisplay` | Read-only quote display (server-provided values) |
| `OrderDisplayStatus` | Sealed interface for Compose status rendering |
| `OrderDisplay` | Read-only order display with formatted amounts |
| `PaymentState` | Sealed UI state machine for payment progress |
| `ReceiptDisplay` | Settlement/refund receipt display |
| `QuoteRequest` / `OrderRequest` / `RefundRequest` | Client->Server request DTOs (Android never sets prices) |

### Design Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | Integer minor units (fen) for all monetary values | No floating-point precision loss in financial calculations |
| D2 | Pricing versioning on every quote/order | Historical orders reconstructable with exact rules in effect at transaction time |
| D3 | Idempotency key as client-provided dedup mechanism | Prevents double-charge from duplicate taps, network retries, callback replays |
| D4 | Source-hash-based dedup index | Same user + same track + same version = existing order (RETURN_EXISTING_RESULT) |
| D5 | One-order-one-job binding | Internal retries never create new orders or duplicate charges |
| D6 | SettlementGate requires 4 conditions for CHARGE | PrivateAudioObject finalized + playback verified + payment authorized + SUCCEEDED outcome |
| D7 | No-charge outcomes settle immediately without gates | SOURCE_WINS, TECHNICAL_FAILED etc. don't need payment/finalization checks |
| D8 | FakePaymentProvider for sandbox | No real payment gateway integration per "没有权限的就跳过" |
| D9 | Refund idempotency check before status check | Handles already-refunded orders gracefully on replay |
| D10 | Audit log is append-only | Immutable trail for compliance debugging |
| D11 | External cost ledger separated from user price | Internal cost ≠ revenue (unit economics) |
| D12 | Android DTOs are display-only | Android never fabricates, modifies, or caches payment truth |

## Completion Checklist

### Quote
- [x] Pricing version carried on every quote
- [x] Expiration enforced (TTL = 10 min)
- [x] Currency = CNY (server-configurable)
- [x] Amount in integer minor units (fen)

### Order
- [x] Create order with server-resolved pricing
- [x] Idempotency via client key prevents duplicates
- [x] Duplicate tap (same source+version) returns existing order
- [x] One order binds to one logical job
- [x] Internal retry cannot create new order

### Outcome Billing
- [x] SUCCEEDED → CHARGE
- [x] SOURCE_WINS → NO_CHARGE
- [x] HUMAN_REQUIRED → NO_CHARGE_YET (blocks premature settlement)
- [x] TECHNICAL_FAILED → NO_CHARGE
- [x] UNSUPPORTED → NO_CHARGE
- [x] ENCRYPTION_FAILED → NO_CHARGE
- [x] PLAYBACK_VERIFY_FAILED → NO_CHARGE

### Payment (Fake/Sandbox Provider)
- [x] Success path works
- [x] Failure simulation works
- [x] Timeout simulation works
- [x] Callback replay detection
- [x] Refund through provider
- [x] Duplicate refund idempotency

### Settlement Gate
- [x] Cannot settle before PrivateAudioObject finalized
- [x] Cannot settle before playback verification
- [x] Cannot double-settle
- [x] No-charge outcomes bypass strict gates

### Security
- [x] Secrets not in data models (architecture-level)
- [x] Cross-user order isolation enforced
- [x] Client cannot self-declare paid (server authoritative status)
- [x] Amounts are integers, never float

### Integration
- [x] E2E happy path: quote→order→pay→job→settle(CHARGE)
- [x] E2E source-wins path: order→job→settle(NO_CHARGE)
- [x] E2E refund path: charge→settle→refund→REFUNDED

### Tests: 71 passed, 0 failed

## Blocked Items (require external dependencies)

| ID | Item | Why Blocked |
|---|---|---|
| U-11-01 | Real payment gateway (WeChat Pay / Alipay) | No API credentials / merchant account; FakeProvider used for sandbox validation |
| U-11-02 | Production database backing | v0.1 uses in-memory store; needs PostgreSQL/MongoDB before launch |
| U-11-02 | Webhook signature verification (real) | Depends on real provider integration |
| U-11-03 | App Store / Google Play payment policy verification | Legal/compliance task, not engineering |
| U-11-04 | Tax/invoice integration | China-specific regulatory requirement |
| U-11-05 | Rate limiting middleware | Needs Redis or similar for distributed rate limiting |
