import React from 'react';
import {
    PieChart,
    Pie,
    Cell,
    ResponsiveContainer,
    Tooltip,
    Legend,
} from 'recharts';

const DemographicsChart = ({ demographics, title = 'Age Distribution' }) => {
    if (!demographics) return null;

    const chartData = [
        { name: '0-14 years', value: demographics.age_0_14_pct || 0, color: '#3b82f6' },
        { name: '15-64 years', value: demographics.age_15_64_pct || 0, color: '#10b981' },
        { name: '65+ years', value: demographics.age_65_plus_pct || 0, color: '#f59e0b' },
    ];

    return (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                    <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                    >
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip
                        formatter={(value) => value ? `${value.toFixed(1)}%` : 'N/A'}
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend verticalAlign="bottom" align="center" iconType="circle" />
                </PieChart>
            </ResponsiveContainer>
        </div>
    );
};

export default DemographicsChart;
