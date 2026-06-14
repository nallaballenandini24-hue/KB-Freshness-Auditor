// Main application JavaScript

const API_BASE_URL = '/api';

// Navigation
document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    loadDashboard();
});

function setupNavigation() {
    document.getElementById('nav-dashboard')?.addEventListener('click', (e) => {
        e.preventDefault();
        loadDashboard();
    });

    document.getElementById('nav-kb')?.addEventListener('click', (e) => {
        e.preventDefault();
        loadKnowledgeBase();
    });

    document.getElementById('nav-tickets')?.addEventListener('click', (e) => {
        e.preventDefault();
        loadTickets();
    });

    document.getElementById('nav-audit')?.addEventListener('click', (e) => {
        e.preventDefault();
        loadAudit();
    });

    document.getElementById('nav-recommendations')?.addEventListener('click', (e) => {
        e.preventDefault();
        loadRecommendations();
    });

    document.getElementById('refresh-btn')?.addEventListener('click', () => {
        location.reload();
    });
}

// API Utility Functions
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    try {
        const response = await fetch(url, { ...defaultOptions, ...options });
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert('Error: ' + error.message, 'danger');
        throw error;
    }
}

// Alert Helper
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    const contentArea = document.getElementById('content-area');
    if (contentArea.firstChild?.classList?.contains('alert')) {
        contentArea.firstChild.remove();
    }
    contentArea.insertAdjacentHTML('afterbegin', alertHtml);
}

// Loading State
function showLoading(show = true) {
    const contentArea = document.getElementById('content-area');
    if (show) {
        contentArea.innerHTML = `
            <div class="text-center py-5">
                <div class="loading"></div>
                <p class="mt-3">Loading...</p>
            </div>
        `;
    }
}

// Format Date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// Format Number
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Active Navigation
function setActiveNav(navId) {
    document.querySelectorAll('.navbar-nav .nav-link').forEach((link) => {
        link.classList.remove('active');
    });
    document.getElementById(navId)?.classList.add('active');
}
