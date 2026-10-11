/* Service worker de NO APAGUES LA LUZ (PWA).
 * Estrategia: cache-first con relleno en segundo plano. El nucleo se precarga
 * al instalar; todo lo que el juego pida despues (runtime CDN, apk, fuentes)
 * se guarda al vuelo -> la segunda visita y el juego offline funcionan.
 * 1791746660 lo sustituye tools/build_web.py por un sello de tiempo en cada build:
 * cache nueva en cada version (los archivos viejos se purgan al activar).
 */
const CACHE = 'napal-1791746660';
const CORE = ['./', 'index.html', 'manifest.webmanifest', 'icon_192.png',
              'icon_512.png', 'icon_maskable.png', 'icon_napal.png', 'favicon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(CORE)).catch(() => {}).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  e.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        try {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        } catch (err) { /* respuesta opaca o no cacheable */ }
        return res;
      }).catch(() => caches.match('index.html'));
    })
  );
});
