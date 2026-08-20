# Moodify Public / Internal Release Topology

**Document ID:** MFY-PUBLIC-INTERNAL-TOPOLOGY-001  
**Version:** 1.0  
**Date:** 2026-08-14  
**Status:** ACTIVE — implements Product Constitution v2.0  
**Owner:** Human product authority + release authority

## 1. Public topology

```text
rongjingmusic.com
  -> Official Website
  -> one primary action: enter Moodify Music

rongjinwenchuan.xyz
  -> Moodify Music
  -> Library / Track / Now Playing / Play
```

`rongjingwenchuan.com` is a legacy public product-site hostname. Before launch it must receive one explicit disposition: redirect to the official website, remain a verified alias, or be retired. It must not host a conflicting product story.

## 2. Internal topology

```text
Moodify Music service
  -> bounded request/reference contracts
  -> Moodify Ear API / worker
  -> ProductionCase / Evidence / human review
  -> verified playback-ready result when implemented
```

Ear Workbench and Ear operator routes have no consumer public product role. Their eventual access path must be authenticated and operationally controlled, for example private network, VPN, operator allowlist or equivalent reviewed control.

`noindex` is discovery hygiene, not access control.

## 3. Domain and route decisions

| Surface | Classification | Decision |
|---|---|---|
| `rongjingmusic.com` | PUBLIC ENTRY | Official Website only; no Ear consumer CTA |
| `rongjinwenchuan.xyz` | PUBLIC PRODUCT | Moodify Music |
| `rongjingwenchuan.com` | LEGACY PUBLIC HOST | Requires explicit redirect/alias/retire decision before GO |
| Official `/ear.html` | NON-PUBLIC LEGACY EXPLANATION | Remove from nav and sitemap; add noindex; do not market as product |
| `apps/ear-workbench` | INTERNAL OPERATOR | Preserve; add internal classification and noindex to every page |
| Public `/api/v1` Ear proxy on website host | TRANSITION RISK | Must not be removed blindly; inventory consumers, then move behind reviewed internal/service access |
| Music `/api/v1/music` | PUBLIC PRODUCT API/BFF | Preserve public contract and authorization |

## 4. Release candidate

Public artifact:

- official website;
- Moodify Music web;
- verified Music media/playback path;
- Music Android only when separately accepted.

Internal release dependencies:

- Ear API/worker health;
- source integrity;
- ProductionCase/Evidence correctness;
- bounded authority and human escalation;
- preparation/rendering correctness where used;
- backup, recovery, security and observability.

## 5. Migration safety

1. Do not delete Ear code, state, evidence or tests.
2. Do not remove the public Ear API proxy until every real consumer is inventoried.
3. Do not expose an internal Workbench merely because it has `noindex`.
4. Do not claim `Track Rendering Profile` or automatic playback-ready selection until a single implemented authority and end-to-end evidence exist.
5. Do not deploy DNS/nginx changes without human deployment authorization and rollback evidence.
6. Preserve source assets and existing Music publication authority.

## 6. Sound-first release truth

For 2026-08-22, the safe public claim is limited to what the deployed media path proves. If automated Source-to-Play preparation is not fully connected, launch with a curated set of internally prepared and verified playback-ready works and label broader automation as future capability.

The release must not convert a product direction into a production claim.
