/**
 * Main Application for Air Quality Dashboard
 * Handles navigation, data loading, and UI interactions
 */

// Application State
const AppState = {
    currentPage: 'dashboard',
    data: [],
    regions: [],
    years: [],
    summary: null,
    pagination: {
        page: 1,
        pageSize: 20,
        total: 0
    },
    filters: {
        region: '',
        year: '',
        commune: ''
    },
    map: null,
    mapMarkers: []
};

// ============== Initialization ==============

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🌬️ Air Quality Dashboard initializing...');
    
    // Setup navigation
    setupNavigation();
    
    // Setup filters
    setupFilters();
    
    // Setup pagination
    setupPagination();
    
    // Setup modal
    setupModal();
    
    // Check API health
    await checkApiStatus();
    
    // Load initial data
    await loadInitialData();
    
    console.log('✅ Dashboard initialized');
});

// ============== API Status ==============

async function checkApiStatus() {
    const statusElement = document.getElementById('api-status');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('span:last-child');
    
    try {
        const isHealthy = await window.AirQualityAPI.checkApiHealth();
        
        if (isHealthy) {
            statusDot.className = 'status-dot connected';
            statusText.textContent = 'API connectée';
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        statusDot.className = 'status-dot error';
        statusText.textContent = 'API déconnectée';
        showToast('Impossible de se connecter à l\'API', 'error');
    }
}

// ============== Navigation ==============

function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            navigateTo(page);
        });
    });
}

function navigateTo(page) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.page === page);
    });
    
    // Update pages
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });
    
    AppState.currentPage = page;
    
    // Initialize page-specific content
    if (page === 'map') {
        initializeMap();
    } else if (page === 'trends') {
        loadTrendData();
    }
}

// ============== Data Loading ==============

async function loadInitialData() {
    showLoading(true);
    
    try {
        // Load metadata
        const [regionsData, yearsData, summaryData] = await Promise.all([
            window.AirQualityAPI.getRegions(),
            window.AirQualityAPI.getYears(),
            window.AirQualityAPI.getSummary()
        ]);
        
        AppState.regions = regionsData.regions;
        AppState.years = yearsData.years;
        AppState.summary = summaryData;
        
        // Populate filter dropdowns
        populateFilters();
        
        // Load records
        await loadRecords();
        
        // Update dashboard stats
        updateDashboardStats();
        
        // Create charts
        createDashboardCharts();
        
    } catch (error) {
        console.error('Error loading initial data:', error);
        showToast('Erreur lors du chargement des données', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadRecords() {
    try {
        const result = await window.AirQualityAPI.getRecords({
            region: AppState.filters.region,
            annee: AppState.filters.year,
            commune: AppState.filters.commune,
            page: AppState.pagination.page,
            page_size: AppState.pagination.pageSize
        });
        
        AppState.data = result.data;
        AppState.pagination.total = result.total;
        
        // Update table
        updateDataTable();
        updatePaginationInfo();
        
    } catch (error) {
        console.error('Error loading records:', error);
        showToast('Erreur lors du chargement des enregistrements', 'error');
    }
}

// ============== Filters ==============

function setupFilters() {
    // Dashboard filters
    document.getElementById('filter-region')?.addEventListener('change', async (e) => {
        AppState.filters.region = e.target.value;
        AppState.pagination.page = 1;
        await loadRecords();
        updateDashboardStats();
        createDashboardCharts();
    });
    
    document.getElementById('filter-year')?.addEventListener('change', async (e) => {
        AppState.filters.year = e.target.value;
        AppState.pagination.page = 1;
        await loadRecords();
        updateDashboardStats();
        createDashboardCharts();
    });
    
    // Data page filters
    document.getElementById('data-region')?.addEventListener('change', async (e) => {
        AppState.filters.region = e.target.value;
        AppState.pagination.page = 1;
        await loadRecords();
    });
    
    document.getElementById('search-commune')?.addEventListener('input', debounce(async (e) => {
        AppState.filters.commune = e.target.value;
        AppState.pagination.page = 1;
        await loadRecords();
    }, 300));
    
    document.getElementById('btn-refresh')?.addEventListener('click', loadRecords);
    
    // Map filters
    document.getElementById('map-pollutant')?.addEventListener('change', updateMapMarkers);
    document.getElementById('map-year')?.addEventListener('change', updateMapMarkers);
    
    // Trend filters
    document.getElementById('trend-pollutant')?.addEventListener('change', loadTrendData);
    document.getElementById('trend-region')?.addEventListener('change', loadTrendData);
}

function populateFilters() {
    const regionSelects = ['filter-region', 'data-region', 'trend-region'];
    const yearSelects = ['filter-year', 'map-year'];
    
    regionSelects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            // Keep first option
            select.innerHTML = select.options[0].outerHTML;
            AppState.regions.forEach(region => {
                select.add(new Option(region, region));
            });
        }
    });
    
    yearSelects.forEach(id => {
        const select = document.getElementById(id);
        if (select) {
            select.innerHTML = select.options[0].outerHTML;
            AppState.years.forEach(year => {
                select.add(new Option(year, year));
            });
        }
    });
}

// ============== Dashboard ==============

function updateDashboardStats() {
    const data = AppState.data;
    const summary = AppState.summary;
    
    // Calculate averages from current data
    const calcAvg = (arr, key) => {
        const values = arr.filter(d => d[key] != null).map(d => d[key]);
        return values.length ? (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1) : '--';
    };
    
    document.getElementById('stat-no2').textContent = calcAvg(data, 'no2');
    document.getElementById('stat-pm10').textContent = calcAvg(data, 'pm10');
    document.getElementById('stat-pm25').textContent = calcAvg(data, 'pm25');
    document.getElementById('stat-o3').textContent = calcAvg(data, 'o3');
    
    // Update summary stats
    if (summary) {
        document.getElementById('total-records').textContent = summary.total_records.toLocaleString();
        document.getElementById('total-communes').textContent = summary.total_communes.toLocaleString();
        document.getElementById('total-regions').textContent = summary.total_regions.toLocaleString();
    }
}

function createDashboardCharts() {
    if (AppState.data.length === 0) return;
    
    window.AirQualityCharts.createEvolutionChart('chart-evolution', AppState.data);
    window.AirQualityCharts.createRegionsChart('chart-regions', AppState.data);
}

// ============== Data Table ==============

function updateDataTable() {
    const tbody = document.getElementById('data-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (AppState.data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; padding: 40px; color: var(--text-secondary);">
                    Aucune donnée trouvée
                </td>
            </tr>
        `;
        return;
    }
    
    AppState.data.forEach(record => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${record.commune}</td>
            <td>${record.region}</td>
            <td>${record.annee}</td>
            <td>${record.no2 ?? '-'}</td>
            <td>${record.pm10 ?? '-'}</td>
            <td>${record.pm25 ?? '-'}</td>
            <td>${record.o3 ?? '-'}</td>
            <td>
                <button class="btn-danger" onclick="handleDeleteRecord(${record.id})">🗑️</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// ============== Pagination ==============

function setupPagination() {
    document.getElementById('btn-prev')?.addEventListener('click', () => {
        if (AppState.pagination.page > 1) {
            AppState.pagination.page--;
            loadRecords();
        }
    });
    
    document.getElementById('btn-next')?.addEventListener('click', () => {
        const maxPage = Math.ceil(AppState.pagination.total / AppState.pagination.pageSize);
        if (AppState.pagination.page < maxPage) {
            AppState.pagination.page++;
            loadRecords();
        }
    });
}

function updatePaginationInfo() {
    const maxPage = Math.ceil(AppState.pagination.total / AppState.pagination.pageSize) || 1;
    
    document.getElementById('pagination-info').textContent = 
        `Page ${AppState.pagination.page} / ${maxPage} (${AppState.pagination.total} résultats)`;
    
    document.getElementById('btn-prev').disabled = AppState.pagination.page <= 1;
    document.getElementById('btn-next').disabled = AppState.pagination.page >= maxPage;
}

// ============== Map ==============

function initializeMap() {
    if (AppState.map) return;
    
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;
    
    // Initialize Leaflet map
    AppState.map = L.map('map').setView([46.603354, 1.888334], 6);
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(AppState.map);
    
    // Add markers
    updateMapMarkers();
}

function updateMapMarkers() {
    if (!AppState.map) return;
    
    // Clear existing markers
    AppState.mapMarkers.forEach(marker => marker.remove());
    AppState.mapMarkers = [];
    
    const pollutant = document.getElementById('map-pollutant')?.value || 'no2';
    const yearFilter = document.getElementById('map-year')?.value;
    
    // Filter data
    let filteredData = AppState.data;
    if (yearFilter) {
        filteredData = filteredData.filter(d => d.annee == yearFilter);
    }
    
    // Add markers
    filteredData.forEach(record => {
        if (record.latitude && record.longitude && record[pollutant]) {
            const value = record[pollutant];
            const color = getColorForValue(value, pollutant);
            
            const marker = L.circleMarker([record.latitude, record.longitude], {
                radius: 8,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            });
            
            marker.bindPopup(`
                <strong>${record.commune}</strong><br>
                ${record.region}<br>
                <hr style="margin: 8px 0;">
                ${pollutant.toUpperCase()}: ${value} µg/m³<br>
                Année: ${record.annee}
            `);
            
            marker.addTo(AppState.map);
            AppState.mapMarkers.push(marker);
        }
    });
}

function getColorForValue(value, pollutant) {
    // Thresholds based on WHO guidelines
    const thresholds = {
        no2: { low: 20, high: 40 },
        pm10: { low: 15, high: 45 },
        pm25: { low: 10, high: 25 },
        o3: { low: 60, high: 100 }
    };
    
    const t = thresholds[pollutant] || { low: 20, high: 40 };
    
    if (value <= t.low) return '#22c55e';  // Green
    if (value <= t.high) return '#f59e0b'; // Yellow
    return '#ef4444';                       // Red
}

// ============== Trends ==============

async function loadTrendData() {
    const pollutant = document.getElementById('trend-pollutant')?.value || 'no2';
    const region = document.getElementById('trend-region')?.value || '';
    
    try {
        const result = await window.AirQualityAPI.getPollutantTrend(pollutant, { region });
        
        // Create chart
        window.AirQualityCharts.createTrendChart('chart-trend', result.data, pollutant);
        
        // Update analysis
        const analysis = window.AirQualityCharts.analyzeTrend(result.data, pollutant);
        document.getElementById('trend-analysis-text').innerHTML = analysis.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
    } catch (error) {
        console.error('Error loading trend data:', error);
        showToast('Erreur lors du chargement des tendances', 'error');
    }
}

// ============== CRUD Operations ==============

async function handleDeleteRecord(id) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet enregistrement ?')) {
        return;
    }
    
    try {
        await window.AirQualityAPI.deleteRecord(id);
        showToast('Enregistrement supprimé', 'success');
        await loadRecords();
    } catch (error) {
        console.error('Error deleting record:', error);
        showToast('Erreur lors de la suppression', 'error');
    }
}

// ============== Modal ==============

function setupModal() {
    const overlay = document.getElementById('modal-overlay');
    const closeBtn = document.getElementById('modal-close');
    const cancelBtn = document.getElementById('modal-cancel');
    
    closeBtn?.addEventListener('click', closeModal);
    cancelBtn?.addEventListener('click', closeModal);
    
    overlay?.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });
}

function openModal(title, content) {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-body').innerHTML = content;
    document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
}

// ============== Utilities ==============

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showLoading(show) {
    // Could implement a loading overlay
    console.log(show ? 'Loading...' : 'Done loading');
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

// Make functions globally available
window.handleDeleteRecord = handleDeleteRecord;
window.openModal = openModal;
window.closeModal = closeModal;
