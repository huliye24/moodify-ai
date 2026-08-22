# MFY-CR-P12 Reconstruction RC1 — BASELINE

## Release Identity

```text
Release:          Moodify Reconstruction RC1
Branch:            codex/moodify-classic-reconstruction-001
Product:           Moodify Music / Moodify Player
Core Action:        PLAY
Internal System:   Moodify Ear (Auditory Intelligence)
```

## Canonical Product Definition (Frozen)

> **Moodify is a reconstruction-first listening environment.**

User flow:
```
Choose Music → Reconstruct → Play
```

Internal:
```
Ear understands → Cloud reconstructs → Identity Guard protects →
Private Audio secures → Listening Environment renders and plays
```

## Version Freeze

| Component | Version | Status |
|---|---|---|
| product_version | Moodify Reconstruction RC1 | FROZEN |
| reconstruction_version | v0.1.0 | FROZEN |
| api_version | v0.1.0 | FROZEN |
| private_audio_container_version | v0.1.0 | FROZEN |
| pricing_version | v0.1.0 | FROZEN |
| android_version_name | 0.1.0-rc1 | FROZEN |
| android_version_code | 1 | FROZEN |

## RC Freeze Scope

**Frozen:**
- Public API contract (P08 DTOs)
- Reconstruction objective version (P04)
- Identity guard version (P05)
- Private audio container format (P10)
- Android UI structure (P09)
- Pricing policy version (P11)
- Data model schemas

**Allowed changes only:**
- BLOCKER_FIX
- SECURITY_FIX
- CRASH_FIX
- DATA_LOSS_FIX
- PAYMENT_CORRECTNESS_FIX
- PRIVACY_FIX
- AUDIO_CORRUPTION_FIX

**Explicitly forbidden:**
- New features
- Major refactors
- New models/DSPs
- New business models
- Community/hardware/token systems
