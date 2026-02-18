import axios from 'axios';
import logger from '../utils/logger';

// Standardize API_BASE_URL to always have a trailing slash
const getApiBaseUrl = () => {
    let url = process.env.REACT_APP_API_BASE_URL || '/api/v1/';
    if (!url.endsWith('/')) {
        url += '/';
    }
    return url;
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance with default config
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
    (config) => {
        logger.api(config, true);
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error) => {
        logger.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
    }
);

// Location API
export const locationAPI = {
    search: async (query) => {
        const response = await apiClient.post('locations/search', { query });
        return response.data;
    },

    getMunicipalities: async (params = {}) => {
        const response = await apiClient.get('locations/municipalities', { params });
        return response.data;
    },

    getMunicipality: async (id) => {
        const response = await apiClient.get(`locations/municipalities/${id}`);
        return response.data;
    },

    getOMIZones: async (municipalityId) => {
        const response = await apiClient.get(`locations/municipalities/${municipalityId}/omi-zones`);
        return response.data;
    },

    getOMIZone: async (zoneId) => {
        const response = await apiClient.get(`locations/omi-zones/${zoneId}`);
        return response.data;
    },

    discover: async (bounds, zoom) => {
        if (!bounds || typeof bounds.getSouthWest !== 'function') {
            logger.error('Invalid bounds passed to discover');
            return [];
        }
        const params = {
            min_lat: bounds.getSouthWest().lat,
            min_lon: bounds.getSouthWest().lng,
            max_lat: bounds.getNorthEast().lat,
            max_lon: bounds.getNorthEast().lng,
            zoom
        };
        const response = await apiClient.get('locations/discover', { params });
        return response.data;
    },

    getFeatured: async () => {
        const response = await apiClient.get('locations/featured');
        return response.data;
    },
};

// Property API
export const propertyAPI = {
    getOMIZonePrices: async (zoneId, params = {}) => {
        const response = await apiClient.get(`properties/prices/omi-zone/${zoneId}`, { params });
        return response.data;
    },

    getMunicipalityPrices: async (municipalityId, params = {}) => {
        const response = await apiClient.get(`properties/prices/municipality/${municipalityId}`, { params });
        return response.data;
    },

    getPriceHistory: async (municipalityId, params = {}) => {
        const response = await apiClient.get(`properties/prices/municipality/${municipalityId}`, { params });
        return response.data;
    },

    getMunicipalityStatistics: async (municipalityId, params = {}) => {
        const response = await apiClient.get(`properties/statistics/municipality/${municipalityId}`, { params });
        return response.data;
    },
};

// Score API
export const scoreAPI = {
    calculateScore: async (data) => {
        const response = await apiClient.post('scores/calculate', data);
        return response.data;
    },

    getMunicipalityScore: async (municipalityId) => {
        const response = await apiClient.get(`scores/municipality/${municipalityId}`);
        return response.data;
    },

    getScore: async (municipalityId) => {
        const response = await apiClient.get(`scores/municipality/${municipalityId}`);
        return response.data;
    },

    getOMIZoneScore: async (zoneId) => {
        const response = await apiClient.get(`scores/omi-zone/${zoneId}`);
        return response.data;
    },

    // Batch get all zone scores for a municipality (with geometry for map rendering)
    getOMIZoneScores: async (municipalityId) => {
        const response = await apiClient.get(`scores/municipality/${municipalityId}/omi-zones`);
        return response.data;
    },
};

// Risk API
export const riskAPI = {
    getRiskSummary: async (municipalityId) => {
        const response = await apiClient.get(`risks/municipality/${municipalityId}`);
        return response.data;
    },

    getRisks: async (municipalityId) => {
        const response = await apiClient.get(`risks/municipality/${municipalityId}`);
        return response.data;
    },

    getSeismicRisk: async (municipalityId) => {
        const response = await apiClient.get(`risks/seismic/municipality/${municipalityId}`);
        return response.data;
    },

    getFloodRisk: async (municipalityId) => {
        const response = await apiClient.get(`risks/flood/municipality/${municipalityId}`);
        return response.data;
    },

    getLandslideRisk: async (municipalityId) => {
        const response = await apiClient.get(`risks/landslide/municipality/${municipalityId}`);
        return response.data;
    },

    getClimateProjections: async (municipalityId) => {
        const response = await apiClient.get(`risks/climate/municipality/${municipalityId}`);
        return response.data;
    },
};

// Demographics API
export const demographicsAPI = {
    getDemographics: async (municipalityId) => {
        const response = await apiClient.get(`demographics/municipality/${municipalityId}`);
        return response.data;
    },

    getCrimeStatistics: async (municipalityId) => {
        const response = await apiClient.get(`demographics/crime/municipality/${municipalityId}`);
        return response.data;
    },
};

// Health check
export const healthCheck = async () => {
    try {
        const response = await apiClient.get('health');
        return response.data;
    } catch (error) {
        return { status: 'error', message: error.message };
    }
};

export default apiClient;
