# MFY-CR-P05 — Hardware-Neutral Master Policy

## Canonical rule

> **The approved reconstruction master should remain hardware-neutral.**
> **Reconstruction is source-specific. Rendering is device-specific.**

```text
Source
  ↓
Reconstruction Cloud          (this phase)
  ↓
Approved Reconstruction Master (hardware-neutral)
  ↓
Identity Guard                (source reference never changes with device)
  ↓
Listening Environment
  ↓
Device Intelligence           (FUTURE, NOT_AUTHORIZED_IN_P05)
  ↓
DAC / Amp / Headphone / Speaker
```

## What P05 protects

Only `Source → Reconstruction Master`. It does NOT touch
`Master → Specific Device`.

## Why

- Headphone A is bass-light, Headphone B is bass-heavy, Speaker C is
  room-dependent. Permanently baking device compensation into the master
  fixes an error that is wrong on every other device.
- Device adaptation must be **non-destructive and downstream**:

```text
正确:  Approved Master + Headphone Profile → playback render
错误:  永久把 Reconstruction Master 加 5 dB bass
```

## Device intelligence (recorded future, not authorized)

Device ID / Device Profile / Frequency Response / Output Power / Gain
Structure / Sample-rate Capability / Channel Capability / User Preference /
Environment Profile — all `FUTURE`, `NOT_AUTHORIZED_IN_P05`.

## Verification in P05

No device-specific permanent processing was produced: NO (asserted in the
final response; no device code exists in this change set).
