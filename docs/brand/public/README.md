# Moodify Public Brand Authority

**Status:** CANONICAL — Public Form v0.1

**Effective:** 2026-08-19

**Human authority:** explicit Package 01 execution instruction

**Canon change:** YES

This directory is the single repository authority for Moodify's public brand language and public-site roles. It is subordinate only to the root `AGENTS.md` and `docs/canon/*`; when older product-framework, website, deployment, or historical documents conflict on public identity, this directory wins.

## Authority set

1. [`PUBLIC_BRAND_CONSTITUTION.md`](PUBLIC_BRAND_CONSTITUTION.md) — highest Public Brand authority.
2. [`brand_authority.yaml`](brand_authority.yaml) — machine-readable mirror.
3. [`PUBLIC_LANGUAGE_REGISTRY.md`](PUBLIC_LANGUAGE_REGISTRY.md) — language tiers and public-use rules.
4. [`SITE_ROLES_AND_ROUTING.md`](SITE_ROLES_AND_ROUTING.md) — site responsibilities and target routing.

## Package 01 evidence

- [`PUBLIC_SURFACE_INVENTORY.md`](PUBLIC_SURFACE_INVENTORY.md)
- [`PUBLIC_LANGUAGE_CONFLICT_MATRIX.md`](PUBLIC_LANGUAGE_CONFLICT_MATRIX.md)
- [`PUBLIC_FORM_BACKLOG.md`](PUBLIC_FORM_BACKLOG.md)
- [`PUBLIC_BRAND_AUTHORITY_REPORT.md`](PUBLIC_BRAND_AUTHORITY_REPORT.md)
- [`PACKAGE_01_ACCEPTANCE.md`](PACKAGE_01_ACCEPTANCE.md)

## Decision rule

Public identity resolves in this order:

`explicit human instruction -> AGENTS.md -> docs/canon/* -> this Public Brand authority -> verified runtime evidence -> current site/app code -> subsystem docs -> historical docs`

Runtime evidence determines what is actually deployed; it cannot replace the public-brand decision. Unverified deployment facts remain `UNVERIFIED`.
