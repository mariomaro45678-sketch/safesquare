import React, { useEffect, useState, useRef } from 'react';

const StatCard = ({ title, value, subtitle, trend, trendLabel = 'YoY', icon, loading = false }) => {
    const [isVisible, setIsVisible] = useState(false);
    const cardRef = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting) {
                setIsVisible(true);
                observer.disconnect();
            }
        }, { threshold: 0.2 });
        if (cardRef.current) observer.observe(cardRef.current);
        return () => observer.disconnect();
    }, []);

    const getTrendInfo = (t) => {
        if (t === null || t === undefined) return null;
        if (t > 0) return { icon: '↑', color: 'text-success-400', bgColor: 'bg-success-500/20', borderColor: 'border-success-500/30', label: `+${t.toFixed(1)}%` };
        if (t < 0) return { icon: '↓', color: 'text-danger-400', bgColor: 'bg-danger-500/20', borderColor: 'border-danger-500/30', label: `${t.toFixed(1)}%` };
        return { icon: '→', color: 'text-white/50', bgColor: 'bg-white/10', borderColor: 'border-white/20', label: '0.0%' };
    };

    const trendInfo = getTrendInfo(trend);

    if (loading) {
        return (
            <div className="bento-item p-6">
                <div className="skeleton h-4 w-24 mb-4 rounded" />
                <div className="skeleton h-10 w-32 mb-2 rounded" />
                <div className="skeleton h-3 w-20 rounded" />
            </div>
        );
    }

    return (
        <div ref={cardRef} className={`bento-item p-6 group transition-all duration-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`} style={{ transitionDelay: '100ms' }}>
            <div className="flex items-start justify-between mb-3">
                <p className="text-xs font-bold text-white/50 uppercase tracking-wider">{title}</p>
                {icon && (
                    <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-white/40 group-hover:bg-primary-500/20 group-hover:text-primary-400 group-hover:border-primary-500/30 transition-all duration-300">
                        {icon}
                    </div>
                )}
            </div>

            <div className="flex items-end justify-between">
                <div>
                    <p className="text-2xl lg:text-3xl font-black text-white tabular-nums leading-none mb-1">{value}</p>
                    <p className="text-sm text-white/40 font-medium">{subtitle}</p>
                </div>
                {trendInfo && (
                    <div className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg ${trendInfo.bgColor} border ${trendInfo.borderColor}`}>
                        <span className={`text-sm font-bold ${trendInfo.color}`}>{trendInfo.icon}</span>
                        <span className={`text-xs font-bold ${trendInfo.color}`}>{trendInfo.label}</span>
                    </div>
                )}
            </div>

            {trendInfo && trendLabel && (
                <div className="mt-3 pt-3 border-t border-white/5">
                    <p className="text-[10px] font-bold text-white/30 uppercase tracking-wider">{trendLabel} Change</p>
                </div>
            )}
        </div>
    );
};

export default StatCard;