# Moodify Web Player

**Role:** public Moodify Music / Player surface

**Primary action:** Play

**Canonical public host:** `play.rongjingmusic.com` (verified live 2026-08-22)

**Compatibility host:** `rongjinwenchuan.xyz` (temporarily retained; redirect policy pending)

This application is the browser listening surface for Moodify. The default experience is playback: discover a track, press Play, and continue listening. Internal Ear, reconstruction, evidence, jobs, and processing controls are not public product navigation.

## Public boundary

- The default route is a player, not a creator dashboard or Ear workbench.
- Library and account actions appear only when the current session supports them.
- Creator tools are secondary authenticated surfaces; they do not define Moodify's first public identity.
- The Moodify logo returns to `rongjingmusic.com`, the Product Home.
- Company links go to `rongjingwenchuan.com`.
- Public language follows `docs/brand/public/PUBLIC_BRAND_CONSTITUTION.md`.

## Runtime shape

- UI: Next.js-compatible React application built with Vinext/Vite.
- Public catalogue and account operations: canonical `/api/v1/music` BFF.
- Self-hosted deployment: `MOODIFY_SELF_HOSTED=1`, using the fail-closed Cloudflare-binding adapter.
- Optional Sites deployment: D1/R2 bindings declared in `.openai/hosting.json`.
- Service worker: `public/sw.js`; private `/api/*` responses must not be cached.

The self-hosted path is the current repository production shape. Optional Cloudflare bindings and examples are not claims that D1/R2 are deployed.

## Audio assets

Real audio is a deployment asset and must not enter ordinary Git history. Published-track filenames, sizes, and SHA-256 values are recorded in `assets/cadeau10-album1.json` for release and rollback verification.

The player reads from `NEXT_PUBLIC_AUDIO_BASE_URL`. Its transition fallback is:

```text
https://play.rongjingmusic.com/audio
```

Expected media layout:

```text
cadeau10-album1/<manifest file>
```

`public/audio/` remains ignored. Do not commit private audio, unlicensed media, or generated heavy assets.

## Authentication and writes

The self-hosted BFF defaults to `demo_read_only`. Invited creator sessions require:

- `MOODIFY_BFF_AUTH_MODE=invite_beta`
- a random `MOODIFY_BFF_SESSION_SECRET` of at least 32 characters
- `MOODIFY_BFF_BETA_INVITES` containing SHA-256 invite-code hashes mapped to existing user IDs

Raw invite codes and session secrets must never enter Git. Creator upload is capability-gated and secondary to the listening experience.

## Development and verification

Requirements:

- Node.js `>=22.13.0`
- Linux or Git Bash for the repository shell helpers

```bash
npm ci
npm run build
npm test
```

For the LA Node production service, use the explicit self-hosted build command:

```bash
npm run build:self-hosted
```

Do not deploy a plain `npm run build` artifact to the Node service: that mode
may retain Cloudflare-only virtual imports and is intended for the Worker/Sites
target.

Useful targeted checks:

```bash
npm run lint
npm run test:contracts
npm run validate:artifact
npm run validate:no-deploy-audio
```

`npm run build` removes bundled audio before validating the artifact. A successful build proves the artifact contract; it does not prove the public host, media origin, BFF, or database is deployed.

## Evidence and failure behavior

- Deployment and media checks live under `apps/web/docs/` and the relevant evidence artifacts.
- Catalogue failure falls back only to the bounded demo catalogue; it must not fabricate account or deployment state.
- Media errors remain visible and must not be converted into a successful playback claim.
- Public capability claims require runtime evidence, not only routes or UI code.
