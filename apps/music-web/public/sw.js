/* Moodify Music Service Worker — app-shell only.

Cache boundary (MFY_MUSIC_APP_FOUNDATION_001):
- PRECACHE: versioned JS/CSS, manifest, icons, offline shell.
- network-only: /api/*, private pages, uploads, auth responses.
- Audio Range responses: never cache-first (pass-through to network).
*/

const VERSION = "mfy-music-shell-v1";
const SHELL_CACHE = "mfy-shell";
const PRECACHE_URLS = [
  "/manifest.webmanifest",
  "/moodify-logo.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL_CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

function isShellRequest(url) {
  const { pathname } = url;
  if (pathname.startsWith("/api/")) return false; // API never cached
  if (pathname.startsWith("/audio/")) return false; // audio Range pass-through
  if (pathname.startsWith("/studio") || pathname.startsWith("/library")
    || pathname.startsWith("/inbox") || pathname.startsWith("/console")
    || pathname.startsWith("/playlists") || pathname.startsWith("/drafts")
    || pathname.startsWith("/beta-login")) return false; // private/session pages
  if (pathname.endsWith(".js") || pathname.endsWith(".css")
    || pathname.endsWith(".png") || pathname.endsWith(".svg")
    || pathname.endsWith(".ico") || pathname.endsWith(".woff2")) return true;
  return pathname === "/" || pathname === "/offline";
}

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return; // cross-origin pass-through
  if (event.request.method !== "GET") return;

  if (isShellRequest(url)) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) {
          // revalidate in background, never block navigation on stale shell
          fetch(event.request).then((fresh) => {
            if (fresh && fresh.ok) caches.open(SHELL_CACHE).then((c) => c.put(event.request, fresh));
          }).catch(() => {});
          return cached;
        }
        return fetch(event.request).then((fresh) => {
          if (fresh && fresh.ok) {
            const copy = fresh.clone();
            caches.open(SHELL_CACHE).then((c) => c.put(event.request, copy));
          }
          return fresh;
        });
      }).catch(() => caches.match("/offline")),
    );
    return;
  }

  // private/API/audio: network-only. On navigation failure show honest offline page.
  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request).catch(() => caches.match("/offline")));
  }
});
