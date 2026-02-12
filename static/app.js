/**
 * REST API Frontend Application
 * Handles authentication, CRUD operations, and UI interactions
 */

const API_BASE = '';  // Same origin

// ==================== State Management ====================
const state = {
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    currentPage: {
        products: 1,
        users: 1
    }
};

// ==================== API Helper ====================
async function api(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || data.error || 'An error occurred');
        }
        
        return data;
    } catch (error) {
        if (error.message.includes('Token has expired')) {
            logout();
        }
        throw error;
    }
}

// ==================== Toast Notifications ====================
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle'
    };
    
    toast.innerHTML = `
        <i class="fas ${icons[type]}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close">&times;</button>
    `;
    
    container.appendChild(toast);
    
    toast.querySelector('.toast-close').addEventListener('click', () => {
        toast.remove();
    });
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// ==================== Authentication ====================
function saveAuth(token, user) {
    state.token = token;
    state.user = user;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showPage('loginPage');
}

function checkAuth() {
    if (state.token && state.user) {
        showPage('dashboardPage');
        loadDashboard();
    } else {
        showPage('loginPage');
    }
}

// ==================== Page Navigation ====================
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
    
    if (pageId === 'dashboardPage') {
        updateUserInfo();
    }
}

function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionId}Section`).classList.add('active');
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
    
    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'products': 'Products',
        'users': 'Users',
        'api-keys': 'API Keys'
    };
    document.getElementById('pageTitle').textContent = titles[sectionId] || sectionId;
    
    // Load section data
    switch (sectionId) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'products':
            loadProducts();
            loadCategories();
            break;
        case 'users':
            loadUsers();
            break;
        case 'api-keys':
            loadApiKeys();
            break;
    }
}

function updateUserInfo() {
    if (state.user) {
        document.getElementById('userName').textContent = state.user.username;
        document.getElementById('userRole').textContent = state.user.role;
        document.getElementById('userRole').className = `badge badge-${state.user.role === 'admin' ? 'primary' : 'success'}`;
    }
}

// ==================== Dashboard ====================
async function loadDashboard() {
    try {
        // Load stats
        const stats = await api('/api/stats');
        document.getElementById('totalUsers').textContent = stats.data.total_users;
        document.getElementById('activeUsers').textContent = stats.data.active_users;
        document.getElementById('totalProducts').textContent = stats.data.total_products;
        document.getElementById('availableProducts').textContent = stats.data.available_products;
        
        // Load health
        const health = await api('/api/health');
        document.getElementById('apiStatus').textContent = health.status;
        document.getElementById('apiStatus').className = `status-badge ${health.status === 'healthy' ? 'healthy' : 'unhealthy'}`;
        document.getElementById('dbStatus').textContent = health.database;
        document.getElementById('dbStatus').className = `status-badge ${health.database === 'healthy' ? 'healthy' : 'unhealthy'}`;
        document.getElementById('apiVersion').textContent = health.version;
        document.getElementById('lastCheck').textContent = new Date().toLocaleTimeString();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================== Products ====================
async function loadProducts(page = 1) {
    const tbody = document.getElementById('productsTableBody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading"><div class="spinner"></div></td></tr>';
    
    try {
        const search = document.getElementById('productSearch').value;
        const category = document.getElementById('categoryFilter').value;
        const sortBy = document.getElementById('sortBy').value;
        
        let url = `/api/products?page=${page}&per_page=10&sort_by=${sortBy}&sort_order=desc`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (category) url += `&category=${encodeURIComponent(category)}`;
        
        const data = await api(url);
        
        if (data.items.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7">
                        <div class="empty-state">
                            <i class="fas fa-box-open"></i>
                            <p>No products found</p>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = data.items.map(product => `
                <tr>
                    <td>${product.id}</td>
                    <td><strong>${escapeHtml(product.name)}</strong></td>
                    <td><span class="badge badge-primary">${escapeHtml(product.category || 'N/A')}</span></td>
                    <td>$${product.price.toFixed(2)}</td>
                    <td>${product.quantity}</td>
                    <td>
                        <span class="badge ${product.is_available ? 'badge-success' : 'badge-danger'}">
                            ${product.is_available ? 'Available' : 'Unavailable'}
                        </span>
                    </td>
                    <td>
                        <div class="table-actions">
                            <button class="btn btn-sm btn-outline" onclick="editProduct(${product.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
        
        renderPagination('productsPagination', data.pagination, loadProducts);
        state.currentPage.products = page;
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state"><p>Error loading products</p></td></tr>`;
        showToast(error.message, 'error');
    }
}

async function loadCategories() {
    try {
        const data = await api('/api/products/categories');
        const select = document.getElementById('categoryFilter');
        select.innerHTML = '<option value="">All Categories</option>' +
            data.data.map(cat => `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`).join('');
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

function showProductModal(product = null) {
    const modal = document.getElementById('productModal');
    const title = document.getElementById('productModalTitle');
    const form = document.getElementById('productForm');
    
    form.reset();
    
    if (product) {
        title.textContent = 'Edit Product';
        document.getElementById('productId').value = product.id;
        document.getElementById('productName').value = product.name;
        document.getElementById('productCategory').value = product.category || '';
        document.getElementById('productDescription').value = product.description || '';
        document.getElementById('productPrice').value = product.price;
        document.getElementById('productQuantity').value = product.quantity;
        document.getElementById('productAvailable').checked = product.is_available;
    } else {
        title.textContent = 'Add Product';
        document.getElementById('productId').value = '';
    }
    
    modal.classList.add('active');
}

async function editProduct(id) {
    try {
        const data = await api(`/api/products/${id}`);
        showProductModal(data.data);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function saveProduct(e) {
    e.preventDefault();
    
    const id = document.getElementById('productId').value;
    const productData = {
        name: document.getElementById('productName').value,
        category: document.getElementById('productCategory').value,
        description: document.getElementById('productDescription').value,
        price: parseFloat(document.getElementById('productPrice').value),
        quantity: parseInt(document.getElementById('productQuantity').value),
        is_available: document.getElementById('productAvailable').checked
    };
    
    try {
        if (id) {
            await api(`/api/products/${id}`, {
                method: 'PUT',
                body: JSON.stringify(productData)
            });
            showToast('Product updated successfully');
        } else {
            await api('/api/products', {
                method: 'POST',
                body: JSON.stringify(productData)
            });
            showToast('Product created successfully');
        }
        
        closeModals();
        loadProducts(state.currentPage.products);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteProduct(id) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
        await api(`/api/products/${id}`, { method: 'DELETE' });
        showToast('Product deleted successfully');
        loadProducts(state.currentPage.products);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================== Users ====================
async function loadUsers(page = 1) {
    const tbody = document.getElementById('usersTableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading"><div class="spinner"></div></td></tr>';
    
    try {
        const search = document.getElementById('userSearch').value;
        const role = document.getElementById('roleFilter').value;
        
        let url = `/api/users?page=${page}&per_page=10`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (role) url += `&role=${encodeURIComponent(role)}`;
        
        const data = await api(url);
        
        if (data.items.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6">
                        <div class="empty-state">
                            <i class="fas fa-users"></i>
                            <p>No users found</p>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = data.items.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td><strong>${escapeHtml(user.username)}</strong></td>
                    <td>${escapeHtml(user.email)}</td>
                    <td>
                        <span class="badge ${user.role === 'admin' ? 'badge-primary' : 'badge-success'}">
                            ${user.role}
                        </span>
                    </td>
                    <td>
                        <span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">
                            ${user.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>${formatDate(user.created_at)}</td>
                </tr>
            `).join('');
        }
        
        renderPagination('usersPagination', data.pagination, loadUsers);
        state.currentPage.users = page;
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state"><p>Error loading users</p></td></tr>`;
        showToast(error.message, 'error');
    }
}

// ==================== API Keys ====================
async function loadApiKeys() {
    const tbody = document.getElementById('apiKeysTableBody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading"><div class="spinner"></div></td></tr>';
    
    try {
        const data = await api('/api/auth/api-keys');
        
        if (data.data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6">
                        <div class="empty-state">
                            <i class="fas fa-key"></i>
                            <p>No API keys found</p>
                        </div>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = data.data.map(key => `
                <tr>
                    <td>${key.id}</td>
                    <td>${escapeHtml(key.name)}</td>
                    <td><code>${escapeHtml(key.key)}</code></td>
                    <td>
                        <span class="badge ${key.is_active ? 'badge-success' : 'badge-danger'}">
                            ${key.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>${key.expires_at ? formatDate(key.expires_at) : 'Never'}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="deleteApiKey(${key.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state"><p>Error loading API keys</p></td></tr>`;
        showToast(error.message, 'error');
    }
}

async function createApiKey(e) {
    e.preventDefault();
    
    const name = document.getElementById('apiKeyName').value;
    const expiresDays = parseInt(document.getElementById('apiKeyExpires').value);
    
    try {
        const data = await api('/api/auth/api-keys', {
            method: 'POST',
            body: JSON.stringify({ name, expires_days: expiresDays })
        });
        
        closeModals();
        
        // Show the new key
        document.getElementById('newKeyValue').textContent = data.data.key;
        document.getElementById('newKeyModal').classList.add('active');
        
        loadApiKeys();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function deleteApiKey(id) {
    if (!confirm('Are you sure you want to delete this API key?')) return;
    
    try {
        await api(`/api/auth/api-keys/${id}`, { method: 'DELETE' });
        showToast('API key deleted successfully');
        loadApiKeys();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ==================== Utility Functions ====================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function renderPagination(containerId, pagination, loadFunction) {
    const container = document.getElementById(containerId);
    
    if (pagination.total_pages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = `
        <button ${pagination.page <= 1 ? 'disabled' : ''} onclick="${loadFunction.name}(${pagination.page - 1})">
            <i class="fas fa-chevron-left"></i>
        </button>
        <span>Page ${pagination.page} of ${pagination.total_pages}</span>
        <button ${pagination.page >= pagination.total_pages ? 'disabled' : ''} onclick="${loadFunction.name}(${pagination.page + 1})">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;
}

function closeModals() {
    document.querySelectorAll('.modal').forEach(modal => {
        modal.classList.remove('active');
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== Event Listeners ====================
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    checkAuth();
    
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}Form`).classList.add('active');
        });
    });
    
    // Login form
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const data = await api('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            saveAuth(data.data.token, data.data.user);
            showToast('Login successful!');
            showPage('dashboardPage');
            loadDashboard();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Register form
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('regUsername').value;
        const email = document.getElementById('regEmail').value;
        const password = document.getElementById('regPassword').value;
        
        try {
            const data = await api('/api/auth/register', {
                method: 'POST',
                body: JSON.stringify({ username, email, password })
            });
            
            saveAuth(data.data.token, data.data.user);
            showToast('Registration successful!');
            showPage('dashboardPage');
            loadDashboard();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', () => {
        logout();
        showToast('Logged out successfully');
    });
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            showSection(item.dataset.section);
        });
    });
    
    // Mobile menu toggle
    document.getElementById('menuToggle').addEventListener('click', () => {
        document.querySelector('.sidebar').classList.toggle('active');
    });
    
    // Search with debounce
    document.getElementById('productSearch').addEventListener('input', debounce(() => loadProducts(1), 300));
    document.getElementById('userSearch').addEventListener('input', debounce(() => loadUsers(1), 300));
    
    // Filters
    document.getElementById('categoryFilter').addEventListener('change', () => loadProducts(1));
    document.getElementById('sortBy').addEventListener('change', () => loadProducts(1));
    document.getElementById('roleFilter').addEventListener('change', () => loadUsers(1));
    
    // Product modal
    document.getElementById('addProductBtn').addEventListener('click', () => showProductModal());
    document.getElementById('productForm').addEventListener('submit', saveProduct);
    
    // API Key modal
    document.getElementById('createApiKeyBtn').addEventListener('click', () => {
        document.getElementById('apiKeyForm').reset();
        document.getElementById('apiKeyModal').classList.add('active');
    });
    document.getElementById('apiKeyForm').addEventListener('submit', createApiKey);
    
    // Copy API key
    document.getElementById('copyKeyBtn').addEventListener('click', () => {
        const key = document.getElementById('newKeyValue').textContent;
        navigator.clipboard.writeText(key).then(() => {
            showToast('API key copied to clipboard');
        });
    });
    
    // Modal close buttons
    document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
        btn.addEventListener('click', closeModals);
    });
    
    // Close modal on backdrop click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModals();
        });
    });
    
    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', (e) => {
        const sidebar = document.querySelector('.sidebar');
        const menuToggle = document.getElementById('menuToggle');
        
        if (sidebar.classList.contains('active') && 
            !sidebar.contains(e.target) && 
            !menuToggle.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });
});
