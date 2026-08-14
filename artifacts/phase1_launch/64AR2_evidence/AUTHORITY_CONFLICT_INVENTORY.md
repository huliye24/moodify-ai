# Authority Conflict Inventory (dual-product expressions)

**Package:** MFY_PUBLIC_MUSIC_INTERNAL_EAR_PROPAGATION_001 (64A-R2), test matrix
**Date:** 2026-08-15
**Rule:** repair current authoritative documents only; historical results are inventoried, not batch-edited.

## Fixed in current authoritative documents

| File | Expression | Action |
|---|---|---|
| `ops/web_origin/site/rongjingmusic/ear.html` | public Ear landing | noindex + "INTERNAL CAPABILITY · HISTORICAL EXPLANATION" header; removed from nav and sitemap |
| `ops/web_origin/site/rongjingmusic/music.html` | dual-product story "Works first. Listening always." / Discover·Listen·Collect·Follow·Connect | retold around Library → Track → Now Playing → Play (Constitution-approved expressions only); Follow/support demoted to a note |
| `ops/web_origin/site/check_site.mjs` | — | new contracts: 3-item nav on every public page, no `/ear.html` links, sitemap excludes Ear, ear.html internalized |
| `docs/product-framework/02_OFFICIAL_WEBSITE_BLUEPRINT.md` | "two products", "Enter Moodify Ear" in body | top-of-file v2 supersession notice; historical body untouched |
| `docs/product-framework/03_MOODIFY_EAR_PRODUCT_FRAMEWORK.md` | public product framing | top-of-file RECLASSIFIED (INTERNAL RESEARCH AND PRODUCTION) notice |
| `docs/product-framework/04_MOODIFY_MUSIC_PRODUCT_FRAMEWORK.md` | — | top-of-file CONFIRMED AS THE ONLY PUBLIC PRODUCT + Source-to-Play notice |
| `docs/contracts/product-boundary.md` | EAR_CANONICAL / MUSIC_CANONICAL labels | CLASSIFICATION UPDATE notice + INTERNAL_CANONICAL / PUBLIC_PRODUCT labels |
| `docs/REPOSITORY_STATUS.md` | brand identity vs product | new "Brand / Core Identity vs Public Product" section |
| `ops/web_origin/README.md` | "Moodify Ear workspace" / "product site" | public/internal classification block |
| `ops/web_origin/VALIDATION_FABRIC_001.md`, `PRODUCTION_TOPOLOGY.md` | — | public/internal classification notices |

## Historical / retained (inventory only, not edited)

| File | Expression | Why retained |
|---|---|---|
| `apps/music-web/AUDIT.md:108,234` | "Ear workspace" | historical audit describing the old topology (pre-Constitution v2.0) |
| `docs/product-framework/02_OFFICIAL_WEBSITE_BLUEPRINT.md` body | "two products" / "Enter Moodify Ear" | historical baseline; supersession notice added above |
| `docs/product-framework/03_MOODIFY_EAR_PRODUCT_FRAMEWORK.md` body | public product definition | historical baseline; reclassification notice added above |
| `ops/web_origin/site/check_site.mjs` | assertion patterns "One ear. Two products" etc. | negative contract patterns, not claims |
| `补丁包/64A`, `补丁包/64A-2` | dual-product task instructions | superseded packages; never rewritten |
| `docs/product-framework/05_PUBLIC_INTERNAL_RELEASE_TOPOLOGY.md:70` | "public Ear API proxy" | migration safety rule wording, classification-correct in context |
| `docs/product-framework/04_...:305` | "public Ear quality certification" | forbidden-claims list, negative context |

## 00/06/07/08 current authority set

New documents (2026-08-15) added by Codex are retained as-is: `00_CURRENT_PRODUCT_DIRECTION_20260815.md`, `06_MOODIFY_PUBLIC_PRODUCT_DESIGN_20260815.md`, `07_SOUND_FIRST_PRODUCT_DOCTRINE_20260815.md`, `08_MOODIFY_V1_SCOPE_AND_SUBTRACTION_20260815.md` — no edits made (outside allowed scope).
