import React from 'react';

const QuickStats = () => {
    // Stats are hardcoded for the MVP regions scope to show platform scale
    const stats = [
        { label: 'Municipalities Analyzed', value: '7,895', icon: '🏙️' },
        { label: 'Market Price Points', value: '15,481', icon: '📈' },
        { label: 'Risk Data Points', value: '9,099', icon: '🛡️' },
        { label: 'Regional Coverage', value: '5 MVP', icon: '🇮🇹' }
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white/50 backdrop-blur-md p-6 rounded-3xl border border-white/20 shadow-xl">
            {stats.map((stat, index) => (
                <div key={index} className="flex flex-col items-center justify-center p-2 text-center">
                    <span className="text-2xl mb-2">{stat.icon}</span>
                    <span className="text-2xl font-black text-gray-900 tracking-tight">{stat.value}</span>
                    <span className="text-[10px] uppercase font-bold text-gray-400 tracking-widest">{stat.label}</span>
                </div>
            ))}
        </div>
    );
};

export default QuickStats;
