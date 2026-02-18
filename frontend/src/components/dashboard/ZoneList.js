import React, { useState, useMemo } from 'react';
import ZoneScoreCard from './ZoneScoreCard';

const ZoneList = ({
    zones = [],
    selectedZoneId,
    onZoneSelect,
    maxHeight = '400px'
}) => {
    const [sortBy, setSortBy] = useState('score'); // 'score' | 'name' | 'type'
    const [filterType, setFilterType] = useState('all');

    // Get unique zone types for filter dropdown
    const zoneTypes = useMemo(() => {
        const types = new Set(zones.map(z => z.zone_type).filter(Boolean));
        return Array.from(types).sort();
    }, [zones]);

    // Sort and filter zones
    const sortedZones = useMemo(() => {
        let filtered = zones;

        // Apply filter
        if (filterType !== 'all') {
            filtered = zones.filter(z => z.zone_type?.toLowerCase() === filterType.toLowerCase());
        }

        // Apply sort
        return filtered.sort((a, b) => {
            switch (sortBy) {
                case 'score':
                    // Zones with scores first, then by score descending
                    if (a.overall_score === null && b.overall_score === null) return 0;
                    if (a.overall_score === null) return 1;
                    if (b.overall_score === null) return -1;
                    return b.overall_score - a.overall_score;
                case 'name':
                    return (a.zone_name || a.zone_code).localeCompare(b.zone_name || b.zone_code);
                case 'type':
                    return (a.zone_type || '').localeCompare(b.zone_type || '');
                default:
                    return 0;
            }
        });
    }, [zones, sortBy, filterType]);

    // Count zones with scores
    const scoredCount = zones.filter(z => z.overall_score !== null).length;

    return (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between mb-4">
                    <div>
                        <h3 className="text-lg font-bold text-gray-900">
                            Neighborhood Zones
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                            {scoredCount} of {zones.length} zones scored
                        </p>
                    </div>
                </div>

                {/* Controls */}
                <div className="flex flex-wrap gap-3">
                    {/* Sort */}
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                        <option value="score">Sort by Score</option>
                        <option value="name">Sort by Name</option>
                        <option value="type">Sort by Type</option>
                    </select>

                    {/* Filter */}
                    {zoneTypes.length > 1 && (
                        <select
                            value={filterType}
                            onChange={(e) => setFilterType(e.target.value)}
                            className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                            <option value="all">All Types</option>
                            {zoneTypes.map(type => (
                                <option key={type} value={type}>{type}</option>
                            ))}
                        </select>
                    )}
                </div>
            </div>

            {/* Zone List */}
            <div
                className="p-4 space-y-3 overflow-y-auto"
                style={{ maxHeight }}
            >
                {sortedZones.length === 0 ? (
                    <div className="text-center py-8">
                        <p className="text-gray-400 text-sm">No zones match your filter</p>
                    </div>
                ) : (
                    sortedZones.map(zone => (
                        <ZoneScoreCard
                            key={zone.zone_id}
                            zoneName={zone.zone_name}
                            zoneCode={zone.zone_code}
                            zoneType={zone.zone_type}
                            score={zone.overall_score}
                            confidence={zone.confidence}
                            isSelected={zone.zone_id === selectedZoneId}
                            onClick={() => onZoneSelect(zone)}
                        />
                    ))
                )}
            </div>

            {/* Footer - Score Legend */}
            <div className="px-6 py-4 border-t border-gray-100 bg-gray-50">
                <div className="flex items-center justify-center space-x-6 text-xs">
                    <div className="flex items-center space-x-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-success-500" />
                        <span className="text-gray-500 font-medium">7+ Good</span>
                    </div>
                    <div className="flex items-center space-x-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-warning-500" />
                        <span className="text-gray-500 font-medium">5-7 Fair</span>
                    </div>
                    <div className="flex items-center space-x-1.5">
                        <div className="w-2.5 h-2.5 rounded-full bg-danger-500" />
                        <span className="text-gray-500 font-medium">&lt;5 Risk</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ZoneList;
