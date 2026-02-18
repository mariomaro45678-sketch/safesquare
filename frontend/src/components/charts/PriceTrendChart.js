import React, { useState } from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
} from 'recharts';
import { formatCurrency } from '../../utils/formatters';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || !payload.length) return null;

    return (
        <div className="bg-white/95 backdrop-blur-xl rounded-2xl shadow-xl border border-gray-100 p-4 min-w-[180px]">
            <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">{label}</p>
            {payload.map((entry, index) => (
                <div key={index} className="flex items-center justify-between py-1">
                    <div className="flex items-center">
                        <div
                            className="w-2 h-2 rounded-full mr-2"
                            style={{ backgroundColor: entry.color }}
                        />
                        <span className="text-sm text-gray-600">{entry.name}</span>
                    </div>
                    <span className="text-sm font-bold text-gray-900 ml-4">
                        {formatCurrency(entry.value)}
                    </span>
                </div>
            ))}
        </div>
    );
};

const PriceTrendChart = ({ data = [], title = 'Price History' }) => {
    const [timeRange, setTimeRange] = useState('all');

    if (!data || data.length === 0) {
        return (
            <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-100">
                    <h3 className="text-lg font-bold text-gray-900">{title}</h3>
                </div>
                <div className="h-[300px] flex flex-col items-center justify-center text-gray-400 p-6">
                    <svg className="w-16 h-16 text-gray-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                    </svg>
                    <p className="text-sm font-medium">No price history available</p>
                </div>
            </div>
        );
    }

    // Transform and filter data
    let chartData = data.map(item => ({
        period: `${item.year} S${item.semester}`,
        avgPrice: item.avg_price,
        minPrice: item.min_price,
        maxPrice: item.max_price,
        year: item.year,
    }));

    // Filter by time range
    if (timeRange !== 'all') {
        const years = parseInt(timeRange);
        const currentYear = new Date().getFullYear();
        chartData = chartData.filter(item => item.year >= currentYear - years);
    }

    // Calculate price change
    const firstPrice = chartData[0]?.avgPrice || 0;
    const lastPrice = chartData[chartData.length - 1]?.avgPrice || 0;
    const priceChange = firstPrice > 0 ? ((lastPrice - firstPrice) / firstPrice) * 100 : 0;
    const avgPrice = chartData.reduce((sum, item) => sum + (item.avgPrice || 0), 0) / chartData.length;

    const timeRanges = [
        { label: '1Y', value: '1' },
        { label: '3Y', value: '3' },
        { label: '5Y', value: '5' },
        { label: 'All', value: 'all' },
    ];

    return (
        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
            {/* Header */}
            <div className="p-6 border-b border-gray-100">
                <div className="flex items-center justify-between flex-wrap gap-4">
                    <div>
                        <h3 className="text-lg font-bold text-gray-900 mb-1">{title}</h3>
                        <div className="flex items-center space-x-4">
                            <span className="text-2xl font-black text-gray-900">
                                {formatCurrency(lastPrice)}
                            </span>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-lg text-sm font-bold ${priceChange >= 0
                                    ? 'bg-success-50 text-success-600'
                                    : 'bg-danger-50 text-danger-600'
                                }`}>
                                {priceChange >= 0 ? '↑' : '↓'} {Math.abs(priceChange).toFixed(1)}%
                            </span>
                        </div>
                    </div>

                    {/* Time Range Selector */}
                    <div className="flex items-center bg-gray-100 p-1 rounded-xl">
                        {timeRanges.map((range) => (
                            <button
                                key={range.value}
                                onClick={() => setTimeRange(range.value)}
                                className={`px-4 py-1.5 text-xs font-bold rounded-lg transition-all ${timeRange === range.value
                                        ? 'bg-white text-gray-900 shadow-sm'
                                        : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                {range.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Chart */}
            <div className="p-6">
                <ResponsiveContainer width="100%" height={280}>
                    <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                        <defs>
                            <linearGradient id="colorAvg" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.2} />
                                <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorMax" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="4 4" vertical={false} stroke="#e5e7eb" />
                        <XAxis
                            dataKey="period"
                            tick={{ fontSize: 11, fill: '#9ca3af', fontWeight: 500 }}
                            axisLine={false}
                            tickLine={false}
                            dy={10}
                        />
                        <YAxis
                            tick={{ fontSize: 11, fill: '#9ca3af', fontWeight: 500 }}
                            tickFormatter={(value) => `€${(value / 1000).toFixed(0)}k`}
                            axisLine={false}
                            tickLine={false}
                            dx={-10}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <ReferenceLine
                            y={avgPrice}
                            stroke="#94a3b8"
                            strokeDasharray="3 3"
                            label={{
                                value: 'Avg',
                                position: 'right',
                                fill: '#94a3b8',
                                fontSize: 10,
                                fontWeight: 600
                            }}
                        />
                        <Area
                            type="monotone"
                            dataKey="maxPrice"
                            stroke="#10b981"
                            strokeWidth={1.5}
                            strokeDasharray="4 4"
                            fill="url(#colorMax)"
                            name="Max Price"
                            dot={false}
                        />
                        <Area
                            type="monotone"
                            dataKey="avgPrice"
                            stroke="#2563eb"
                            strokeWidth={2.5}
                            fill="url(#colorAvg)"
                            name="Average Price"
                            dot={{ r: 3, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }}
                            activeDot={{ r: 5, fill: '#2563eb', strokeWidth: 2, stroke: '#fff' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="minPrice"
                            stroke="#f59e0b"
                            strokeWidth={1.5}
                            strokeDasharray="4 4"
                            fill="transparent"
                            name="Min Price"
                            dot={false}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>

            {/* Legend */}
            <div className="px-6 pb-6">
                <div className="flex items-center justify-center space-x-6 text-xs">
                    <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-primary-600 mr-2" />
                        <span className="text-gray-600 font-medium">Average</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-success-500 mr-2" />
                        <span className="text-gray-600 font-medium">Maximum</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-warning-500 mr-2" />
                        <span className="text-gray-600 font-medium">Minimum</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PriceTrendChart;
