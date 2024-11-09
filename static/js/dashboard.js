class Dashboard {
    constructor() {
        this.deals = [];
        this.alerts = [];
        this.init();
    }

    async init() {
        await this.loadDashboard();
        this.setupEventListeners();
        this.initCharts();
    }

    async loadDashboard() {
        try {
            const response = await fetch('/api/v1/users/dashboard');
            if (!response.ok) throw new Error('Failed to load dashboard');
            
            const data = await response.json();
            this.updateDashboard(data);
        } catch (error) {
            console.error('Dashboard load error:', error);
            showError('Failed to load dashboard data');
        }
    }

    updateDashboard(data) {
        // Update favorite deals
        const dealsList = document.getElementById('favorite-deals');
        dealsList.innerHTML = data.favorite_deals.map(deal => `
            <div class="deal-card">
                <img src="${deal.image_url}" alt="${deal.title}">
                <h3>${deal.title}</h3>
                <p class="price">$${deal.discounted_price}</p>
                <p class="savings">Save ${deal.savings}%</p>
                <button onclick="dashboard.trackDeal(${deal.id})">
                    Track Price
                </button>
            </div>
        `).join('');

        // Update price alerts
        this.updateAlerts(data.price_alerts);

        // Update notifications
        this.updateNotifications(data.notifications);
    }

    async createPriceAlert(productId, targetPrice) {
        try {
            const response = await fetch('/api/v1/alerts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_id: productId,
                    target_price: targetPrice
                })
            });

            if (!response.ok) throw new Error('Failed to create alert');
            showSuccess('Price alert created successfully');
        } catch (error) {
            console.error('Alert creation error:', error);
            showError('Failed to create price alert');
        }
    }

    initCharts() {
        // Initialize price history chart
        const ctx = document.getElementById('price-history-chart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.deals.map(d => d.date),
                datasets: [{
                    label: 'Price History',
                    data: this.deals.map(d => d.price),
                    borderColor: '#43A047',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Initialize dashboard
const dashboard = new Dashboard(); 