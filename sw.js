// ═══════════════════════════════════════════════
// SERVICE WORKER — QuoteApp
// ═══════════════════════════════════════════════
// INCREMENT this on every deploy to trigger update:
const CACHE_VERSION = 4;
const CACHE_NAME = 'quoteapp-v' + CACHE_VERSION;

// Core assets to pre-cache on install
const PRECACHE = [
  './',
  './index.html',
  './data.json',
  './data-mikedyson.json',
  './data-motscools.json',
  './manifest.json'
];

// ── INSTALL: pre-cache core assets ──
self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE))
      .catch(err => console.warn('SW precache fail:', err))
  );
  // Do NOT skipWaiting — let the client show the update popup
});

// ── ACTIVATE: purge all old caches ──
self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── FETCH: stale-while-revalidate ──
self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET' || !req.url.startsWith('http')) return;

  // Navigation (HTML): network-first, cache fallback
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req).then(res => {
        const clone = res.clone();
        caches.open(CACHE_NAME).then(c => c.put(req, clone));
        return res;
      }).catch(() => caches.match(req).then(r => r || caches.match('./')))
    );
    return;
  }

  // Other assets: serve cache, update in background
  e.respondWith(
    caches.open(CACHE_NAME).then(cache =>
      cache.match(req).then(cached => {
        const fresh = fetch(req).then(res => {
          if (res.ok) cache.put(req, res.clone());
          return res;
        }).catch(() => null);
        return cached || fresh;
      })
    )
  );
});

// ── MESSAGE: client triggers activation ──
self.addEventListener('message', (e) => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});
