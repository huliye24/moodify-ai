# MFY-CR-P11 — Unresolved Items

| ID | Item | Severity | Category | Description |
|---|---|---|---|---|
| U-11-01 | Real Payment Gateway Integration | HIGH | External | No WeChat Pay/Alipay/Stripe credentials. FakePaymentProvider validates all logic but cannot process real transactions. |
| U-11-02 | Persistent Database Backing | HIGH | Infrastructure | OrderService, RefundService, SettlementService all use in-memory dicts. Need PostgreSQL/MongoDB for production durability and concurrency. |
| U-11-03 | Webhook Signature Verification (Production) | MEDIUM | Security | FakeProvider accepts any signature. Real provider requires HMAC/RSA signature verification with secret from secret manager. |
| U-11-04 | Distributed Rate Limiting | MEDIUM | Abuse Protection | Per-user rate limit, max concurrent unpaid jobs need Redis/memcached for multi-instance deployment. |
| U-11-05 | App Store / Google Play Payment Policy | HIGH | Legal/Compliance | P11 architecture supports platform separation (ANDROID_PROVIDER/WEB_PROVIDER/IOS_PROVIDER) but actual platform payment rules must be verified before launch. |
| U-11-06 | Tax/Invoice (中国税务/发票) | MEDIUM | Legal/Compliance | China fapiao (发票) integration not implemented. Required for CNY revenue. |
| U-11-07 | Production Secret Management | MEDIUM | Security | Payment API keys must be stored in AWS Secrets Manager / Azure Key Vault / similar. Never in code, Git, or Android. |

## Notes

- **U-11-01 through U-11-07 are infrastructure/legal blockers, NOT code defects.**
- All commerce logic (idempotency, billing matrix, settlement gate, refund flow) is fully implemented and tested.
- The system is **COMMERCE_READY_TECHNICALLY** per spec item #33 — engineering is complete but public monetization awaits external dependencies.
