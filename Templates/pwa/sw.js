{% load static %}
const CACHE_NAME = 'wardrobe-v1';
const ASSETS = [
    '{% url "user_login" %}',
    '{% static "css/main.css" %}',
    '{% static "js/three-bg.js" %}',
    '{% url "manifest" %}'
];

// Install Event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS);
        })
    );
});

// Fetch Event
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});
