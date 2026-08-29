# Public Brand Lint Rules

**Date:** 2026-08-19
**Package:** 05 - Brand Unification
**Purpose:** Automated brand consistency checking for public-facing code

---

## Rule Set

### Category 1: Forbidden First-Layer Identity

These phrases must NOT appear in hero, primary nav, main CTA, or `<title>`:

```json
{
  "forbidden_first_layer": [
    "The Ear of AI",
    "Auditory Intelligence Infrastructure",
    "Give machines the ability to hear",
    "Build with Moodify",
    "ACU",
    "Auditory Computing Unit",
    "API-first",
    "Developer Platform",
    "Creator Platform as primary identity"
  ]
}
```

**Severity:** ERROR if in: hero, title, primary nav, metadata
**Severity:** WARN if in: footer, secondary nav, body copy (context-dependent)

---

### Category 2: Required Brand Phrases

These must be present on their respective surfaces:

```json
{
  "required_phrases": {
    "product_home": [
      "Every voice deserves to be heard",
      "每一种声音，都值得被世界听见",
      "Listen. Then Play."
    ],
    "company_home": [
      "We build things worth hearing",
      "Rongjing Wenchuan",
      "荣景文川"
    ],
    "player": [
      "Moodify",
      "Play"
    ]
  }
}
```

**Severity:** WARN if missing (may be in sub-section or aria-label)

---

### Category 3: Domain Correctness

```json
{
  "domain_rules": {
    "company_home_canonical": "rongjingwenchuan.com",
    "product_home_canonical": "rongjingmusic.com",
    "player_canonical": "play.rongjingmusic.com",
    "legacy_domain": "rongjinwenchuan.xyz",
    "forbidden_as_primary_brand": ["rongjinwenchuan.xyz", ".xyz"]
  }
}
```

**Severity:** ERROR if `.xyz` used as canonical or primary brand reference
**Severity:** INFO if `.xyz` present in audio URL fallback (expected during migration)

---

### Category 4: Metadata Consistency

```json
{
  "metadata_rules": {
    "title_max_length": 60,
    "description_max_length": 160,
    "must_have_og": true,
    "canonical_required": true,
    "no_duplicate_title_across_sites": true
  }
}
```

---

### Category 5: Navigation Contracts

```json
{
  "navigation_contracts": {
    "company_to_product": {
      "required": true,
      "target": "rongjingmusic.com",
      "max_redirects": 1
    },
    "product_to_player": {
      "required": true,
      "target": "play.rongjingmusic.com",
      "max_redirects": 1
    },
    "player_to_product": {
      "required": true,
      "target": "rongjingmusic.com",
      "max_redirects": 1
    },
    "product_to_company": {
      "required": true,
      "target": "rongjingwenchuan.com",
      "max_redirects": 1
    }
  }
}
```

---

### Category 6: Truth Policy

```json
{
  "truth_policy": {
    "forbidden_unless_verified": [
      "funding amount",
      "valuation",
      "partnership announcement",
      "user count",
      "revenue figure",
      "team size claim",
      "launch date claim"
    ],
    "labeling_requirement": "If any metric is shown, must include 'as of [date]' or 'source: [source]'"
  }
}
```

**Severity:** ERROR if unverified claim in public surface
**Severity:** WARN if in internal/research docs (acceptable context)

---

## Implementation Notes

This rule set can be implemented as:
1. **Python script** (`scripts/public_brand_lint.py`) — grep + regex based
2. **ESLint plugin** — custom rules for JSX/TSX
3. **CI step** — run on PRs touching public paths

Recommended scope for linting:
```
apps/music-web/app/
ops/web_origin/site/
docs/public-form/
```

Exclude from linting:
```
docs/canon/          # Internal authority
experiments/         # Research
research/            # Academic work
apps/ear-workbench/  # Internal tool
```
