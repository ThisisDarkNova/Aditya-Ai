// Service Worker for ADITYA PWA capability (offline caching)
const CACHE_NAME = 'aditya-cache-v1';
const ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/app.js',
    '/offline.html',
    '/404.html',
    '/site.webmanifest'
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

self.addEventListener('fetch', (e) => {
    e.respondWith(
        caches.match(e.request).then((response) => {
            return response || fetch(e.request).catch(() => {
                if (e.request.mode === 'navigate') {
                    return caches.match('/offline.html');
                }
            });
        })
    );
});
