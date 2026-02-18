import React, { useEffect, useState, useRef } from 'react';

const StatCard = ({
    title,
    value,
    subtitle,
    trend,
    trendLabel = 'YoY',
    icon,
    loading = false
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const cardRef = useRef(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    observer.disconnect();
                }
            },
            { threshold: 0.2 }
        );

        if (cardRef.current) {
            observer.observe(cardRef.current);
        }

        return () => observer.disconnect();
    }, []);

    const getTrendInfo = (t) => {
        if (t === null || t === undefined) return null;
        if (t > 0) return {
            icon: '↑',
            color: 'text-success-600',
            bgColor: 'bg-success-50',
            label: `+${t.toFixed(1)}%`
        };
        if (t < 0) return {
            icon: '↓',
            color: 'text-danger-600',
            bgColor: 'bg-danger-50',
            label: `${t.toFixed(1)}%`
        };
        return {
            icon: '→',
            color: 'text-gray-500',
            bgColor: 'bg-gray-100',
            label: '0.0%'
        };
    };

    const trendInfo = getTrendInfo(trend);

    if (loading) {
        return (
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                <div className="skeleton h-4 w-24 mb-3 rounded" />
                <div className="skeleton h-10 w-32 mb-2 rounded" />
                <div className="skeleton h-3 w-20 rounded" />
            </div>
        );
    }

    return (
        <div
            ref={cardRef}
            className={`group bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md hover:border-gray-200 transition-all duration-300
                ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
            `}
            style={{ transitionDelay: '100ms' }}
        >
            <div className="flex items-start justify-between mb-3">
                <p className="text-xs font-bold text-gray-400 uppercase tracking-wider">
                    {title}
                </p>
                {icon && (
                    <div className="w-8 h-8 bg-gray-50 rounded-lg flex items-center justify-center text-gray-400 group-hover:bg-primary-50 group-hover:text-primary-600 transition-colors">
                        {icon}
                    </div>
                )}
            </div>

            <div className="flex items-end justify-between">
                <div>
                    <p className="text-2xl lg:text-3xl font-black text-gray-900 tabular-nums leading-none mb-1">
                        {value}
                    </p>
                    <p className="text-sm text-gray-500 font-medium">
                        {subtitle}
                    </p>
                </div>

                {trendInfo && (
                    <div className={`flex items-center space-x-1 px-2.5 py-1 rounded-lg ${trendInfo.bgColor}`}>
                        <span className={`text-sm font-bold ${trendInfo.color}`}>
                            {trendInfo.icon}
                        </span>
                        <span className={`text-xs font-bold ${trendInfo.color}`}>
                            {trendInfo.label}
                        </span>
                    </div>
                )}
            </div>

            {trendInfo && trendLabel && (
                <div className="mt-3 pt-3 border-t border-gray-50">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                        {trendLabel} Change
                    </p>
                </div>
            )}
        </div>
    );
};

export default StatCard;
