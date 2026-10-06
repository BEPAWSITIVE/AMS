const CACHE_NAME = 'ams-cache-v4';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll([
        '/',
        '/manifest.json'
      ]);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  
  // Skip supabase api calls or other external stuff from being aggressively cached if needed
  // but network-first is safe anyway.
  
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Don't cache bad responses or partials
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }
        
        // Clone response and cache it
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseToCache);
        });
        
        return response;
      })
      .catch(() => {
        // Network failed (offline). Look in cache.
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // If it's a page navigation request and not in cache, fallback to '/'
          if (event.request.mode === 'navigate') {
            return caches.match('/');
          }
          
          return new Response('', { status: 408, statusText: 'Request timed out.' });
        });
      })
  );
});
