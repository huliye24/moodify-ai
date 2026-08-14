# Moodify Web Origin

> **PUBLIC/INTERNAL CLASSIFICATION (2026-08-14) — Per Constitution v2.0 and Release Topology v1.0: the PUBLIC product entry is `rongjingmusic.com` official website pointing to Moodify Music (`rongjinwenchuan.xyz`). `rongjingwenchuan.com` is a legacy public host awaiting an explicit disposition (redirect/alias/retire) before GO. Moodify Ear and its Workbench are INTERNAL systems; their operator routes must not be presented as public product and are not public launch surfaces.**

This directory defines the reproducible origin-server layer for:

- `rongjingmusic.com` — official website (public entry; serves the Music product story, no Ear consumer CTA)
- `rongjinwenchuan.xyz` — Moodify Music (public product)
- `rongjingwenchuan.com` — legacy public host (disposition pending)
- Ear workbench / Ear API proxy — INTERNAL (operator/research only; `noindex` is discovery hygiene, not access control)

The current frontends are static prototypes. Hosting them on the origin does
not by itself create an auditory-analysis backend. API wiring is a separate,
testable deployment step.

## Release model

Each site is stored under `/var/www/<domain>/releases/<UTC timestamp>` and the
`current` symlink is switched only after assets download successfully. Previous
releases remain available for rollback.

```bash
sudo bash ops/web_origin/deploy_static_origins.sh
sudo bash ops/web_origin/verify_origins.sh
```

Rollback changes only a symlink and reloads Nginx:

```bash
sudo bash ops/web_origin/rollback_static_origin.sh rongjingmusic.com <release-id>
```

## DNS cutover

Before DNS changes, validate by origin IP and Host header:

```bash
curl -H 'Host: rongjingmusic.com' http://103.144.246.242/healthz
curl -H 'Host: rongjingwenchuan.com' http://103.144.246.242/healthz
```

Then update the Cloudflare proxied apex A records to the origin IP. The `www`
records are currently absent; add CNAME records to each apex if `www` should be
supported. HTTPS cutover requires an origin certificate compatible with the
Cloudflare SSL mode before traffic is switched. Do not weaken SSL mode just to
make a cutover pass.
# Moodify Web Origin and Ear Service

The static origin deployment is extended by `deploy_moodify_service.sh`, which
installs the canonical `moodify-core-package`, FastAPI, the existing SQLite
node queue, and the serial Auditory Data Factory worker. It deliberately does
not create an independent web-task state machine.

Production service files are under `systemd/`; Nginx proxy/rate limits are
under `nginx/`; the connected workspace JavaScript is under
`site/rongjingmusic/`.
