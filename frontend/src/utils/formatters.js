/**
 * Utility functions for formatting data
 */

// Format currency (Euro)
export const formatCurrency = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('it-IT', {
        style: 'currency',
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(value);
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
    if (value == null) return 'N/A';
    return `${value.toFixed(decimals)}%`;
};

// Format number with thousand separators
export const formatNumber = (value) => {
    if (value == null) return 'N/A';
    return new Intl.NumberFormat('it-IT').format(value);
};

// Format date
export const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('it-IT').format(date);
};

// Get score color based on value
export const getScoreColor = (score) => {
    if (score >= 8.5) return 'text-green-600';
    if (score >= 7.0) return 'text-blue-600';
    if (score >= 5.5) return 'text-yellow-600';
    if (score >= 4.0) return 'text-orange-600';
    return 'text-red-600';
};

// Get score background color
export const getScoreBgColor = (score) => {
    if (score >= 8.5) return 'bg-green-100';
    if (score >= 7.0) return 'bg-blue-100';
    if (score >= 5.5) return 'bg-yellow-100';
    if (score >= 4.0) return 'bg-orange-100';
    return 'bg-red-100';
};

// Get risk level color
export const getRiskColor = (level) => {
    const colors = {
        'Very High': 'text-red-600',
        'High': 'text-orange-600',
        'Medium': 'text-yellow-600',
        'Moderate': 'text-yellow-600',
        'Low': 'text-blue-600',
        'Very Low': 'text-green-600',
    };
    return colors[level] || 'text-gray-600';
};

// Get risk badge color
export const getRiskBadgeColor = (level) => {
    const colors = {
        'Very High': 'bg-red-100 text-red-800',
        'High': 'bg-orange-100 text-orange-800',
        'Medium': 'bg-yellow-100 text-yellow-800',
        'Moderate': 'bg-yellow-100 text-yellow-800',
        'Low': 'bg-blue-100 text-blue-800',
        'Very Low': 'bg-green-100 text-green-800',
    };
    return colors[level] || 'bg-gray-100 text-gray-800';
};
