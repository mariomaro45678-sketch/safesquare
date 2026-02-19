import React, { useState, useEffect, useRef } from 'react';
import logger from '../utils/logger';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/search/SearchBar';
import PropertyMap from '../components/map/PropertyMap';

// Animated Counter with glow
const AnimatedCounter = ({ end, duration = 2000, suffix = '', prefix = '' }) => {
    const [count, setCount] = useState(0);
    const countRef = useRef(null);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setIsVisible(true);
                    observer.disconnect();
                }
            },
            { threshold: 0.3 }
        );
        if (countRef.current) observer.observe(countRef.current);
        return () => observer.disconnect();
    }, []);

    useEffect(() => {
        if (!isVisible) return;
        let startTime;
        const animate = (currentTime) => {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 4);
            setCount(Math.floor(easeOut * end));
            if (progress < 1) requestAnimationFrame(animate);
        };
        requestAnimationFrame(animate);
    }, [isVisible, end, duration]);

    return <span ref={countRef} className="tabular-nums">{prefix}{count.toLocaleString()}{suffix}</span>;
};

// Bento Feature Card
const BentoCard = ({ icon, title, description, stats, color = 'blue', size = 'default', onClick }) => {
    const gradients = {
        blue: 'from-primary-500/20 to-primary-600/5 hover:from-primary-500/30',
        purple: 'from-purple-500/20 to-purple-600/5 hover:from-purple-500/30',
        cyan: 'from-cyan-500/20 to-cyan-600/5 hover:from-cyan-500/30',
        green: 'from-success-500/20 to-success-600/5 hover:from-success-500/30',
        amber: 'from-warning-500/20 to-warning-600/5 hover:from-warning-500/30',
    };

    return (
        <div onClick={onClick} className={`bento-item p-6 lg:p-8 cursor-pointer group ${size === 'large' ? 'md:col-span-2 md:row-span-2' : ''} ${size === 'wide' ? 'md:col-span-2' : ''} bg-gradient-to-br ${gradients[color]}`}>
            <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 lg:w-14 lg:h-14 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 group-hover:bg-white/10 transition-all duration-300">
                    <div className="text-white/80 group-hover:text-white transition-colors">{icon}</div>
                </div>
                {stats && (
                    <div className="text-right">
                        <div className="text-2xl lg:text-3xl font-black text-white">{stats.value}</div>
                        <div className="text-xs text-white/50 font-medium">{stats.label}</div>
                    </div>
                )}
            </div>
            <h3 className="text-xl lg:text-2xl font-bold text-white mb-2 group-hover:text-gradient-primary transition-all">{title}</h3>
            <p className="text-white/50 text-sm lg:text-base leading-relaxed">{description}</p>
        </div>
    );
};

// Floating Orb
const FloatingOrb = ({ color, size, style }) => {
    const colors = {
        blue: 'bg-primary-500/30',
        purple: 'bg-purple-500/30',
        cyan: 'bg-cyan-500/30',
        green: 'bg-success-500/30',
    };
    return <div className={`absolute rounded-full blur-3xl ${colors[color]} animate-blob`} style={{ width: size, height: size, ...style }} />;
};

const HomePage = () => {
    const navigate = useNavigate();
    const [featuredLocations, setFeaturedLocations] = useState([]);
    const [isMapLoaded, setIsMapLoaded] = useState(false);

    const handleSearch = (query) => navigate(`/search?q=${encodeURIComponent(query)}`);
    const handleCityClick = (city) => {
        const id = city.municipalityId || city.id;
        if (id) navigate(`/property/${id}`);
    };

    useEffect(() => {
        const loadFeatured = async () => {
            try {
                const { locationAPI } = require('../services/api');
                const data = await locationAPI.getFeatured();
                setFeaturedLocations(data.map(city => ({
                    id: city.id, municipalityId: city.id, name: city.name,
                    score: city.investment_score || 5.0, coordinates: city.coordinates
                })));
                setIsMapLoaded(true);
            } catch (err) {
                logger.error('Failed to load featured locations:', err);
                setFeaturedLocations([
                    { id: 1685, municipalityId: 1685, name: 'Milano', score: 8.7, coordinates: { latitude: 45.4642, longitude: 9.1900 } },
                    { id: 5190, municipalityId: 5190, name: 'Roma', score: 7.2, coordinates: { latitude: 41.9028, longitude: 12.4964 } },
                    { id: 4230, municipalityId: 4230, name: 'Bologna', score: 8.4, coordinates: { latitude: 44.4949, longitude: 11.3426 } },
                ]);
                setIsMapLoaded(true);
            }
        };
        loadFeatured();
    }, []);

    const tickerItems = [
        { label: 'Milano', value: '€4,850/m²', change: '+3.2%' },
        { label: 'Roma', value: '€3,420/m²', change: '+1.8%' },
        { label: 'Firenze', value: '€3,890/m²', change: '+2.5%' },
        { label: 'Bologna', value: '€3,150/m²', change: '+2.1%' },
        { label: 'Torino', value: '€2,180/m²', change: '+1.4%' },
        { label: 'Napoli', value: '€2,450/m²', change: '+2.8%' },
    ];

    const features = [
        {
            icon: <svg className="w-6 h-6 lg:w-7 lg:h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>,
            title: 'Demographic Pulse',
            description: 'ISTAT-powered analysis tracking population dynamics, spending power, and social stability.',
            color: 'blue',
            stats: { value: '7.9K+', label: 'Municipalities' }
        },
        {
            icon: <svg className="w-6 h-6 lg:w-7 lg:h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>,
            title: 'Safety & Hazard Risks',
            description: 'Integrated INGV seismic, ISPRA flood/landslide mapping, and air quality data.',
            color: 'green',
            stats: { value: '8', label: 'Risk Layers' }
        },
        {
            icon: <svg className="w-6 h-6 lg:w-7 lg:h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>,
            title: 'Yield Projections',
            description: 'Real-time OMI transaction data with historical trends to calculate projected yields.',
            color: 'purple',
            stats: { value: '50M+', label: 'Data Points' }
        },
    ];

    const quickSearches = ['Milano', 'Roma', 'Bologna', 'Firenze', 'Torino', 'Napoli'];

    return (
        <div className="relative overflow-hidden bg-dark-900 min-h-screen">
            {/* Hero Section */}
            <section className="relative min-h-screen flex items-center py-20 lg:py-0">
                {/* Aurora Background */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute inset-0 bg-hero-dark opacity-50" />
                    <FloatingOrb color="blue" size="600px" style={{ top: '-20%', right: '-10%', animationDelay: '0s' }} />
                    <FloatingOrb color="purple" size="500px" style={{ bottom: '-10%', left: '-5%', animationDelay: '2s' }} />
                    <FloatingOrb color="cyan" size="400px" style={{ top: '30%', left: '20%', animationDelay: '4s' }} />
                    <div className="absolute inset-0 noise-overlay" />
                </div>

                <div className="container mx-auto px-4 relative z-10">
                    <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
                        {/* Left Content */}
                        <div className="max-w-2xl">
                            {/* Live Badge */}
                            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full glass mb-8 animate-fade-in-up">
                                <span className="relative flex h-2 w-2">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-400 opacity-75" />
                                    <span className="relative inline-flex rounded-full h-2 w-2 bg-success-500" />
                                </span>
                                <span className="text-xs font-bold text-white/80 uppercase tracking-wider">Live 2025 Market Data</span>
                            </div>

                            {/* Headline */}
                            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-black text-white leading-[1.05] tracking-tight mb-6 animate-fade-in-up animation-delay-200">
                                Invest in Italian
                                <br />
                                Real Estate with
                                <br />
                                <span className="text-gradient-primary glow-text">Precision.</span>
                            </h1>

                            {/* Subheadline */}
                            <p className="text-lg lg:text-xl text-white/60 leading-relaxed mb-10 max-w-xl animate-fade-in-up animation-delay-400">
                                The first intelligence platform combining market value, demographics, and hazard risks to deliver a{' '}
                                <span className="text-white font-semibold">definitive investment score</span> for every Italian municipality.
                            </p>

                            {/* Search */}
                            <div className="mb-8 animate-fade-in-up animation-delay-600">
                                <SearchBar onSearch={handleSearch} placeholder="Search any Italian municipality..." size="large" />
                                <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
                                    <span className="text-white/40 font-medium">Popular:</span>
                                    {quickSearches.map((city) => (
                                        <button key={city} onClick={() => handleSearch(city)} className="px-3 py-1.5 glass rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-all text-sm font-medium">
                                            {city}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Stats Row */}
                            <div className="flex flex-wrap gap-4 animate-fade-in-up animation-delay-800">
                                <div className="glass rounded-2xl px-5 py-4 flex items-center space-x-4">
                                    <div className="w-10 h-10 rounded-xl bg-primary-500/20 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                                    </div>
                                    <div>
                                        <div className="text-2xl font-black text-white"><AnimatedCounter end={7900} suffix="+" /></div>
                                        <div className="text-xs text-white/50 font-medium">Municipalities</div>
                                    </div>
                                </div>
                                <div className="glass rounded-2xl px-5 py-4 flex items-center space-x-4">
                                    <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                                        <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
                                    </div>
                                    <div>
                                        <div className="text-2xl font-black text-white"><AnimatedCounter end={50} suffix="M+" /></div>
                                        <div className="text-xs text-white/50 font-medium">Data Points</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Right - Map */}
                        <div className="relative animate-fade-in animation-delay-600">
                            <div className="absolute inset-0 bg-primary-500/10 blur-[100px] rounded-full scale-75" />
                            <div className="relative glass rounded-[2rem] p-2 shadow-2xl">
                                {isMapLoaded ? (
                                    <PropertyMap center={[42.5, 12.5]} zoom={5} locations={featuredLocations} height="450px" onLocationClick={handleCityClick} discoveryMode={true} />
                                ) : (
                                    <div className="h-[450px] bg-dark-800 rounded-2xl animate-pulse flex items-center justify-center">
                                        <div className="text-white/40 font-medium">Loading map...</div>
                                    </div>
                                )}
                                {/* Floating Score Card */}
                                <div className="absolute -bottom-4 -left-4 glass rounded-2xl p-4 shadow-xl max-w-[180px] animate-float">
                                    <div className="flex items-center space-x-2 mb-1">
                                        <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                                        <span className="text-[10px] font-bold text-white/60 uppercase tracking-wider">Top Rated</span>
                                    </div>
                                    <div className="text-sm font-bold text-white">Milano: <span className="text-success-400">8.7/10</span></div>
                                </div>
                                {/* AI Badge */}
                                <div className="absolute -top-4 -right-4 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl p-4 shadow-xl max-w-[160px] animate-float animation-delay-1000">
                                    <div className="text-[10px] font-bold text-white/80 uppercase tracking-wider mb-1">AI Analysis</div>
                                    <div className="text-sm font-bold text-white">87% Confidence</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Ticker Section */}
            <section className="border-y border-white/5 bg-dark-900/50 backdrop-blur-sm py-4 overflow-hidden">
                <div className="ticker-wrap">
                    <div className="ticker">
                        {[...tickerItems, ...tickerItems].map((item, i) => (
                            <div key={i} className="flex items-center space-x-6 px-8 whitespace-nowrap">
                                <span className="font-bold text-white">{item.label}</span>
                                <span className="text-white/60">{item.value}</span>
                                <span className={`text-sm font-bold ${item.change.startsWith('+') ? 'text-success-400' : 'text-danger-400'}`}>{item.change}</span>
                                <div className="w-px h-4 bg-white/20" />
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Bento Grid */}
            <section className="py-24 lg:py-32 relative">
                <div className="container mx-auto px-4">
                    <div className="max-w-2xl mx-auto text-center mb-16">
                        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full glass mb-6">
                            <span className="text-xs font-bold text-primary-400 uppercase tracking-wider">Sophisticated Analysis</span>
                        </div>
                        <h2 className="text-3xl lg:text-5xl font-black text-white tracking-tight leading-tight mb-4">
                            Beyond market prices.
                            <br />
                            <span className="text-white/40">Our algorithms look deeper.</span>
                        </h2>
                        <p className="text-lg text-white/50">Comprehensive data integration from Italy's most trusted institutional sources.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
                        {features.map((feature, index) => (
                            <BentoCard key={feature.title} {...feature} onClick={() => navigate('/search')} />
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 lg:py-32 relative overflow-hidden">
                <div className="absolute inset-0">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl" />
                </div>
                <div className="container mx-auto px-4 relative z-10">
                    <div className="max-w-3xl mx-auto text-center">
                        <h2 className="text-3xl lg:text-5xl font-black text-white tracking-tight mb-6">
                            Ready to make smarter
                            <br />
                            investment decisions?
                        </h2>
                        <p className="text-lg text-white/50 mb-10 max-w-xl mx-auto">
                            Start exploring 7,900+ Italian municipalities with institutional-grade investment intelligence.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button onClick={() => navigate('/search')} className="btn btn-primary btn-lg">
                                Start Exploring Free
                                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" /></svg>
                            </button>
                            <button onClick={() => navigate('/about')} className="btn btn-secondary btn-lg">
                                Learn More
                            </button>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default HomePage;