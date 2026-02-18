import React from 'react';
import { Link } from 'react-router-dom';

const AboutPage = () => {
    const dataSources = [
        {
            name: "ISTAT",
            full: "Istituto Nazionale di Statistica",
            description: "Providing granular demographic data, resident population trends, and socio-economic indicators since 1926.",
            icon: "📊",
            metrics: "50M+ data points"
        },
        {
            name: "ISPRA",
            full: "Istituto Superiore per la Protezione",
            description: "Source for flood risk (PAI), landslide instability, and national hydrogeological assessments.",
            icon: "🛡️",
            metrics: "7,900+ zones"
        },
        {
            name: "INGV",
            full: "Istituto Nazionale di Geofisica",
            description: "Authoritative seismic hazard maps and historical geophysical data for the entire peninsula.",
            icon: "🌋",
            metrics: "100+ years data"
        },
        {
            name: "OMI",
            full: "Osservatorio del Mercato Immobiliare",
            description: "Official real estate transaction prices and rental yields from Agenzia delle Entrate.",
            icon: "🏠",
            metrics: "2M+ transactions"
        }
    ];

    const scoringFactors = [
        { name: 'Market Value', weight: 25, color: 'bg-primary-600' },
        { name: 'Price Trends', weight: 15, color: 'bg-primary-500' },
        { name: 'Rental Yield', weight: 15, color: 'bg-indigo-500' },
        { name: 'Demographics', weight: 15, color: 'bg-violet-500' },
        { name: 'Seismic Risk', weight: 10, color: 'bg-danger-500' },
        { name: 'Flood Risk', weight: 8, color: 'bg-danger-400' },
        { name: 'Landslide Risk', weight: 6, color: 'bg-warning-500' },
        { name: 'Climate', weight: 6, color: 'bg-success-500' },
    ];

    const stats = [
        { value: '7,900+', label: 'Municipalities' },
        { value: '50M+', label: 'Data Points' },
        { value: '8', label: 'Risk Layers' },
        { value: '99.9%', label: 'Uptime' },
    ];

    return (
        <div className="bg-white min-h-screen">
            {/* Hero Section */}
            <section className="relative pt-20 lg:pt-32 pb-24 lg:pb-40 bg-gradient-to-b from-gray-50 to-white overflow-hidden">
                {/* Background Decorations */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-20 right-20 w-96 h-96 bg-primary-100/50 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-100/30 rounded-full blur-3xl" />
                </div>

                <div className="container mx-auto px-4 relative z-10">
                    <div className="max-w-4xl mx-auto text-center">
                        <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-primary-50 border border-primary-100 mb-8">
                            <span className="text-xs font-bold text-primary-600 uppercase tracking-wider">Our Mission</span>
                        </div>

                        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-gray-900 tracking-tight leading-[1.1] mb-8">
                            Unlocking Professional
                            <br />
                            Real Estate{' '}
                            <span className="text-gradient-primary">Intelligence.</span>
                        </h1>

                        <p className="text-lg lg:text-xl text-gray-500 leading-relaxed max-w-2xl mx-auto mb-12">
                            SafeSquare bridges the gap between complex government data and individual investors.
                            We synthesize millions of data points into actionable investment scores for every Italian municipality.
                        </p>

                        {/* Stats Row */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 max-w-3xl mx-auto">
                            {stats.map((stat, index) => (
                                <div key={index} className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                                    <div className="text-2xl lg:text-3xl font-black text-gray-900">{stat.value}</div>
                                    <div className="text-xs font-bold text-gray-400 uppercase tracking-wider mt-1">{stat.label}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Problem & Solution */}
            <section className="py-24 lg:py-32">
                <div className="container mx-auto px-4">
                    <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center max-w-6xl mx-auto">
                        {/* Problem */}
                        <div>
                            <span className="inline-flex items-center px-3 py-1 rounded-lg bg-danger-50 text-danger-600 text-xs font-bold uppercase tracking-wider mb-4">
                                The Challenge
                            </span>
                            <h2 className="text-3xl lg:text-4xl font-black text-gray-900 tracking-tight mb-6">
                                Data Fragmentation Across Institutions
                            </h2>
                            <p className="text-gray-500 mb-8 leading-relaxed">
                                Italy's real estate market is rich in data, but it's scattered across multiple institutional silos.
                                Understanding the risk of a specific location requires cross-referencing seismic charts from INGV,
                                flood maps from ISPRA, and price trends from OMI.
                            </p>

                            <div className="space-y-4">
                                {[
                                    'Inaccessible raw data formats',
                                    'Complex scientific metrics',
                                    'Time-consuming manual research',
                                    'No unified risk assessment'
                                ].map((item, index) => (
                                    <div key={index} className="flex items-center space-x-3">
                                        <div className="w-6 h-6 bg-danger-100 rounded-lg flex items-center justify-center">
                                            <svg className="w-3 h-3 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </div>
                                        <span className="text-sm font-semibold text-gray-600">{item}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Solution */}
                        <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-[2rem] p-8 lg:p-12 text-white shadow-2xl relative overflow-hidden">
                            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                                <div className="absolute -top-20 -right-20 w-60 h-60 bg-white/10 rounded-full blur-3xl" />
                                <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-white/5 rounded-full blur-3xl" />
                            </div>

                            <div className="relative">
                                <span className="inline-flex items-center px-3 py-1 rounded-lg bg-white/20 text-white text-xs font-bold uppercase tracking-wider mb-4">
                                    Our Solution
                                </span>
                                <h3 className="text-2xl lg:text-3xl font-black mb-6">
                                    Unified Intelligence Platform
                                </h3>
                                <p className="text-primary-100 mb-8 leading-relaxed">
                                    We've built an automated data pipeline that periodically ingests, normalizes,
                                    and geocodes fragmented data into a unified PostGIS-powered analytical engine.
                                </p>

                                <div className="space-y-4">
                                    {[
                                        'Automated GIS Normalization',
                                        'Weighted Scoring Algorithm',
                                        'Hyper-Local Risk Visualization',
                                        'Real-Time Data Updates'
                                    ].map((item, index) => (
                                        <div key={index} className="flex items-center space-x-3">
                                            <div className="w-6 h-6 bg-white/20 rounded-lg flex items-center justify-center">
                                                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                </svg>
                                            </div>
                                            <span className="text-sm font-bold text-white">{item}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Scoring Methodology */}
            <section className="py-24 lg:py-32 bg-gray-50 border-y border-gray-100">
                <div className="container mx-auto px-4">
                    <div className="max-w-4xl mx-auto">
                        <div className="text-center mb-16">
                            <span className="inline-flex items-center px-3 py-1 rounded-lg bg-primary-50 text-primary-600 text-xs font-bold uppercase tracking-wider mb-4">
                                Methodology
                            </span>
                            <h2 className="text-3xl lg:text-4xl font-black text-gray-900 tracking-tight mb-4">
                                How We Calculate Scores
                            </h2>
                            <p className="text-gray-500 max-w-2xl mx-auto">
                                Our investment score is a weighted composite of 8 distinct factors,
                                each normalized to a 0-10 scale based on national benchmarks.
                            </p>
                        </div>

                        <div className="bg-white rounded-3xl p-8 lg:p-10 border border-gray-100 shadow-sm">
                            <div className="space-y-4">
                                {scoringFactors.map((factor, index) => (
                                    <div key={index} className="group">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm font-bold text-gray-700">{factor.name}</span>
                                            <span className="text-sm font-bold text-gray-400">{factor.weight}%</span>
                                        </div>
                                        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full ${factor.color} rounded-full transition-all duration-500 group-hover:opacity-80`}
                                                style={{ width: `${factor.weight * 4}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-8 pt-8 border-t border-gray-100">
                                <p className="text-sm text-gray-500 leading-relaxed">
                                    <strong className="text-gray-700">Note:</strong> Weights are calibrated based on academic research
                                    in real estate investment analysis and may be adjusted as market conditions evolve.
                                    Higher scores indicate better investment potential and lower risk exposure.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Data Sources */}
            <section id="data" className="py-24 lg:py-32">
                <div className="container mx-auto px-4">
                    <div className="text-center mb-16">
                        <span className="inline-flex items-center px-3 py-1 rounded-lg bg-primary-50 text-primary-600 text-xs font-bold uppercase tracking-wider mb-4">
                            Data Partners
                        </span>
                        <h2 className="text-3xl lg:text-4xl font-black text-gray-900 tracking-tight">
                            Institutional Data Sources
                        </h2>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
                        {dataSources.map((source, idx) => (
                            <div
                                key={idx}
                                className="group bg-white p-8 rounded-3xl border border-gray-100 shadow-sm hover:shadow-xl hover:border-primary-200 transition-all duration-300"
                            >
                                <div className="text-4xl mb-6 grayscale group-hover:grayscale-0 transition-all transform group-hover:-translate-y-1">
                                    {source.icon}
                                </div>
                                <h3 className="text-xl font-black text-gray-900 mb-1">{source.name}</h3>
                                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-4 group-hover:text-primary-600 transition-colors">
                                    {source.full}
                                </p>
                                <p className="text-sm text-gray-500 leading-relaxed mb-4">
                                    {source.description}
                                </p>
                                <div className="pt-4 border-t border-gray-100">
                                    <span className="text-xs font-bold text-primary-600">
                                        {source.metrics}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-24 lg:py-32 bg-gray-900 relative overflow-hidden">
                <div className="absolute inset-0">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl" />
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl" />
                </div>

                <div className="container mx-auto px-4 relative z-10">
                    <div className="max-w-3xl mx-auto text-center">
                        <h2 className="text-3xl lg:text-4xl font-black text-white tracking-tight mb-6">
                            Ready to explore the data?
                        </h2>
                        <p className="text-lg text-gray-400 mb-10">
                            Start analyzing 7,900+ Italian municipalities with institutional-grade investment intelligence.
                        </p>
                        <Link
                            to="/search"
                            className="btn btn-lg bg-white text-gray-900 hover:bg-gray-100 font-bold inline-flex"
                        >
                            Start Exploring
                            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                            </svg>
                        </Link>
                    </div>
                </div>
            </section>

            {/* Disclaimer */}
            <section className="py-24">
                <div className="container mx-auto px-4">
                    <div className="max-w-3xl mx-auto">
                        <div className="bg-warning-50 rounded-3xl p-8 lg:p-12 border border-warning-100">
                            <div className="flex items-start space-x-4">
                                <div className="w-12 h-12 bg-warning-100 rounded-xl flex items-center justify-center flex-shrink-0">
                                    <svg className="w-6 h-6 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-warning-900 mb-3">Important Disclaimer</h3>
                                    <p className="text-sm text-warning-800 leading-relaxed">
                                        SafeSquare is an analytical platform designed for research and educational purposes.
                                        While we strive for maximum data accuracy by aggregating official government sources,
                                        the investment scores and risk assessments provided are purely indicative.
                                        Users should never make financial decisions based solely on the scores provided on this platform.
                                        Always consult with certified engineering, geological, and financial professionals before committing to property investments.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default AboutPage;
