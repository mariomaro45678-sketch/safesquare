import React, { memo } from 'react';

const ZoneScoreCard = memo(({
    zoneName,
    zoneCode,
    zoneType,
    score,
    confidence,
    isSelected = false,
    onClick
}) => {
    const getScoreConfig = (s) => {
        if (s === null || s === undefined) {
            return { bg: 'bg-gray-100', text: 'text-gray-500', dot: 'bg-gray-400', label: 'Pending' };
        }
        if (s >= 7) return { bg: 'bg-success-50', text: 'text-success-700', dot: 'bg-success-500', label: 'Good' };
        if (s >= 5) return { bg: 'bg-warning-50', text: 'text-warning-700', dot: 'bg-warning-500', label: 'Fair' };
        return { bg: 'bg-danger-50', text: 'text-danger-700', dot: 'bg-danger-500', label: 'Risk' };
    };

    const scoreConfig = getScoreConfig(score);
    const displayName = zoneName || zoneCode;

    return (
        <button
            onClick={onClick}
            className={`
                w-full text-left p-4 rounded-2xl border transition-all duration-200
                ${isSelected
                    ? 'bg-primary-50 border-primary-300 ring-2 ring-primary-500 ring-opacity-50'
                    : 'bg-white border-gray-100 hover:border-gray-200 hover:shadow-sm'
                }
            `}
        >
            <div className="flex items-center justify-between">
                {/* Zone Info */}
                <div className="flex-1 min-w-0 mr-3">
                    <h4 className={`font-bold truncate ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                        {displayName}
                    </h4>
                    <div className="flex items-center space-x-2 mt-1">
                        <span className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                            {zoneCode}
                        </span>
                        {zoneType && (
                            <>
                                <span className="text-gray-300">•</span>
                                <span className="text-xs text-gray-500 capitalize">
                                    {zoneType}
                                </span>
                            </>
                        )}
                    </div>
                </div>

                {/* Score Badge */}
                <div className={`flex items-center px-3 py-2 rounded-xl ${scoreConfig.bg}`}>
                    <div className={`w-2 h-2 rounded-full ${scoreConfig.dot} mr-2`} />
                    <span className={`text-lg font-black tabular-nums ${scoreConfig.text}`}>
                        {score !== null && score !== undefined ? score.toFixed(1) : '—'}
                    </span>
                </div>
            </div>

            {/* Confidence indicator (optional) */}
            {confidence !== null && confidence !== undefined && score !== null && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-400 font-medium">Data Confidence</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-primary-500 rounded-full"
                                    style={{ width: `${confidence * 100}%` }}
                                />
                            </div>
                            <span className="text-gray-500 font-bold">{Math.round(confidence * 100)}%</span>
                        </div>
                    </div>
                </div>
            )}
        </button>
    );
});

ZoneScoreCard.displayName = 'ZoneScoreCard';

export default ZoneScoreCard;
