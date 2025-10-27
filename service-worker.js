self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('nebula-cache-v1').then((cache) => {
      return cache.addAll([
        '/',
        
        '/static/js/chat.js',
        '/static/img/icon-192.png',
        '/static/img/icon-512.png', '/static/img/nebula_logo.png'
      ]);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request);
    })
  );
});
