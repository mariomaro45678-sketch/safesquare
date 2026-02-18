import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatNumber } from '../../utils/formatters';

const SearchResults = ({ results, onSelectLocation, selectedId }) => {
    const navigate = useNavigate();

    const handleClick = (location) => {
        if (onSelectLocation) {
            onSelectLocation(location);
        }
    };

    const handleViewDetails = (e, id) => {
        e.stopPropagation();
        navigate(`/property/${id}`);
    };

    const getScoreInfo = (score) => {
        if (score >= 7.5) return { label: 'Excellent', color: 'bg-success-500', bgColor: 'bg-success-50', textColor: 'text-success-700' };
        if (score >= 6) return { label: 'Strong', color: 'bg-success-400', bgColor: 'bg-success-50', textColor: 'text-success-600' };
        if (score >= 5) return { label: 'Moderate', color: 'bg-warning-500', bgColor: 'bg-warning-50', textColor: 'text-warning-700' };
        if (score >= 3) return { label: 'Low', color: 'bg-warning-600', bgColor: 'bg-warning-50', textColor: 'text-warning-700' };
        return { label: 'High Risk', color: 'bg-danger-500', bgColor: 'bg-danger-50', textColor: 'text-danger-700' };
    };

    if (!results || results.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-20 px-6">
                <div className="w-20 h-20 bg-gray-100 rounded-3xl flex items-center justify-center mb-6">
                    <svg className="w-10 h-10 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">No results found</h3>
                <p className="text-sm text-gray-500 text-center max-w-xs">
                    Try searching for a different municipality, province, or region in Italy.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-3">
            {results.map((result, index) => {
                const id = result.municipality?.id || result.municipalityId;
                const isSelected = selectedId === id;
                const score = result.municipality?.investment_score || 5.0;
                const scoreInfo = getScoreInfo(score);

                return (
                    <div
                        key={id || index}
                        onClick={() => handleClick(result)}
                        className={`group relative bg-white rounded-2xl p-5 transition-all duration-300 cursor-pointer border-2 overflow-hidden
                            ${isSelected
                                ? 'border-primary-500 shadow-lg shadow-primary-500/10 scale-[1.01]'
                                : 'border-transparent shadow-sm hover:shadow-md hover:border-gray-200'
                            }
                        `}
                    >
                        {/* Selection Indicator */}
                        {isSelected && (
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-500" />
                        )}

                        <div className="flex items-start gap-4">
                            {/* Score Circle */}
                            <div className={`flex-shrink-0 w-14 h-14 rounded-2xl ${scoreInfo.bgColor} flex flex-col items-center justify-center transition-transform group-hover:scale-105`}>
                                <span className={`text-lg font-black ${scoreInfo.textColor}`}>
                                    {score.toFixed(1)}
                                </span>
                                <span className={`text-[8px] font-bold uppercase tracking-wider ${scoreInfo.textColor}`}>
                                    Score
                                </span>
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                {/* Badges */}
                                <div className="flex flex-wrap items-center gap-2 mb-2">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${scoreInfo.bgColor} ${scoreInfo.textColor}`}>
                                        {scoreInfo.label}
                                    </span>
                                    {result.omi_zone && (
                                        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-gray-100 text-gray-600">
                                            Zone {result.omi_zone.zone_code}
                                        </span>
                                    )}
                                </div>

                                {/* Municipality Name */}
                                <h3 className="text-lg font-bold text-gray-900 leading-tight truncate group-hover:text-primary-600 transition-colors">
                                    {result.municipality?.name}
                                </h3>

                                {/* Location Info */}
                                <div className="flex items-center mt-1 text-sm text-gray-500">
                                    <svg className="w-3.5 h-3.5 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                    </svg>
                                    <span className="truncate">
                                        {result.municipality?.province_name}, {result.municipality?.region_name}
                                    </span>
                                </div>

                                {/* Stats Row */}
                                {result.municipality?.population && (
                                    <div className="flex items-center gap-4 mt-3 pt-3 border-t border-gray-100">
                                        <div className="flex items-center text-xs text-gray-500">
                                            <svg className="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                                            </svg>
                                            <span className="font-semibold">{formatNumber(result.municipality.population)}</span>
                                        </div>
                                        {result.municipality?.avg_price_sqm && (
                                            <div className="flex items-center text-xs text-gray-500">
                                                <svg className="w-3.5 h-3.5 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                                </svg>
                                                <span className="font-semibold">€{formatNumber(result.municipality.avg_price_sqm)}/m²</span>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* Action Button */}
                            <button
                                onClick={(e) => handleViewDetails(e, id)}
                                className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200
                                    ${isSelected
                                        ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/30'
                                        : 'bg-gray-100 text-gray-400 group-hover:bg-primary-50 group-hover:text-primary-600'
                                    }
                                `}
                                aria-label="View details"
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                                </svg>
                            </button>
                        </div>

                        {/* Hover Gradient */}
                        <div className="absolute inset-0 bg-gradient-to-r from-primary-50/0 via-primary-50/0 to-primary-50/50 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none rounded-2xl" />
                    </div>
                );
            })}
        </div>
    );
};

export default SearchResults;
