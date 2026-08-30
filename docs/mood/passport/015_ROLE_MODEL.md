# MOOD PASSPORT 015 — Role Model

**Package:** `MOOD-PASSPORT-015`
**Authority surface:** `apps/web/lib/mood/passport/resident-registry.ts` (roles) + `apps/web/app/api/resident/me/roles/route.ts`

---

## 1. Two Classes of Roles

### Self-declared (interest signals)

A Resident may declare any subset, freely and idempotently:

```text
creator · developer · researcher · node-operator · agent-builder
```

Self-declared roles are **interest labels**, not credentials. They render as
plain pills and never imply capability or trust.

### Verified (authority-issued)

```text
verified-contributor · verified-developer · genesis-builder · node-operator-verified
```

Verified roles require an **evidence source** (URL / authority reference)
and may only be issued through `awardVerifiedRole()` — an authority-side
code path (governance / system tooling). There is **no** self-issue route:

- the self-declaration API rejects verified role names outright
  (`invalid-role`) — INV-015-11
- `awardVerifiedRole` without a non-empty source fails
  (`missing-or-invalid-source`)
- awarding a verified role strips the prior self-declared claim of the same
  name (verification supersedes declaration)

## 2. Display

Verified roles render with a `✓` prefix and a distinct pill style;
self-declared roles render plainly. The separation is visible, not cosmetic.

## 3. What Roles Are NOT

- roles are **not** permission grants in v1 (no privileged route keys off a role)
- roles are **not** token-gated: no holding threshold, no balance check
- roles are **not** inherited from wallet net worth or NFT ownership
- `node-operator-verified` / `genesis-builder` have no runtime effect until
  019 / genesis packages consume them

## 4. Badge Interaction

Roles and badges are separate registries. Badges carry richer metadata
(slug, title, description, source, evidence URL) — see 015_BADGE_MODEL.md.
A verified role *may* later be mirrored as a badge by governance tooling;
nothing does this automatically in v1.
