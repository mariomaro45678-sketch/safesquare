import React, { useEffect, useState, useRef } from 'react';

const ScoreCard = ({ score, category = "Investment Score", description }) => {
    const [animatedScore, setAnimatedScore] = useState(0);
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

    useEffect(() => {
        if (!isVisible) return;
        const duration = 1500;
        const startTime = Date.now();
        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            setAnimatedScore(easeOut * score);
            if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }, [isVisible, score]);

    const getScoreInfo = (s) => {
        if (s >= 7.5) return { label: 'Excellent', color: 'success', gradient: 'from-success-400 to-success-500', glow: 'shadow-glow-success' };
        if (s >= 6) return { label: 'Strong', color: 'success', gradient: 'from-success-400 to-cyan-500', glow: 'shadow-glow-success' };
        if (s >= 5) return { label: 'Moderate', color: 'warning', gradient: 'from-warning-400 to-warning-500', glow: 'shadow-glow-warning' };
        if (s >= 3) return { label: 'Low', color: 'warning', gradient: 'from-warning-500 to-danger-500', glow: 'shadow-glow-warning' };
        return { label: 'High Risk', color: 'danger', gradient: 'from-danger-400 to-danger-500', glow: 'shadow-glow-danger' };
    };

    const scoreInfo = getScoreInfo(score);
    const circumference = 2 * Math.PI * 54;
    const strokeDashoffset = circumference - (animatedScore / 10) * circumference;

    return (
        <div ref={cardRef} className={`relative overflow-hidden bento-item p-6 lg:p-8 transition-all duration-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            {/* Background Glow */}
            <div className={`absolute -top-20 -right-20 w-40 h-40 bg-gradient-to-br ${scoreInfo.gradient} rounded-full opacity-20 blur-3xl`} />

            <div className="relative">
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <div>
                        <p className="text-xs font-bold text-white/50 uppercase tracking-widest mb-2">{category}</p>
                        <div className={`inline-flex items-center px-3 py-1.5 rounded-lg bg-${scoreInfo.color}-500/20 border border-${scoreInfo.color}-500/30`}>
                            <span className={`text-sm font-bold text-${scoreInfo.color}-400`}>{scoreInfo.label}</span>
                        </div>
                    </div>

                    {/* Circular Progress */}
                    <div className="relative w-28 h-28">
                        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="54" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                            <circle cx="60" cy="60" r="54" fill="none" stroke={`url(#scoreGradient-${scoreInfo.color})`} strokeWidth="8" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} style={{ transition: 'stroke-dashoffset 1.5s ease-out', filter: `drop-shadow(0 0 8px ${scoreInfo.color === 'success' ? '#10b981' : scoreInfo.color === 'warning' ? '#f59e0b' : '#ef4444'})` }} />
                            <defs>
                                <linearGradient id={`scoreGradient-success`} x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="#10b981" /><stop offset="100%" stopColor="#06b6d4" />
                                </linearGradient>
                                <linearGradient id={`scoreGradient-warning`} x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="#f59e0b" /><stop offset="100%" stopColor="#ef4444" />
                                </linearGradient>
                                <linearGradient id={`scoreGradient-danger`} x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" stopColor="#ef4444" /><stop offset="100%" stopColor="#dc2626" />
                                </linearGradient>
                            </defs>
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-3xl font-black text-white tabular-nums">{animatedScore.toFixed(1)}</span>
                            <span className="text-xs font-bold text-white/40">/ 10</span>
                        </div>
                    </div>
                </div>

                {/* Score Bar */}
                <div className="mb-6">
                    <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                        <div className={`h-full bg-gradient-to-r ${scoreInfo.gradient} rounded-full transition-all duration-1000 ease-out ${scoreInfo.glow}`} style={{ width: `${(animatedScore / 10) * 100}%` }} />
                    </div>
                    <div className="flex justify-between mt-2 text-[10px] font-bold text-white/40 uppercase tracking-wider">
                        <span>Risk</span><span>Moderate</span><span>Excellent</span>
                    </div>
                </div>

                {description && (
                    <div className="pt-4 border-t border-white/5">
                        <p className="text-sm text-white/50 leading-relaxed">{description}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ScoreCard;