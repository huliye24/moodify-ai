# Moodify Web Origin

> **CURRENT CLASSIFICATION (Canon v1.1 / Public Form v0.1):** `rongjingmusic.com` is the Moodify Product Home; `rongjingwenchuan.com` is the 荣景文川 Company Home; `rongjinwenchuan.xyz` is the transition Web Player / historical entry. The long-term `play.rongjingmusic.com` migration remains `UNVERIFIED`. Moodify Ear and its Workbench are internal operator/research systems and are not public product surfaces.

This directory defines the reproducible origin-server layer for:

- `rongjingmusic.com` — Moodify Product Home
- `rongjingwenchuan.com` — 荣景文川 Company Home
- `rongjinwenchuan.xyz` — transition Moodify Web Player / historical entry
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
## Internal services

The static origin deployment is extended by `deploy_moodify_service.sh`, which
installs the canonical `moodify-core-package`, FastAPI, the existing SQLite
node queue, and the serial Auditory Data Factory worker. It deliberately does
not create an independent web-task state machine.

Production service files are under `systemd/`; Nginx proxy/rate limits are
under `nginx/`; the connected workspace JavaScript is under
`site/rongjingmusic/`.
