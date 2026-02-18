import React from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Cell,
} from 'recharts';

const RiskComparisonChart = ({ riskData, title = 'Risk Assessment' }) => {
    if (!riskData) return null;

    const chartData = [
        {
            name: 'Seismic',
            score: riskData.seismic_risk?.risk_score || 0,
            level: riskData.seismic_risk?.hazard_level || 'Unknown'
        },
        {
            name: 'Flood',
            score: riskData.flood_risk?.risk_score || 0,
            level: riskData.flood_risk?.hazard_level || 'Unknown'
        },
        {
            name: 'Landslide',
            score: riskData.landslide_risk?.risk_score || 0,
            level: riskData.landslide_risk?.hazard_level || 'Unknown'
        },
        {
            name: 'Climate',
            score: riskData.climate_projection ? Math.min(100, (riskData.climate_projection.heat_days_increase / 40) * 100) : 0,
            level: riskData.climate_projection?.avg_temp_change ? `+${riskData.climate_projection.avg_temp_change}°C` : 'Unknown'
        },
    ];

    // Add min function if not available (though Math.min is standard)
    const min = (a, b) => Math.min(a, b);

    // Color based on risk score
    const getBarColor = (score) => {
        if (score >= 70) return '#ef4444'; // red
        if (score >= 40) return '#f97316'; // orange
        if (score >= 20) return '#eab308'; // yellow
        return '#22c55e'; // green
    };

    return (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                    <Tooltip
                        content={({ active, payload }) => {
                            if (active && payload && payload.length) {
                                return (
                                    <div className="bg-white p-3 border border-gray-200 rounded shadow-lg">
                                        <p className="font-semibold text-gray-900">{payload[0].payload.name}</p>
                                        <p className="text-sm text-gray-600 font-medium">Score: {payload[0].value ? payload[0].value.toFixed(1) : '0.0'}/100</p>
                                        <p className="text-sm mt-1">
                                            Level: <span style={{ color: getBarColor(payload[0].value) }} className="font-bold">{payload[0].payload.level}</span>
                                        </p>
                                    </div>
                                );
                            }
                            return null;
                        }}
                    />
                    <Legend iconType="circle" />
                    <Bar dataKey="score" name="Risk Score" radius={[4, 4, 0, 0]} barSize={40}>
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getBarColor(entry.score)} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RiskComparisonChart;
