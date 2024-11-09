const CACHE_NAME = 'cannabis-app-cache-v1';
const IMAGE_CACHE_NAME = 'image-cache';

// Assets to cache immediately
const PRECACHE_ASSETS = [
    '/',
    '/static/css/main.css',
    '/static/css/chatbot.css',
    '/static/js/main.js',
    '/static/images/logo.svg',
    '/static/images/hero-bg.jpg'
];

self.addEventListener('install', event => {
    event.waitUntil(
        Promise.all([
            caches.open(CACHE_NAME).then(cache => {
                return cache.addAll(PRECACHE_ASSETS);
            }),
            caches.open(IMAGE_CACHE_NAME)
        ])
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // Handle image requests
    if (event.request.destination === 'image') {
        event.respondWith(handleImageRequest(event.request));
        return;
    }
    
    // Handle other requests
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request).then(response => {
                // Cache successful responses
                if (response.ok) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            });
        })
    );
});

async function handleImageRequest(request) {
    // Try cache first
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }
    
    // Fetch and cache if not found
    try {
        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(IMAGE_CACHE_NAME);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.error('Image fetch failed:', error);
        // Return a fallback image
        return caches.match('/static/images/fallback.jpg');
    }
}

// Clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName !== IMAGE_CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
}); 