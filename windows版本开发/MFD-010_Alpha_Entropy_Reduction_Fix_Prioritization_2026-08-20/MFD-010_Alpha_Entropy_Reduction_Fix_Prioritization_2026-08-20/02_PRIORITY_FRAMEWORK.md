# MFD-010 Priority Framework

## Dimensions

### Evidence Strength

```text
E0 anecdote
E1 reproducible once
E2 multiple cases
E3 telemetry + reproduction
E4 strong repeated evidence
```

### Core Impact

```text
C0 irrelevant
C1 cosmetic
C2 friction
C3 repeat-use damage
C4 blocks Play
C5 security/data authority
```

### Product Fit

```text
CORE
SUPPORTING
DISTRACTING
CONTRADICTS_PRODUCT
UNKNOWN
```

### Complexity

```text
S
M
L
XL
```

### Entropy Cost

```text
LOW
MEDIUM
HIGH
VERY_HIGH
```

---

## Decision Matrix

| Evidence | Core Impact | Product Fit | Likely Decision |
|---|---|---|---|
| E3/E4 | C4/C5 | CORE | FIX_NOW |
| E2+ | C3 | CORE | FIX_NOW/FIX_NEXT |
| E1 | C2 | SUPPORTING | OBSERVE |
| E0/E1 | C0/C1 | DISTRACTING | REJECT/DEFER |
| E2+ | C2/C3 | SUPPORTING | FIX_NEXT |
| any | any | CONTRADICTS_PRODUCT | usually REJECT |
