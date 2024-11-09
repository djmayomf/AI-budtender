// Global state
let currentLocation = null;
let map = null;
let markers = [];

// Initialize map
function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 13,
        center: { lat: 34.0522, lng: -118.2437 }
    });

    // Try to get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            position => {
                currentLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                map.setCenter(currentLocation);
                loadNearbyDispensaries();
            },
            error => console.error('Error getting location:', error)
        );
    }
}

// Load and display deals
async function loadDeals() {
    try {
        const response = await fetch('/api/v1/deals');
        const data = await response.json();
        
        const dealsGrid = document.querySelector('.deals-grid');
        dealsGrid.innerHTML = data.deals.map(deal => `
            <div class="deal-card">
                <img src="${deal.image_url}" alt="${deal.title}">
                <div class="deal-content">
                    <h3>${deal.title}</h3>
                    <p class="price">$${deal.discounted_price}</p>
                    <p class="savings">Save ${deal.savings}%</p>
                    <p class="location">${deal.dispensary}</p>
                    <button onclick="trackDeal(${deal.id})">Track Price</button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading deals:', error);
    }
}

// Load nearby dispensaries
async function loadNearbyDispensaries() {
    if (!currentLocation) return;

    try {
        const response = await fetch(`/api/v1/dispensaries?lat=${currentLocation.lat}&lng=${currentLocation.lng}`);
        const dispensaries = await response.json();
        
        // Clear existing markers
        markers.forEach(marker => marker.setMap(null));
        markers = [];

        // Add markers and list items
        const list = document.querySelector('.dispensary-list');
        list.innerHTML = '';

        dispensaries.forEach(dispensary => {
            // Add marker
            const marker = new google.maps.Marker({
                position: { lat: dispensary.lat, lng: dispensary.lng },
                map: map,
                title: dispensary.name
            });
            markers.push(marker);

            // Add list item
            list.innerHTML += `
                <div class="dispensary-item">
                    <h3>${dispensary.name}</h3>
                    <p>${dispensary.address}</p>
                    <p>${dispensary.distance} miles away</p>
                    <button onclick="viewDispensary(${dispensary.id})">View Menu</button>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading dispensaries:', error);
    }
}

// Modal functions
function showLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
}

async function handleLogin(event) {
    event.preventDefault();
    const form = event.target;
    const email = form.querySelector('input[type="email"]').value;
    const password = form.querySelector('input[type="password"]').value;

    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (response.ok) {
            window.location.href = '/dashboard';
        } else {
            const data = await response.json();
            alert(data.error);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('An error occurred during login');
    }
}

// Add these functions
class ProductCatalog {
    constructor() {
        this.activeFilters = new Set();
        this.currentCategory = null;
        this.currentSort = 'price-asc';
        this.products = [];
        this.imagePreloader = imagePreloader;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialProducts();
    }

    setupEventListeners() {
        // Category navigation
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const category = e.currentTarget.dataset.category;
                this.switchCategory(category);
            });
        });

        // Subcategory filters
        document.querySelectorAll('.subcategory-group a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const filter = e.currentTarget.dataset.filter;
                this.toggleFilter(filter);
            });
        });

        // Sort options
        document.getElementById('sort-by').addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.updateProductDisplay();
        });
    }

    async loadInitialProducts() {
        try {
            const response = await fetch('/api/v1/products');
            this.products = await response.json();
            
            // Preload product images
            this.imagePreloader.prefetchProductImages(this.products);
            
            this.updateProductDisplay();
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    switchCategory(category) {
        // Hide all panels
        document.querySelectorAll('.subcategories-panel').forEach(panel => {
            panel.classList.remove('active');
        });

        // Show selected category panel
        const panel = document.getElementById(`${category}-panel`);
        if (panel) {
            panel.classList.add('active');
        }

        this.currentCategory = category;
        this.activeFilters.clear();
        this.updateProductDisplay();
    }

    toggleFilter(filter) {
        if (this.activeFilters.has(filter)) {
            this.activeFilters.delete(filter);
        } else {
            this.activeFilters.add(filter);
        }
        this.updateActiveFilters();
        this.updateProductDisplay();
    }

    updateActiveFilters() {
        const container = document.querySelector('.active-filters');
        container.innerHTML = Array.from(this.activeFilters).map(filter => `
            <div class="filter-tag">
                ${filter}
                <button onclick="catalog.toggleFilter('${filter}')">&times;</button>
            </div>
        `).join('');
    }

    async updateProductDisplay() {
        try {
            const params = new URLSearchParams({
                category: this.currentCategory || '',
                filters: Array.from(this.activeFilters).join(','),
                sort: this.currentSort
            });

            const response = await fetch(`/api/v1/products/filter?${params}`);
            const filteredProducts = await response.json();
            
            // Preload images for new products
            this.imagePreloader.prefetchProductImages(filteredProducts);

            const grid = document.querySelector('.product-grid');
            grid.innerHTML = filteredProducts.map(product => 
                this.renderProductCard(product)
            ).join('');
        } catch (error) {
            console.error('Error updating products:', error);
        }
    }

    renderProductCard(product) {
        // Use cached image URL
        const imageUrl = this.imagePreloader.getImage(product.image_url);
        
        return `
            <div class="product-card">
                <img src="${imageUrl}" 
                     alt="${product.name}" 
                     class="product-image"
                     loading="lazy"
                     onerror="this.src='/static/images/fallback.jpg'">
                <div class="product-info">
                    <h3 class="product-title">${product.name}</h3>
                    <div class="product-meta">
                        <span>${product.brand}</span>
                        <div class="product-rating">
                            ${this.renderRating(product.rating)}
                            <span>(${product.review_count})</span>
                        </div>
                    </div>
                    <div class="product-price">
                        $${product.price.toFixed(2)}
                        ${product.discount ? `
                            <span class="discount-badge">${product.discount}% OFF</span>
                        ` : ''}
                    </div>
                    <button onclick="catalog.addToCart(${product.id})" class="add-to-cart-btn">
                        Add to Cart
                    </button>
                </div>
            </div>
        `;
    }

    renderRating(rating) {
        const stars = [];
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                stars.push('<i class="fas fa-star"></i>');
            } else if (i - 0.5 <= rating) {
                stars.push('<i class="fas fa-star-half-alt"></i>');
            } else {
                stars.push('<i class="far fa-star"></i>');
            }
        }
        return stars.join('');
    }

    async addToCart(productId) {
        try {
            const response = await fetch('/api/v1/cart/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ product_id: productId })
            });

            if (response.ok) {
                showNotification('Product added to cart');
                updateCartCount();
            } else {
                throw new Error('Failed to add to cart');
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
            showNotification('Failed to add product to cart', 'error');
        }
    }
}

// Initialize catalog
const catalog = new ProductCatalog();

// Add notification system
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Add these chatbot functions
class ChatBot {
    constructor() {
        this.messages = [];
        this.isMinimized = true;
        this.isFirstInteraction = true;
        this.preferences = {};
        this.init();
    }

    init() {
        // Hide chatbot container initially
        const container = document.getElementById('chatbot');
        container.style.display = 'none';
    }

    show() {
        const trigger = document.getElementById('chat-trigger');
        const container = document.getElementById('chatbot');
        
        trigger.style.display = 'none';
        container.style.display = 'flex';
        container.classList.remove('minimized');
        
        if (this.isFirstInteraction) {
            this.startConversation();
            this.isFirstInteraction = false;
        }
    }

    minimize() {
        const container = document.getElementById('chatbot');
        container.classList.add('minimized');
    }

    close() {
        const trigger = document.getElementById('chat-trigger');
        const container = document.getElementById('chatbot');
        
        container.style.display = 'none';
        trigger.style.display = 'flex';
        this.isMinimized = true;
    }

    startConversation() {
        // Add welcome messages with slight delays
        setTimeout(() => {
            this.addMessage("👋 Hey there! I'm BudBot, your cannabis guide.", 'bot');
        }, 500);

        setTimeout(() => {
            this.addMessage("Let me help you find the perfect product. How would you like to start your day?", 'bot');
        }, 1500);

        setTimeout(() => {
            this.addQuickReplies([
                "🌅 Energetic morning",
                "😌 Relaxing day",
                "🎯 Focused work",
                "🌙 Peaceful sleep"
            ]);
        }, 2500);
    }

    addQuickReplies(options) {
        const messagesContainer = document.getElementById('chat-messages');
        const quickRepliesDiv = document.createElement('div');
        quickRepliesDiv.className = 'quick-replies';
        
        options.forEach(option => {
            const button = document.createElement('button');
            button.className = 'quick-reply-btn';
            button.textContent = option;
            button.onclick = () => this.handleQuickReply(option);
            quickRepliesDiv.appendChild(button);
        });
        
        messagesContainer.appendChild(quickRepliesDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    handleQuickReply(option) {
        this.addMessage(option, 'user');
        
        // Remove quick replies after selection
        const quickReplies = document.querySelector('.quick-replies');
        if (quickReplies) {
            quickReplies.remove();
        }

        // Process the user's choice
        switch(option) {
            case "🌅 Energetic morning":
                this.suggestSativaStrains();
                break;
            case "😌 Relaxing day":
                this.suggestHybridStrains();
                break;
            case "🎯 Focused work":
                this.suggestFocusStrains();
                break;
            case "🌙 Peaceful sleep":
                this.suggestIndicaStrains();
                break;
        }
    }

    async suggestSativaStrains() {
        this.addMessage("Great choice! Let me find some energizing sativa strains for you...", 'bot');
        
        try {
            const response = await fetch('/api/v1/strains/recommend?type=sativa');
            const strains = await response.json();
            
            setTimeout(() => {
                this.addMessage("Here are some perfect morning strains:", 'bot');
                this.addStrainRecommendations(strains);
            }, 1000);
        } catch (error) {
            console.error('Error fetching strains:', error);
        }
    }

    addStrainRecommendations(strains) {
        const messagesContainer = document.getElementById('chat-messages');
        const recommendationsDiv = document.createElement('div');
        recommendationsDiv.className = 'strain-recommendations';
        
        strains.forEach(strain => {
            const strainCard = document.createElement('div');
            strainCard.className = 'strain-card';
            strainCard.innerHTML = `
                <img src="${strain.image_url}" alt="${strain.name}">
                <h4>${strain.name}</h4>
                <p>${strain.thc}% THC</p>
                <p>${strain.effects.join(', ')}</p>
                <button onclick="chatbot.viewStrain('${strain.id}')">View Details</button>
            `;
            recommendationsDiv.appendChild(strainCard);
        });
        
        messagesContainer.appendChild(recommendationsDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async sendMessage() {
        const input = document.getElementById('user-message');
        const message = input.value.trim();
        
        if (message) {
            this.addMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/api/chatbot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message })
                });

                if (!response.ok) throw new Error('Failed to get response');
                
                const data = await response.json();
                this.addMessage(data.response, 'bot');
                
            } catch (error) {
                console.error('Chatbot error:', error);
                this.addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        }
    }

    addMessage(text, sender) {
        const messagesContainer = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = text;
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async getMoodBasedRecommendations(mood) {
        try {
            const response = await fetch('/api/v1/recommendations/mood', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mood })
            });

            if (!response.ok) throw new Error('Failed to get recommendations');
            
            const recommendations = await response.json();
            this.displayRecommendations(recommendations);
        } catch (error) {
            console.error('Error getting recommendations:', error);
        }
    }

    displayRecommendations(recommendations) {
        const messagesContainer = document.getElementById('chat-messages');
        const recsDiv = document.createElement('div');
        recsDiv.className = 'recommendations-container';
        
        recommendations.forEach(strain => {
            const strainCard = document.createElement('div');
            strainCard.className = 'strain-recommendation-card';
            strainCard.innerHTML = `
                <img src="${strain.image_url}" alt="${strain.name}">
                <div class="strain-info">
                    <h4>${strain.name}</h4>
                    <p class="strain-type">${strain.type}</p>
                    <p class="thc-content">THC: ${strain.thc}%</p>
                    <div class="effects">
                        ${strain.effects.map(effect => `
                            <span class="effect-tag">${effect}</span>
                        `).join('')}
                    </div>
                    <div class="rating-buttons">
                        <button onclick="chatbot.rateStrain(${strain.id}, 1)">👎</button>
                        <button onclick="chatbot.rateStrain(${strain.id}, 5)">👍</button>
                    </div>
                </div>
            `;
            recsDiv.appendChild(strainCard);
        });
        
        messagesContainer.appendChild(recsDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async rateStrain(strainId, rating) {
        try {
            await fetch('/api/v1/strains/rate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ strain_id: strainId, rating })
            });
            
            // Get updated recommendations
            const response = await fetch('/api/v1/recommendations/personal');
            const newRecommendations = await response.json();
            
            this.addMessage("Based on your rating, you might also like these:", 'bot');
            this.displayRecommendations(newRecommendations);
        } catch (error) {
            console.error('Error rating strain:', error);
        }
    }
}

// Initialize chatbot
const chatbot = new ChatBot();

function sendMessage() {
    const input = document.getElementById('user-message');
    const message = input.value.trim();
    
    if (message) {
        chatbot.sendMessage(message);
        input.value = '';
    }
}

function toggleChatbot() {
    chatbot.toggleMinimize();
}

// Function to search deals
async function searchDeals() {
    const location = document.getElementById('location').value;
    const dealsContainer = document.getElementById('deals-container');
    
    try {
        const response = await fetch(`/api/deals?location=${encodeURIComponent(location)}`);
        const data = await response.json();
        
        if (data.deals && data.deals.length > 0) {
            dealsContainer.innerHTML = data.deals.map(deal => `
                <div class="col-md-4 mb-4">
                    <div class="deal-card">
                        <img src="${deal.image_url}" alt="${deal.title}" class="deal-image mb-3">
                        <h3>${deal.title}</h3>
                        <p>${deal.dispensary}</p>
                        <div class="deal-price">
                            $${deal.discounted_price}
                            <span class="original-price text-muted text-decoration-line-through">
                                $${deal.original_price}
                            </span>
                        </div>
                        <div class="deal-savings">
                            Save ${deal.savings}%
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            dealsContainer.innerHTML = '<p class="text-center">No deals found in your area</p>';
        }
    } catch (error) {
        console.error('Error fetching deals:', error);
        dealsContainer.innerHTML = '<p class="text-center text-danger">Error loading deals</p>';
    }
}

// Load initial deals
document.addEventListener('DOMContentLoaded', () => {
    searchDeals();
}); 