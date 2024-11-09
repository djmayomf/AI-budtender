class ImagePreloader {
    constructor() {
        this.imageCache = new Map();
        this.preloadQueue = [];
        this.isLoading = false;
        this.maxConcurrent = 5; // Maximum concurrent image loads
        this.initServiceWorker();
    }

    async initServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                console.log('ServiceWorker registered:', registration);
            } catch (error) {
                console.error('ServiceWorker registration failed:', error);
            }
        }
    }

    preloadImages(urls) {
        urls.forEach(url => {
            if (!this.imageCache.has(url)) {
                this.preloadQueue.push(url);
            }
        });
        this.processQueue();
    }

    async processQueue() {
        if (this.isLoading || this.preloadQueue.length === 0) return;
        
        this.isLoading = true;
        const batch = this.preloadQueue.splice(0, this.maxConcurrent);
        
        const loadPromises = batch.map(url => this.loadImage(url));
        await Promise.allSettled(loadPromises);
        
        this.isLoading = false;
        if (this.preloadQueue.length > 0) {
            this.processQueue();
        }
    }

    async loadImage(url) {
        try {
            const response = await fetch(url);
            const blob = await response.blob();
            const objectURL = URL.createObjectURL(blob);
            this.imageCache.set(url, objectURL);
            
            // Cache in ServiceWorker
            if ('caches' in window) {
                const cache = await caches.open('image-cache');
                await cache.put(url, new Response(blob));
            }
            
            return objectURL;
        } catch (error) {
            console.error(`Failed to preload image: ${url}`, error);
            return url;
        }
    }

    getImage(url) {
        return this.imageCache.get(url) || url;
    }

    prefetchProductImages(products) {
        const imageUrls = products
            .map(product => product.image_url)
            .filter(url => url && !this.imageCache.has(url));
        this.preloadImages(imageUrls);
    }

    clearOldCache() {
        if (this.imageCache.size > 1000) { // Limit cache size
            const oldestEntries = Array.from(this.imageCache.entries())
                .slice(0, 100)
                .map(([url]) => url);
            
            oldestEntries.forEach(url => {
                const objectURL = this.imageCache.get(url);
                URL.revokeObjectURL(objectURL);
                this.imageCache.delete(url);
            });
        }
    }
}

// Initialize the image preloader
const imagePreloader = new ImagePreloader();
export default imagePreloader; 