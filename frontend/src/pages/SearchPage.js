import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { locationAPI } from '../services/api';
import logger from '../utils/logger';
import PropertyMap from '../components/map/PropertyMap';
import SearchBar from '../components/search/SearchBar';
import SearchResults from '../components/search/SearchResults';

// Skeleton Loading Component
const ResultSkeleton = () => (
    <div className="space-y-3">
        {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl p-5 border border-gray-100">
                <div className="flex items-start gap-4">
                    <div className="w-14 h-14 rounded-2xl skeleton" />
                    <div className="flex-1 space-y-3">
                        <div className="flex gap-2">
                            <div className="h-5 w-16 skeleton rounded" />
                            <div className="h-5 w-12 skeleton rounded" />
                        </div>
                        <div className="h-6 w-32 skeleton rounded" />
                        <div className="h-4 w-48 skeleton rounded" />
                    </div>
                    <div className="w-12 h-12 skeleton rounded-xl" />
                </div>
            </div>
        ))}
    </div>
);

const SearchPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [mapLocations, setMapLocations] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearch = useCallback(async (query) => {
        setIsLoading(true);
        setError(null);
        setSearchQuery(query);

        try {
            const data = await locationAPI.search(query);

            if (data && data.found) {
                const searchResults = [{
                    municipality: data.municipality,
                    omi_zone: data.omi_zone,
                    coordinates: data.coordinates || data.municipality?.coordinates
                }];

                setResults(searchResults);
                setMapLocations(searchResults.map(res => ({
                    name: res.omi_zone
                        ? `${res.municipality.name} - ${res.omi_zone.zone_name}`
                        : res.municipality.name,
                    coordinates: res.coordinates,
                    municipalityId: res.municipality.id,
                    score: res.municipality.investment_score || 5.0
                })));
            } else {
                setResults([]);
                setMapLocations([]);
            }
        } catch (err) {
            logger.error('Search error:', err);
            setError('Failed to fetch search results. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Sync with URL params
    useEffect(() => {
        const query = searchParams.get('q');
        if (query) {
            setSearchQuery(query);
            handleSearch(query);
        }
    }, [searchParams, handleSearch]);

    return (
        <div className="flex flex-col lg:flex-row h-[calc(100vh-80px)] bg-surface-50">
            {/* Sidebar */}
            <div className="w-full lg:w-[440px] xl:w-[480px] bg-white border-r border-gray-200 flex flex-col shadow-xl z-20 relative">
                {/* Header */}
                <div className="p-6 lg:p-8 border-b border-gray-100">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
                                <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-gray-900">Discover</h2>
                                <p className="text-xs text-gray-500">Explore Italian municipalities</p>
                            </div>
                        </div>
                    </div>
                    <SearchBar onSearch={handleSearch} placeholder="City, province, or region..." />
                </div>

                {/* Results Area */}
                <div className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-4">
                    {/* Status Bar */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            {searchQuery && (
                                <span className="text-sm text-gray-500">
                                    {isLoading ? 'Searching...' : (
                                        <>
                                            <span className="font-semibold text-gray-900">{results.length}</span>
                                            {' '}result{results.length !== 1 ? 's' : ''} for "{searchQuery}"
                                        </>
                                    )}
                                </span>
                            )}
                        </div>
                    </div>

                    {/* Content */}
                    {isLoading ? (
                        <ResultSkeleton />
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center py-16 px-6">
                            <div className="w-16 h-16 bg-danger-100 rounded-2xl flex items-center justify-center mb-4">
                                <svg className="w-8 h-8 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-2">Something went wrong</h3>
                            <p className="text-sm text-gray-500 text-center mb-4">{error}</p>
                            <button
                                onClick={() => handleSearch(searchQuery)}
                                className="btn btn-primary btn-sm"
                            >
                                Try Again
                            </button>
                        </div>
                    ) : !searchQuery ? (
                        <div className="flex flex-col items-center justify-center py-16 px-6">
                            <div className="w-20 h-20 bg-gray-100 rounded-3xl flex items-center justify-center mb-6">
                                <svg className="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                                </svg>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-2">Start Exploring</h3>
                            <p className="text-sm text-gray-500 text-center max-w-xs">
                                Search for any Italian municipality or explore the map to discover investment opportunities.
                            </p>
                        </div>
                    ) : (
                        <SearchResults
                            results={results}
                            selectedId={selectedId}
                            onSelectLocation={(loc) => setSelectedId(loc.municipality?.id)}
                        />
                    )}
                </div>

                {/* Footer Stats */}
                <div className="p-4 lg:p-6 border-t border-gray-100 bg-gray-50/50">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center space-x-1">
                            <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                            <span>Live data</span>
                        </div>
                        <span>7,900+ municipalities available</span>
                    </div>
                </div>
            </div>

            {/* Map Area */}
            <div className="flex-1 relative">
                <PropertyMap
                    locations={mapLocations}
                    height="100%"
                    discoveryMode={true}
                    onLocationClick={(loc) => {
                        setSelectedId(loc.municipalityId);
                        if (loc.municipalityId) {
                            navigate(`/property/${loc.municipalityId}`);
                        }
                    }}
                />

                {/* Floating UI Elements */}
                <div className="absolute top-6 right-6 flex flex-col space-y-4 z-[1000]">
                    {/* Info Card */}
                    <div className="bg-white/95 backdrop-blur-xl shadow-xl rounded-2xl p-5 max-w-xs border border-gray-100">
                        <div className="flex items-center space-x-2 mb-3">
                            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                                <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                                </svg>
                            </div>
                            <h4 className="font-bold text-gray-900">Interactive Map</h4>
                        </div>
                        <p className="text-xs text-gray-500 leading-relaxed">
                            Colored markers indicate investment potential. Click any municipality to view detailed insights.
                        </p>
                    </div>

                    {/* Legend */}
                    <div className="bg-white/95 backdrop-blur-xl shadow-xl rounded-2xl p-5 border border-gray-100">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">Investment Score</h4>
                        <div className="space-y-2">
                            <div className="flex items-center text-xs">
                                <div className="w-3 h-3 rounded-full bg-success-500 mr-2" />
                                <span className="text-gray-600 font-medium">7.0 - 10.0 High</span>
                            </div>
                            <div className="flex items-center text-xs">
                                <div className="w-3 h-3 rounded-full bg-warning-500 mr-2" />
                                <span className="text-gray-600 font-medium">5.0 - 6.9 Moderate</span>
                            </div>
                            <div className="flex items-center text-xs">
                                <div className="w-3 h-3 rounded-full bg-danger-500 mr-2" />
                                <span className="text-gray-600 font-medium">0.0 - 4.9 Risk</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Mobile Search Toggle */}
                <button className="lg:hidden absolute bottom-6 left-1/2 -translate-x-1/2 bg-primary-600 text-white shadow-xl rounded-full px-6 py-3 flex items-center space-x-2 z-[1000]">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                    </svg>
                    <span className="font-bold text-sm">View Results</span>
                </button>
            </div>
        </div>
    );
};

export default SearchPage;
