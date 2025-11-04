const CACHE_NAME = 'gold-game-v1';
const urlsToCache = [
  '/game',
  '/static/css/game.css',
  '/static/js/game.js',
  '/static/sounds/win.mp3',
  '/static/sounds/lose.mp3',
  '/static/sounds/trade.mp3',
  '/static/sounds/alert.mp3'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
