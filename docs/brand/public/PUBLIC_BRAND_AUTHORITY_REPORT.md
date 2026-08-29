# Public Brand Authority Report — Package 01

**CANON_CHANGE = YES**

**Why:** explicit human Package 01 decision freezes the public belief, product principle, site roles and public-language tiers.

**Evidence:** package manifest hashes matched; repository and live-site read-only audit completed 2026-08-19.

**Affected authority files:** root `AGENTS.md`, `docs/canon/CURRENT_CANON.md`, `PRODUCT_BOUNDARY.md`, `AUTHORITY_ORDER.md`, `CANON_CHANGELOG.md`, `docs/product-framework/PRODUCT_AUTHORITY_INDEX.md`, and this directory.

**Migration:** Packages 02–04 update Product Home, Company Home and Player separately.
**Rollback:** revert only the Package 01 authority/document changes as one unit; no production runtime rollback is needed because Package 01 changes no production code or configuration.

## 1. Highest Public Brand authority

`docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md` is the highest topic-specific Public Brand authority. It is made canonical by `docs/canon/*` and is machine-mirrored by `brand_authority.yaml`. The root `AGENTS.md` and `docs/canon/*` remain repository-level superior authorities.

## 2. Conflicting older documents

- `docs/product-framework/TERMINOLOGY_AND_CLAIMS.md` still makes `The Ear of AI` the public product identity.
- `docs/product-framework/01_MOODIFY_PRODUCT_CONSTITUTION.md` internalizes Ear but retains `The Ear of AI` as core outward identity language.
- `docs/product-framework/02_OFFICIAL_WEBSITE_BLUEPRINT.md` preserves a historical dual-product/technical-first site story.
- `docs/product-framework/04_MOODIFY_MUSIC_PRODUCT_FRAMEWORK.md` gives publishing, creator and licensing capabilities more public weight than current Public Form permits.
- `docs/product-framework/05_PUBLIC_INTERNAL_RELEASE_TOPOLOGY.md`, `docs/contracts/product-boundary.md`, and `ops/web_origin/README.md` retain earlier domain roles.

They are not deleted. Where they conflict on public identity, language prominence or site roles, they are superseded by the Public Brand authority. Their engineering contracts remain valid unless separately changed.

## 3. Conflict classification

- **Historical/product documentation:** website blueprint and old terminology definitions.
- **Current engineering documentation:** release topology and domain contracts; these describe real runtime dependencies and require staged migration, not textual erasure.
- **Still affects production:** Product Home footer/OG/About, live Company Home Hero/SEO, Player creator/upload/licensing navigation, verification scripts, hard-coded `.xyz` API/media endpoints.

## 4. How future Codex work decides

For a public-brand question, follow `AGENTS.md` → `docs/canon/*` → `docs/brand/public/`. For a claim about what is deployed, consult verified runtime evidence and current code. Brand intent cannot fabricate deployment; runtime reality cannot silently redefine the brand. Conflicts not resolved by these scopes must be labeled `HUMAN_DECISION_REQUIRED`.

## 5. Human decisions still required

- The exact production source/release provenance for `rongjingwenchuan.com`.
- Whether and when `.xyz` becomes 301, 302 or a compatibility entry after `play.rongjingmusic.com` is operational.
- Which Creator/upload/licensing routes remain reachable after they leave primary navigation.
- The final Android release advertised by Product Home.

The public belief, product principle, primary action, research-question demotion, and three-site roles are no longer open questions.
