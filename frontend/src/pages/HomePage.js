import React, { useState, useEffect, useRef } from 'react';
import logger from '../utils/logger';
import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/search/SearchBar';
import PropertyMap from '../components/map/PropertyMap';

// Animated Counter Component
const AnimatedCounter = ({ end, duration = 2000, suffix = '' }) => {
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

        if (countRef.current) {
            observer.observe(countRef.current);
        }

        return () => observer.disconnect();
    }, []);

    useEffect(() => {
        if (!isVisible) return;

        let startTime;
        const animate = (currentTime) => {
            if (!startTime) startTime = currentTime;
            const progress = Math.min((currentTime - startTime) / duration, 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            setCount(Math.floor(easeOut * end));

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [isVisible, end, duration]);

    return (
        <span ref={countRef}>
            {count.toLocaleString()}{suffix}
        </span>
    );
};

// Feature Card Component
const FeatureCard = ({ icon, title, description, delay }) => (
    <div
        className="group relative bg-white rounded-3xl p-8 border border-gray-100 shadow-sm hover:shadow-xl transition-all duration-500 hover:-translate-y-2"
        style={{ animationDelay: `${delay}ms` }}
    >
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600/5 to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <div className="relative">
            <div className="w-14 h-14 bg-gray-50 rounded-2xl flex items-center justify-center text-gray-400 group-hover:bg-primary-600 group-hover:text-white transition-all duration-300 mb-6 group-hover:scale-110 group-hover:shadow-lg group-hover:shadow-primary-600/30">
                {icon}
            </div>
            <h4 className="text-xl font-bold text-gray-900 mb-3">{title}</h4>
            <p className="text-gray-500 leading-relaxed">{description}</p>
        </div>
    </div>
);

// Quick Stat Badge
const StatBadge = ({ value, label, icon }) => (
    <div className="flex items-center space-x-3 bg-white/80 backdrop-blur-sm rounded-2xl px-4 py-3 border border-gray-100 shadow-sm">
        <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center text-primary-600">
            {icon}
        </div>
        <div>
            <div className="text-lg font-black text-gray-900">{value}</div>
            <div className="text-xs text-gray-500 font-medium">{label}</div>
        </div>
    </div>
);

const HomePage = () => {
    const navigate = useNavigate();
    const [featuredLocations, setFeaturedLocations] = useState([]);
    const [isMapLoaded, setIsMapLoaded] = useState(false);

    const handleSearch = (query) => {
        navigate(`/search?q=${encodeURIComponent(query)}`);
    };

    const handleCityClick = (city) => {
        const id = city.municipalityId || city.id;
        if (id) {
            navigate(`/property/${id}`);
        }
    };

    useEffect(() => {
        const loadFeatured = async () => {
            try {
                const { locationAPI } = require('../services/api');
                const data = await locationAPI.getFeatured();

                const formatted = data.map(city => ({
                    id: city.id,
                    municipalityId: city.id,
                    name: city.name,
                    score: city.investment_score || 5.0,
                    price: null,
                    coordinates: city.coordinates
                }));
                setFeaturedLocations(formatted);
                setIsMapLoaded(true);
            } catch (err) {
                logger.error('Failed to load featured locations:', err);
                setFeaturedLocations([
                    { id: 1685, municipalityId: 1685, name: 'Milano', score: 8.7, coordinates: { latitude: 45.4642, longitude: 9.1900 } },
                    { id: 5190, municipalityId: 5190, name: 'Roma', score: 7.2, coordinates: { latitude: 41.9028, longitude: 12.4964 } },
                    { id: 4230, municipalityId: 4230, name: 'Bologna', score: 8.4, coordinates: { latitude: 44.4949, longitude: 11.3426 } },
                    { id: 6016, municipalityId: 6016, name: 'Napoli', score: 4.8, coordinates: { latitude: 40.8518, longitude: 14.2681 } },
                    { id: 4459, municipalityId: 4459, name: 'Firenze', score: 7.9, coordinates: { latitude: 43.7696, longitude: 11.2558 } }
                ]);
                setIsMapLoaded(true);
            }
        };
        loadFeatured();
    }, []);

    const features = [
        {
            icon: (
                <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            ),
            title: 'Demographic Pulse',
            description: 'ISTAT-powered analysis tracking population dynamics, spending power, and social stability for long-term demand prediction.'
        },
        {
            icon: (
                <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
            ),
            title: 'Safety & Hazard Risks',
            description: 'Integrated INGV seismic, ISPRA flood/landslide mapping, and air quality data to protect your capital investment.'
        },
        {
            icon: (
                <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
            ),
            title: 'Yield Projections',
            description: 'Real-time OMI transaction data with historical trends to calculate projected capitalization rates and rental yields.'
        }
    ];

    const quickSearches = ['Milano', 'Roma', 'Bologna', 'Firenze', 'Torino'];

    return (
        <div className="relative overflow-hidden bg-surface-50">
            {/* Hero Section */}
            <section className="relative min-h-[90vh] flex items-center py-20 lg:py-0">
                {/* Background Decorations */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-20 right-0 w-[800px] h-[800px] bg-primary-100/40 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-blob" />
                    <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-indigo-100/30 rounded-full mix-blend-multiply filter blur-3xl opacity-50 animate-blob animation-delay-2000" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-primary-50/50 rounded-full blur-3xl" />
                </div>

                <div className="container mx-auto px-4 relative z-10">
                    <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
                        {/* Left Content */}
                        <div className="max-w-2xl">
                            {/* Live Badge */}
                            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-white border border-gray-200 shadow-sm mb-8 animate-slide-up">
                                <span className="relative flex h-2.5 w-2.5">
                                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success-400 opacity-75" />
                                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-success-500" />
                                </span>
                                <span className="text-xs font-bold text-gray-600 uppercase tracking-wider">
                                    Live 2024 Market Data
                                </span>
                            </div>

                            {/* Headline */}
                            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-black text-gray-900 leading-[1.05] tracking-tight mb-6 animate-slide-up animation-delay-200">
                                Invest in Italian
                                <br />
                                Real Estate with
                                <br />
                                <span className="text-gradient-primary">Precision.</span>
                            </h1>

                            {/* Subheadline */}
                            <p className="text-lg lg:text-xl text-gray-500 leading-relaxed mb-10 max-w-xl animate-slide-up animation-delay-400">
                                The first intelligence platform combining market value, demographics, and hazard risks to deliver a{' '}
                                <span className="text-gray-900 font-semibold">definitive investment score</span> for every Italian municipality.
                            </p>

                            {/* Search */}
                            <div className="mb-8 animate-slide-up animation-delay-600">
                                <SearchBar
                                    onSearch={handleSearch}
                                    placeholder="Search any Italian municipality..."
                                    size="large"
                                />
                                <div className="mt-4 flex flex-wrap items-center gap-2 text-sm">
                                    <span className="text-gray-400 font-medium">Popular:</span>
                                    {quickSearches.map((city) => (
                                        <button
                                            key={city}
                                            onClick={() => handleSearch(city)}
                                            className="px-3 py-1 bg-white border border-gray-200 rounded-lg text-gray-600 hover:border-primary-300 hover:text-primary-600 transition-colors text-sm font-medium"
                                        >
                                            {city}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Stats Row */}
                            <div className="flex flex-wrap gap-4 animate-slide-up animation-delay-600">
                                <StatBadge
                                    value={<><AnimatedCounter end={7900} suffix="+" /></>}
                                    label="Municipalities"
                                    icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>}
                                />
                                <StatBadge
                                    value={<><AnimatedCounter end={50} suffix="M+" /></>}
                                    label="Data Points"
                                    icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
                                />
                                <StatBadge
                                    value={<><AnimatedCounter end={8} suffix="" /></>}
                                    label="Risk Layers"
                                    icon={<svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>}
                                />
                            </div>
                        </div>

                        {/* Right - Map */}
                        <div className="relative animate-slide-in-right animation-delay-400">
                            {/* Glow Effect */}
                            <div className="absolute inset-0 bg-primary-600/10 blur-[100px] rounded-full scale-75" />

                            {/* Map Container */}
                            <div className="relative bg-white rounded-[2rem] p-3 shadow-premium border border-gray-100 rotate-1 hover:rotate-0 transition-transform duration-700">
                                {isMapLoaded ? (
                                    <PropertyMap
                                        center={[42.5, 12.5]}
                                        zoom={5}
                                        locations={featuredLocations}
                                        height="500px"
                                        onLocationClick={handleCityClick}
                                        discoveryMode={true}
                                    />
                                ) : (
                                    <div className="h-[500px] bg-gray-100 rounded-2xl animate-pulse flex items-center justify-center">
                                        <div className="text-gray-400 font-medium">Loading map...</div>
                                    </div>
                                )}

                                {/* Floating Card */}
                                <div className="absolute -bottom-4 -left-4 bg-white p-4 rounded-2xl shadow-xl border border-gray-100 max-w-[180px] -rotate-3 hover:rotate-0 transition-transform duration-300">
                                    <div className="flex items-center space-x-2 mb-1">
                                        <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse" />
                                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">Top Rated</span>
                                    </div>
                                    <div className="text-sm font-bold text-gray-900">
                                        Milano: <span className="text-success-600">8.7/10</span>
                                    </div>
                                </div>

                                {/* Floating Card Right */}
                                <div className="absolute -top-4 -right-4 bg-gray-900 text-white p-4 rounded-2xl shadow-xl max-w-[160px] rotate-3 hover:rotate-0 transition-transform duration-300">
                                    <div className="text-[10px] font-black text-gray-400 uppercase tracking-wider mb-1">AI Analysis</div>
                                    <div className="text-sm font-bold">87% Confidence</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="py-24 lg:py-32 bg-white border-t border-gray-100">
                <div className="container mx-auto px-4">
                    {/* Section Header */}
                    <div className="max-w-2xl mx-auto text-center mb-16">
                        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-primary-50 border border-primary-100 mb-6">
                            <span className="text-xs font-bold text-primary-600 uppercase tracking-wider">
                                Sophisticated Analysis
                            </span>
                        </div>
                        <h2 className="text-3xl lg:text-4xl font-black text-gray-900 tracking-tight leading-tight mb-4">
                            Beyond just market prices.
                            <br />
                            <span className="text-gray-400">Our algorithms look deeper.</span>
                        </h2>
                        <p className="text-lg text-gray-500">
                            Comprehensive data integration from Italy's most trusted institutional sources.
                        </p>
                    </div>

                    {/* Features Grid */}
                    <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                        {features.map((feature, index) => (
                            <FeatureCard
                                key={feature.title}
                                icon={feature.icon}
                                title={feature.title}
                                description={feature.description}
                                delay={index * 100}
                            />
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 lg:py-32 bg-gray-900 relative overflow-hidden">
                {/* Background */}
                <div className="absolute inset-0">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
                </div>

                <div className="container mx-auto px-4 relative z-10">
                    <div className="max-w-3xl mx-auto text-center">
                        <h2 className="text-3xl lg:text-5xl font-black text-white tracking-tight mb-6">
                            Ready to make smarter
                            <br />
                            investment decisions?
                        </h2>
                        <p className="text-lg text-gray-400 mb-10 max-w-xl mx-auto">
                            Start exploring 7,900+ Italian municipalities with institutional-grade investment intelligence.
                        </p>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center">
                            <button
                                onClick={() => navigate('/search')}
                                className="btn btn-lg bg-white text-gray-900 hover:bg-gray-100 font-bold"
                            >
                                Start Exploring Free
                                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                                </svg>
                            </button>
                            <button
                                onClick={() => navigate('/about')}
                                className="btn btn-lg bg-transparent text-white border-2 border-gray-700 hover:border-gray-500 font-bold"
                            >
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
