# MFY-CR-P12 — Known Limitations

## Technical Limitations

### Audio Processing
| Limitation | Impact | Mitigation |
|---|---|---|
| No production Ear pipeline | Cannot run real reconstructions | P06/P07 code structure ready; needs cloud deployment |
| Golden tracks not runnable on current cloud | Cannot verify audio quality regression | 2 VPS servers exist but only host static website |
| No real DSP inference | All reconstruction is stub/mock | AI inference pipeline not yet deployed |

### Android
| Limitation | Impact | Mitigation |
|---|---|---|
| Gradle build blocked on this machine | Cannot produce APK for testing | native-platform.dll sandbox issue; code compiles logically |
| ReconstructionClient is STUB | No real HTTP calls to server | Interface defined; OkHttp/Ktor decision pending |
| No real Keystore test | Device key generation untested on hardware | Code follows Android docs; needs real device |

### Cloud / Backend
| Limitation | Impact | Mitigation |
|---|---|---|
| In-memory state storage (P11) | Orders/refunds lost on restart | Needs PostgreSQL/MongoDB before production |
| No production database | No persistence, no concurrency safety | Schema designed; migration planned |
| Static website only on VPS | No Ear API, no job queue | Full cloud deployment needed |

### Commerce
| Limitation | Impact | Mitigation |
|---|---|---|
| FakePaymentProvider only | No real transactions possible | WeChat Pay/Alipay integration needed |
| No rate limiting middleware | Abuse protection incomplete | Redis/memcached needed for distributed limiting |
| China tax/invoice not integrated | Cannot issue fapiao | Third-party integration required |

### Privacy / Security
| Limitation | Impact | Mitigation |
|---|---|---|
| Single-user dev auth | No multi-user isolation tested | Auth architecture defined; needs implementation |
| No plaintext retention audit possible | Cannot verify server-side cleanup | Need production server access |
| No webhook signature verification (real) | FakeProvider accepts any signature | Real provider requires HMAC/RSA verification |

## Functional Limitations

- **No subscription / VIP / tokens / coins** — Per P11 spec, single-track payment only
- **No community / social / sharing** — Per P11/P12 spec, play-first product
- **No hardware / DAC / EQ** — Per P12 spec, Phase 2 only
- **No download / export of reconstructed results** — Private playback only
- **No stems processing in v0.1** — Feature flag ENABLE_STEMS defaults off
- **No auto-upgrade charging** — New reconstruction version pricing decided by policy

## Environmental Limitations (This Session)

- Windows sandbox blocks Gradle native platform DLL → APK cannot be built on this machine
- No physical Android device connected → real-device testing skipped per user instruction
- No production cloud credentials → E2E cloud jobs cannot be executed
- No payment gateway merchant accounts → real commerce blocked to sandbox
