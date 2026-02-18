import React, { useEffect, useState } from 'react';

const ScoreCard = ({ score, category = "Investment Score", description }) => {
    const [animatedScore, setAnimatedScore] = useState(0);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);
        const duration = 1500;
        const startTime = Date.now();

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            setAnimatedScore(easeOut * score);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [score]);

    const getScoreInfo = (s) => {
        if (s >= 7.5) return { label: 'Excellent', color: 'success', gradient: 'from-success-500 to-success-600' };
        if (s >= 6) return { label: 'Strong', color: 'success', gradient: 'from-success-400 to-success-500' };
        if (s >= 5) return { label: 'Moderate', color: 'warning', gradient: 'from-warning-400 to-warning-500' };
        if (s >= 3) return { label: 'Low', color: 'warning', gradient: 'from-warning-500 to-warning-600' };
        return { label: 'High Risk', color: 'danger', gradient: 'from-danger-500 to-danger-600' };
    };

    const scoreInfo = getScoreInfo(score);
    const circumference = 2 * Math.PI * 45;
    const strokeDashoffset = circumference - (animatedScore / 10) * circumference;

    return (
        <div className={`relative overflow-hidden bg-white rounded-3xl p-6 lg:p-8 border border-gray-100 shadow-sm transition-all duration-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            {/* Background Glow */}
            <div className={`absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br ${scoreInfo.gradient} rounded-full opacity-10 blur-3xl`} />

            <div className="relative">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">
                            {category}
                        </p>
                        <div className={`inline-flex items-center px-3 py-1 rounded-lg bg-${scoreInfo.color}-50 text-${scoreInfo.color}-600`}>
                            <span className="text-sm font-bold">{scoreInfo.label}</span>
                        </div>
                    </div>

                    {/* Circular Progress */}
                    <div className="relative w-28 h-28">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                            {/* Background circle */}
                            <circle
                                cx="50"
                                cy="50"
                                r="45"
                                fill="none"
                                stroke="#e5e7eb"
                                strokeWidth="8"
                            />
                            {/* Progress circle */}
                            <circle
                                cx="50"
                                cy="50"
                                r="45"
                                fill="none"
                                stroke="url(#scoreGradient)"
                                strokeWidth="8"
                                strokeLinecap="round"
                                strokeDasharray={circumference}
                                strokeDashoffset={strokeDashoffset}
                                style={{ transition: 'stroke-dashoffset 1.5s ease-out' }}
                            />
                            <defs>
                                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor={score >= 5 ? '#10b981' : '#ef4444'} />
                                    <stop offset="100%" stopColor={score >= 7 ? '#059669' : score >= 5 ? '#f59e0b' : '#dc2626'} />
                                </linearGradient>
                            </defs>
                        </svg>
                        {/* Score Text */}
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-3xl font-black text-gray-900 tabular-nums">
                                {animatedScore.toFixed(1)}
                            </span>
                            <span className="text-xs font-bold text-gray-400">/ 10</span>
                        </div>
                    </div>
                </div>

                {/* Score Bar */}
                <div className="mb-6">
                    <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                        <div
                            className={`h-full bg-gradient-to-r ${scoreInfo.gradient} rounded-full transition-all duration-1000 ease-out`}
                            style={{ width: `${(animatedScore / 10) * 100}%` }}
                        />
                    </div>
                    <div className="flex justify-between mt-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                        <span>Risk</span>
                        <span>Moderate</span>
                        <span>Excellent</span>
                    </div>
                </div>

                {/* Description */}
                {description && (
                    <div className="pt-4 border-t border-gray-100">
                        <p className="text-sm text-gray-500 leading-relaxed">
                            {description}
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ScoreCard;
