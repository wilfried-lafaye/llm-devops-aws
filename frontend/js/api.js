/**
 * API Client for Air Quality Dashboard
 * Handles all communication with the backend API
 */

const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/v1'
    : '/api/v1';

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        // Handle 204 No Content
        if (response.status === 204) {
            return null;
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

/**
 * Check API health status
 */
async function checkApiHealth() {
    try {
        const baseUrl = API_BASE_URL.replace('/api/v1', '');
        const response = await fetch(`${baseUrl}/health`);
        return response.ok;
    } catch {
        return false;
    }
}

// ============== Records API ==============

/**
 * Get air quality records with optional filters
 */
async function getRecords(params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.commune) queryParams.append('commune', params.commune);
    if (params.region) queryParams.append('region', params.region);
    if (params.annee) queryParams.append('annee', params.annee);
    if (params.page) queryParams.append('page', params.page);
    if (params.page_size) queryParams.append('page_size', params.page_size);
    
    const queryString = queryParams.toString();
    const endpoint = `/records${queryString ? `?${queryString}` : ''}`;
    
    return apiFetch(endpoint);
}

/**
 * Get a single record by ID
 */
async function getRecordById(id) {
    return apiFetch(`/records/${id}`);
}

/**
 * Create a new record
 */
async function createRecord(recordData) {
    return apiFetch('/records', {
        method: 'POST',
        body: JSON.stringify(recordData),
    });
}

/**
 * Update an existing record
 */
async function updateRecord(id, updateData) {
    return apiFetch(`/records/${id}`, {
        method: 'PUT',
        body: JSON.stringify(updateData),
    });
}

/**
 * Delete a record
 */
async function deleteRecord(id) {
    return apiFetch(`/records/${id}`, {
        method: 'DELETE',
    });
}

// ============== Metadata API ==============

/**
 * Get list of all regions
 */
async function getRegions() {
    return apiFetch('/regions');
}

/**
 * Get list of all communes
 */
async function getCommunes(region = null) {
    const queryString = region ? `?region=${encodeURIComponent(region)}` : '';
    return apiFetch(`/communes${queryString}`);
}

/**
 * Get list of available years
 */
async function getYears() {
    return apiFetch('/years');
}

// ============== Statistics API ==============

/**
 * Get statistics for a region
 */
async function getRegionStats(region, annee = null) {
    const queryString = annee ? `?annee=${annee}` : '';
    return apiFetch(`/stats/region/${encodeURIComponent(region)}${queryString}`);
}

/**
 * Get statistics for a commune
 */
async function getCommuneStats(commune) {
    return apiFetch(`/stats/commune/${encodeURIComponent(commune)}`);
}

/**
 * Get pollutant trend over time
 */
async function getPollutantTrend(pollutant, params = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.region) queryParams.append('region', params.region);
    if (params.commune) queryParams.append('commune', params.commune);
    
    const queryString = queryParams.toString();
    const endpoint = `/trends/${pollutant}${queryString ? `?${queryString}` : ''}`;
    
    return apiFetch(endpoint);
}

/**
 * Compare multiple regions
 */
async function compareRegions(regions, annee = null) {
    const regionsParam = Array.isArray(regions) ? regions.join(',') : regions;
    const queryString = annee 
        ? `?regions=${encodeURIComponent(regionsParam)}&annee=${annee}`
        : `?regions=${encodeURIComponent(regionsParam)}`;
    
    return apiFetch(`/compare${queryString}`);
}

/**
 * Get dataset summary
 */
async function getSummary() {
    return apiFetch('/summary');
}

// ============== Export API functions ==============

window.AirQualityAPI = {
    checkApiHealth,
    getRecords,
    getRecordById,
    createRecord,
    updateRecord,
    deleteRecord,
    getRegions,
    getCommunes,
    getYears,
    getRegionStats,
    getCommuneStats,
    getPollutantTrend,
    compareRegions,
    getSummary,
};
