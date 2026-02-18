
import React from 'react';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';

const ClimateProjectionChart = ({ climateData }) => {
    if (!climateData) return null;

    const data = [
        {
            year: 'Historical (Mean)',
            temp: 14.5, // National average baseline
            heatDays: 12,
            precip: 800
        },
        {
            year: '2050 (Projected)',
            temp: 14.5 + (climateData.avg_temp_change || 2.5),
            heatDays: 12 + (climateData.heat_days_increase || 15),
            precip: 800 * (1 + (climateData.extreme_rainfall_increase || 10) / 100)
        }
    ];

    return (
        <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h3 className="text-2xl font-black text-gray-900 uppercase tracking-tighter">Climate Projection (2050)</h3>
                    <p className="text-gray-500 text-sm font-bold uppercase tracking-widest mt-1">SSP5-8.5 Scenario</p>
                </div>
                <div className="text-right">
                    <span className="text-4xl font-black text-blue-600">+{climateData.avg_temp_change?.toFixed(1) || '2.5'}°C</span>
                    <p className="text-gray-500 text-xs font-bold uppercase tracking-widest">Est. Warming</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="h-48">
                    <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-4">Temperature Trend</p>
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={data}>
                            <defs>
                                <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <XAxis dataKey="year" hide />
                            <Tooltip
                                contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                itemStyle={{ fontWeight: '800', fontSize: '12px' }}
                            />
                            <Area type="monotone" dataKey="temp" name="Avg Temp °C" stroke="#ef4444" fillOpacity={1} fill="url(#colorTemp)" strokeWidth={3} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                <div className="space-y-4">
                    <div className="bg-orange-50 p-4 rounded-2xl flex items-center justify-between">
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-widest text-orange-600">Additional Heatwaves</p>
                            <p className="text-2xl font-black text-orange-700">+{climateData.heat_days_increase || 18} days</p>
                        </div>
                        <div className="w-10 h-10 bg-orange-100 rounded-xl flex items-center justify-center text-orange-600">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        </div>
                    </div>

                    <div className="bg-blue-50 p-4 rounded-2xl flex items-center justify-between">
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-widest text-blue-600">Extreme Rainfall</p>
                            <p className="text-2xl font-black text-blue-700">+{climateData.extreme_rainfall_increase || 15}%</p>
                        </div>
                        <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center text-blue-600">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ClimateProjectionChart;
