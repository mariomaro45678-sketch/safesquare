import React from 'react';
import {
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    ResponsiveContainer,
    Tooltip,
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    const score = data.value;
    const color = score >= 7 ? '#10b981' : score >= 5 ? '#f59e0b' : '#ef4444';

    return (
        <div className="bg-white/95 backdrop-blur-xl rounded-xl shadow-xl border border-gray-100 p-3">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-1">
                {data.category}
            </p>
            <div className="flex items-center">
                <div
                    className="w-2.5 h-2.5 rounded-full mr-2"
                    style={{ backgroundColor: color }}
                />
                <span className="text-lg font-black text-gray-900">
                    {score?.toFixed(1) || 'N/A'}
                </span>
                <span className="text-xs text-gray-400 ml-1">/10</span>
            </div>
        </div>
    );
};

const ScoreRadarChart = ({ componentScores, title = 'Score Breakdown' }) => {
    // Transform component scores to chart data
    const chartData = [
        {
            category: 'Price',
            shortName: '€ Price',
            value: componentScores.price_trend || componentScores.price_score || 0,
            icon: '💰'
        },
        {
            category: 'Yield',
            shortName: 'Yield',
            value: componentScores.rental_yield || componentScores.yield_score || 0,
            icon: '📈'
        },
        {
            category: 'Demographics',
            shortName: 'Demo',
            value: componentScores.demographics || componentScores.demographic_score || 0,
            icon: '👥'
        },
        {
            category: 'Safety',
            shortName: 'Safety',
            value: componentScores.crime || componentScores.safety_score || 0,
            icon: '🛡️'
        },
        {
            category: 'Seismic',
            shortName: 'Seismic',
            value: componentScores.seismic || componentScores.seismic_score || 10,
            icon: '🌋'
        },
        {
            category: 'Flood',
            shortName: 'Flood',
            value: componentScores.flood || componentScores.flood_score || 10,
            icon: '🌊'
        },
        {
            category: 'Landslide',
            shortName: 'Land',
            value: componentScores.landslide || componentScores.landslide_score || 10,
            icon: '⛰️'
        },
        {
            category: 'Climate',
            shortName: 'Climate',
            value: componentScores.climate || componentScores.climate_score || 0,
            icon: '🌡️'
        },
    ];

    // Calculate category averages
    const marketAvg = (chartData[0].value + chartData[1].value + chartData[2].value) / 3;
    const safetyAvg = (chartData[3].value + chartData[4].value + chartData[5].value + chartData[6].value + chartData[7].value) / 5;

    const getScoreColor = (score) => {
        if (score >= 7) return 'text-success-600 bg-success-50';
        if (score >= 5) return 'text-warning-600 bg-warning-50';
        return 'text-danger-600 bg-danger-50';
    };

    return (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-100">
                <h3 className="text-lg font-bold text-gray-900 mb-4">{title}</h3>

                {/* Category Summaries */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="bg-gray-50 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Market</span>
                            <span className={`px-2 py-0.5 rounded-lg text-xs font-bold ${getScoreColor(marketAvg)}`}>
                                {marketAvg.toFixed(1)}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500">Price, Yield, Demographics</p>
                    </div>
                    <div className="bg-gray-50 rounded-xl p-4">
                        <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">Safety</span>
                            <span className={`px-2 py-0.5 rounded-lg text-xs font-bold ${getScoreColor(safetyAvg)}`}>
                                {safetyAvg.toFixed(1)}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500">Risk factors assessment</p>
                    </div>
                </div>
            </div>

            {/* Chart */}
            <div className="p-6 pb-2">
                <ResponsiveContainer width="100%" height={320}>
                    <RadarChart data={chartData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
                        <PolarGrid
                            stroke="#e5e7eb"
                            strokeDasharray="3 3"
                        />
                        <PolarAngleAxis
                            dataKey="shortName"
                            tick={{
                                fontSize: 11,
                                fill: '#6b7280',
                                fontWeight: 600
                            }}
                            tickLine={false}
                        />
                        <PolarRadiusAxis
                            angle={67.5}
                            domain={[0, 10]}
                            tick={{ fontSize: 9, fill: '#9ca3af' }}
                            tickCount={6}
                            axisLine={false}
                        />
                        <Radar
                            name="Score"
                            dataKey="value"
                            stroke="#2563eb"
                            strokeWidth={2}
                            fill="#2563eb"
                            fillOpacity={0.15}
                            animationDuration={1000}
                            animationBegin={200}
                        />
                        <Tooltip content={<CustomTooltip />} />
                    </RadarChart>
                </ResponsiveContainer>
            </div>

            {/* Score Grid */}
            <div className="px-6 pb-6">
                <div className="grid grid-cols-4 gap-2">
                    {chartData.map((item, index) => (
                        <div
                            key={index}
                            className="text-center py-2 px-1 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
                        >
                            <div className="text-sm mb-0.5">{item.icon}</div>
                            <div className={`text-xs font-bold ${item.value >= 7 ? 'text-success-600' :
                                item.value >= 5 ? 'text-warning-600' :
                                    'text-danger-600'
                                }`}>
                                {item.value?.toFixed(1) || '—'}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ScoreRadarChart;
