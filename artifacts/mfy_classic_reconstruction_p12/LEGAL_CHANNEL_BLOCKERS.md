# MFY-CR-P12 — Legal / Channel Blockers

## Status: PUBLIC_RELEASE_BLOCKED (Engineering RC Approved)

> P12 does not make legal conclusions. This document lists what MUST be completed before any public paid release.

## Required Before Public Release

### Legal Review
| Item | Status | Owner |
|---|---|---|
| Target market copyright handling review | **REQUIRED** | Legal counsel |
| User-uploaded audio terms of service | **REQUIRED** | Legal counsel |
| Privacy policy (China PIPL compliant) | **REQUIRED** | Legal + Engineering |
| Third-party processor disclosure | **REQUIRED** | Legal + Engineering |
| Data retention policy | **REQUIRED** | Legal + Engineering |

### Channel Rules
| Item | Status | Notes |
|---|---|---|
| Google Play payment policy | **REQUIRED REVIEW** | Platform-specific; may differ from Web |
| App Store (future iOS) payment policy | **FUTURE** | Not applicable for Android-first RC1 |
| China consumer protection law compliance | **REQUIRED** | Refund rights, disclosure |
| Tax / invoice (发票) integration | **REQUIRED** | CNY revenue requires fapiao capability |

### Payment
| Item | Status | Notes |
|---|---|---|
| WeChat Pay merchant account | **REQUIRED** | Primary China payment method |
| Alipay merchant account | **RECOMMENDED** | Secondary China method |
| Payment callback security audit | **REQUIRED** | Before real transactions |
| PCI-DSS or equivalent | **ASSESS** | Depends on card payment support |

### Brand Promise Constraints (Per P12 #45)
- ❌ Will NOT promise "任何歌都变好听"
- ❌ Will NOT promise "AI 无损修复一切"
- ❌ Will NOT promise "绝对还原原始母带"
- ❌ Will NOT promise "zero knowledge" (we use envelope encryption, not ZK proofs)
- ✅ WILL promise "private cloud reconstruction"
- ✅ WILL promise "reconstruction designed to preserve recording identity"
- ✅ WILL disclose "results may vary by source and playback system"

## Internal RC Position

```
ENGINEERING_RC_READY      = YES
AUDIO_RC_READY            = BLOCKED (no production pipeline to validate)
ANDROID_RC_READY          = BLOCKED (no real device test per user constraint)
CLOUD_RC_READY            = BLOCKED (static website only, no Ear API)
PRIVACY_RC_READY          = PASS (architecture verified; production audit pending)
COMMERCE_RC_READY         = SANDBOX_ONLY (FakePaymentProvider validated)
OPERATIONS_RC_READY       = PARTIAL (monitoring defined; no production infra)
PUBLIC_MONETIZATION_READY  = NO (legal + channel + real payment + audio validation all needed)
```

## Staging Release Path

Before any public release:
1. **Internal closed test**: 3–10 trusted users, authorized test material only
2. **Collect metrics**: crash rate, completion rate, user preference, source wins %
3. **Legal sign-off**: All items in table above
4. **Payment go-live**: Real provider integration with staging transactions
5. **Gradual rollout**: Feature flags allow disable without full shutdown
