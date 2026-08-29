# Moodify Web Origin Deployment Evidence

## Scope

- Origin: `103.144.246.242` (`moodify-ear-runner`)
- Sites: `rongjingmusic.com`, `rongjingwenchuan.com`
- Deployment type: static release mirror behind Nginx and Cloudflare Tunnel
- DNS cutover: completed 2026-08-12

## Verified server state

- Ubuntu 22.04.2 LTS, 4 CPU, approximately 7.9 GB RAM and 91 GB free disk.
- Nginx 1.18 is enabled and active.
- UFW is enabled with default inbound deny.
- Allowed inbound services: OpenSSH and Nginx Full (80/443).
- Per-site access/error logs are configured.
- Releases are timestamped and selected through `current` symlinks.
- Nginx restart and configuration validation passed.
- `cloudflared-moodify.service` is enabled and active.
- Tunnel `moodify-web-origin` has ID
  `92f54925-3754-4093-9ac9-1702a14e2a70` and established four QUIC
  connections to Cloudflare edge locations.

## Content verification

The following paths returned HTTP 200 with expected content after deployment
and again after Nginx restart:

- `rongjingmusic.com`: `/`, `/healthz`, `/app-workspace.css`,
  `/app-workspace.js`, `/assets/moodify-symbol.png`
- `rongjingwenchuan.com`: `/`, `/healthz`, `/styles.css`, `/app.js`,
  `/assets/moodify-symbol.png`

An independent Windows-side test used `curl --resolve` against the public origin
IP and verified the correct HTML title for each Host header.

After DNS cutover, public HTTPS checks for both apex domains returned:

- HTTP 200 through Cloudflare;
- `X-Moodify-Origin: moodify-cloud-103-144-246-242`;
- `CF-Cache-Status: DYNAMIC` on the cache-busted health request;
- the expected per-site JSON from `/healthz`;
- the expected Moodify page title.

This origin-specific header and the dynamic health response distinguish the new
server from the previously cached Cloudflare Pages responses.

## DNS and rollback evidence

The active proxied apex records now point to:

`92f54925-3754-4093-9ac9-1702a14e2a70.cfargotunnel.com`

The records replaced during cutover were:

- `rongjingmusic.com` -> `rongjingmusic.pages.dev` (proxied CNAME)
- `rongjingwenchuan.com` -> `rongjingwenchuan.pages.dev` (proxied CNAME)

These values are the rollback targets. Test hostnames were removed after
successful validation.

Tunnel credentials and Cloudflare origin certificates remain server-only under
`/root/.cloudflared` with mode `0600`; their contents were not recorded in the
repository. The unused Nginx Origin CA CSRs and private keys remain inactive
under `/etc/nginx/origin-certs`.

## Operational state

- Nginx and the Tunnel are enabled at boot and active.
- Nginx and Tunnel restart automatically on failure.
- UFW remains active with SSH and Nginx ingress allowed.
- Release directories and `current` symlinks provide content rollback.
- The apex sites are live on the new server; `www` records were intentionally
  left unchanged/absent because they were not part of the requested URLs.

The existing public sites remain online through their prior Cloudflare origins.
