import React from 'react';
import { useNavigate } from 'react-router-dom';
import { formatNumber } from '../../utils/formatters';

const SearchResults = ({ results, onSelectLocation, selectedId }) => {
    const navigate = useNavigate();

    const handleClick = (location) => {
        if (onSelectLocation) onSelectLocation(location);
    };

    const handleViewDetails = (e, id) => {
        e.stopPropagation();
        navigate(`/property/${id}`);
    };

    const getScoreInfo = (score) => {
        if (score >= 7.5) return { label: 'Excellent', color: 'success', bgClass: 'bg-success-500/20', textClass: 'text-success-400', borderClass: 'border-success-500/30' };
        if (score >= 6) return { label: 'Strong', color: 'success', bgClass: 'bg-success-500/15', textClass: 'text-success-400', borderClass: 'border-success-500/20' };
        if (score >= 5) return { label: 'Moderate', color: 'warning', bgClass: 'bg-warning-500/20', textClass: 'text-warning-400', borderClass: 'border-warning-500/30' };
        if (score >= 3) return { label: 'Low', color: 'warning', bgClass: 'bg-warning-500/15', textClass: 'text-warning-400', borderClass: 'border-warning-500/20' };
        return { label: 'High Risk', color: 'danger', bgClass: 'bg-danger-500/20', textClass: 'text-danger-400', borderClass: 'border-danger-500/30' };
    };

    if (!results || results.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-20 px-6">
                <div className="w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center mb-6">
                    <svg className="w-10 h-10 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
                </div>
                <h3 className="text-lg font-bold text-white mb-2">No results found</h3>
                <p className="text-sm text-white/50 text-center max-w-xs">Try searching for a different municipality, province, or region in Italy.</p>
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
                    <div key={id || index} onClick={() => handleClick(result)} className={`group relative bento-item p-5 cursor-pointer overflow-hidden transition-all duration-300 ${isSelected ? 'border-primary-500/50 ring-2 ring-primary-500/20' : ''}`}>
                        {isSelected && <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary-500" />}
                        <div className="flex items-start gap-4">
                            {/* Score Circle */}
                            <div className={`flex-shrink-0 w-14 h-14 rounded-2xl ${scoreInfo.bgClass} border ${scoreInfo.borderClass} flex flex-col items-center justify-center transition-transform group-hover:scale-105`}>
                                <span className={`text-lg font-black ${scoreInfo.textClass}`}>{score.toFixed(1)}</span>
                                <span className={`text-[8px] font-bold uppercase tracking-wider ${scoreInfo.textClass} opacity-70`}>Score</span>
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex flex-wrap items-center gap-2 mb-2">
                                    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${scoreInfo.bgClass} ${scoreInfo.textClass} border ${scoreInfo.borderClass}`}>{scoreInfo.label}</span>
                                    {result.omi_zone && <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-white/10 border border-white/10 text-white/60">Zone {result.omi_zone.zone_code}</span>}
                                </div>
                                <h3 className="text-lg font-bold text-white leading-tight truncate group-hover:text-primary-400 transition-colors">{result.municipality?.name}</h3>
                                <div className="flex items-center mt-1 text-sm text-white/50">
                                    <svg className="w-3.5 h-3.5 mr-1.5 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                                    <span className="truncate">{result.municipality?.province_name}, {result.municipality?.region_name}</span>
                                </div>
                                {result.municipality?.population && (
                                    <div className="flex items-center gap-4 mt-3 pt-3 border-t border-white/5">
                                        <div className="flex items-center text-xs text-white/40">
                                            <svg className="w-3.5 h-3.5 mr-1.5 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                                            <span className="font-semibold text-white/60">{formatNumber(result.municipality.population)}</span>
                                        </div>
                                        {result.municipality?.avg_price_sqm && (
                                            <div className="flex items-center text-xs text-white/40">
                                                <svg className="w-3.5 h-3.5 mr-1.5 text-white/30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                <span className="font-semibold text-white/60">€{formatNumber(result.municipality.avg_price_sqm)}/m²</span>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>

                            {/* Action Button */}
                            <button onClick={(e) => handleViewDetails(e, id)} className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center transition-all duration-200 ${isSelected ? 'bg-primary-500 text-white' : 'bg-white/5 border border-white/10 text-white/40 group-hover:bg-primary-500/20 group-hover:border-primary-500/30 group-hover:text-primary-400'}`} aria-label="View details">
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                            </button>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default SearchResults;