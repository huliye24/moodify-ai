# Stereo-First Policy

**Part of:** [CLASSIC_RECONSTRUCTION_CONSTITUTION.md](CLASSIC_RECONSTRUCTION_CONSTITUTION.md) (v1.0)
**Status:** LIVE

---

## 1. Principle

> **Stereo-first, stems-on-demand.**

Stereo is the default source of truth. The stereo master is what the artist and production chain delivered; it is the primary domain for measurement, diagnosis and reconstruction.

## 2. Decision Flow

```text
Stereo Source
  ↓
Measure
  ↓
Diagnose
  ↓
Can the limitation be addressed safely in stereo?
  ├─ YES → Stereo Reconstruction
  └─ NO
       ↓
Is stem separation justified?
  ├─ NO → BYPASS / HUMAN_REQUIRED
  └─ YES → Stem Separation
```

## 3. When Stems Are Allowed

Stem separation may be invoked only when ALL of the following hold:

1. a specific limitation cannot be addressed safely in stereo;
2. separation is likely to create more benefit than artifact risk;
3. the result can be verified.

## 4. Why Stereo Comes First

The following reasons are canonical:

- stem separation has monetary cost;
- stem separation can introduce artifacts;
- bleed (leakage between separated stems) can damage identity;
- many era limitations are stereo-visible and addressable in stereo;
- separation is a means, not a product identity.

## 5. Forbidden

> **Every track must be separated.**

This is forbidden. Separation is justified per-case through the decision flow, never by default.

## 6. Relationship to External Services

LALAL and Audiolla are **optional external stem/reconstruction services**, invoked only under this policy. They never define the product identity and never bypass the decision model.
