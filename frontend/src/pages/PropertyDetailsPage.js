import React, { useEffect, useState, useMemo } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { locationAPI, propertyAPI, scoreAPI, riskAPI, demographicsAPI } from '../services/api';
import logger from '../utils/logger';
import ScoreCard from '../components/dashboard/ScoreCard';
import StatCard from '../components/dashboard/StatCard';
import PriceTrendChart from '../components/charts/PriceTrendChart';
import ScoreRadarChart from '../components/charts/ScoreRadarChart';
import PropertyMap from '../components/map/PropertyMap';
import ZoneList from '../components/dashboard/ZoneList';
import ZonePolygonLayer from '../components/map/ZonePolygonLayer';
import { formatNumber, formatCurrency } from '../utils/formatters';

// Skeleton Components
const PageSkeleton = () => (
    <div className="bg-surface-50 min-h-screen pb-20">
        <div className="bg-white border-b border-gray-100 pt-12 pb-8">
            <div className="container mx-auto px-4">
                <div className="skeleton h-8 w-48 mb-4 rounded-lg" />
                <div className="skeleton h-12 w-80 mb-4 rounded-lg" />
                <div className="skeleton h-6 w-64 rounded-lg" />
            </div>
        </div>
        <div className="container mx-auto px-4 mt-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-8">
                    <div className="skeleton h-[200px] rounded-3xl" />
                    <div className="skeleton h-[400px] rounded-3xl" />
                </div>
                <div className="space-y-8">
                    <div className="skeleton h-[300px] rounded-3xl" />
                    <div className="skeleton h-[400px] rounded-3xl" />
                </div>
            </div>
        </div>
    </div>
);

// AI Verdict Component
const AIVerdict = ({ municipality, score, riskData, population }) => {
    const getVerdict = () => {
        if (score >= 7.5) return {
            status: 'Strong Buy',
            color: 'success',
            icon: '🚀',
            message: 'Excellent investment opportunity with strong fundamentals across market, demographic, and safety metrics.'
        };
        if (score >= 6) return {
            status: 'Buy',
            color: 'success',
            icon: '✅',
            message: 'Solid investment potential with favorable market conditions and manageable risk levels.'
        };
        if (score >= 5) return {
            status: 'Hold',
            color: 'warning',
            icon: '⏸️',
            message: 'Moderate investment opportunity. Consider diversifying and monitoring market trends closely.'
        };
        if (score >= 3) return {
            status: 'Caution',
            color: 'warning',
            icon: '⚠️',
            message: 'Below-average investment metrics. Significant due diligence recommended before proceeding.'
        };
        return {
            status: 'High Risk',
            color: 'danger',
            icon: '🛑',
            message: 'Multiple risk factors identified. Investment not recommended without substantial mitigation strategies.'
        };
    };

    const verdict = getVerdict();

    const getBgColor = () => {
        switch (verdict.color) {
            case 'success': return 'from-success-600 to-success-700';
            case 'warning': return 'from-warning-500 to-warning-600';
            case 'danger': return 'from-danger-600 to-danger-700';
            default: return 'from-gray-600 to-gray-700';
        }
    };

    return (
        <div className={`relative overflow-hidden rounded-3xl bg-gradient-to-br ${getBgColor()} text-white p-6 lg:p-8`}>
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-10">
                <div className="absolute -top-10 -right-10 w-40 h-40 border-[30px] border-white rounded-full" />
                <div className="absolute -bottom-20 -left-20 w-60 h-60 border-[30px] border-white rounded-full" />
            </div>

            <div className="relative">
                {/* Header */}
                <div className="flex items-start justify-between mb-6">
                    <div>
                        <div className="flex items-center space-x-2 mb-2">
                            <span className="text-3xl">{verdict.icon}</span>
                            <span className="text-xs font-bold uppercase tracking-widest opacity-80">AI Verdict</span>
                        </div>
                        <h3 className="text-2xl lg:text-3xl font-black">
                            {verdict.status}
                        </h3>
                    </div>
                    <div className="flex flex-col items-end">
                        <span className="text-4xl font-black">{score.toFixed(1)}</span>
                        <span className="text-xs font-bold opacity-70">/10 Score</span>
                    </div>
                </div>

                {/* Message */}
                <p className="text-sm lg:text-base leading-relaxed opacity-90 mb-6">
                    {verdict.message}
                </p>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
                        <p className="text-[10px] font-bold uppercase tracking-wider opacity-70 mb-1">Population</p>
                        <p className="text-lg font-bold">{formatNumber(population)}</p>
                    </div>
                    <div className="bg-white/10 backdrop-blur-sm rounded-xl p-3">
                        <p className="text-[10px] font-bold uppercase tracking-wider opacity-70 mb-1">Risk Factors</p>
                        <p className="text-lg font-bold">{riskData ? ['seismic_risk', 'flood_risk', 'landslide_risk'].filter(k => riskData[k]?.hazard_level?.toLowerCase() === 'high').length : 0} High</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Risk Badge Component
const RiskBadge = ({ level, label }) => {
    const config = {
        high: { bg: 'bg-danger-100', text: 'text-danger-700', dot: 'bg-danger-500' },
        medium: { bg: 'bg-warning-100', text: 'text-warning-700', dot: 'bg-warning-500' },
        low: { bg: 'bg-success-100', text: 'text-success-700', dot: 'bg-success-500' },
        none: { bg: 'bg-gray-100', text: 'text-gray-600', dot: 'bg-gray-400' },
    };
    const styles = config[level] || config.none;

    return (
        <div className={`inline-flex items-center px-3 py-1.5 rounded-xl ${styles.bg}`}>
            <div className={`w-2 h-2 rounded-full ${styles.dot} mr-2`} />
            <span className={`text-xs font-bold ${styles.text}`}>{label}</span>
        </div>
    );
};

const PropertyDetailsPage = () => {
    const { municipalityId: id } = useParams();
    const navigate = useNavigate();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [municipality, setMunicipality] = useState(null);
    const [priceHistory, setPriceHistory] = useState([]);
    const [scoreData, setScoreData] = useState(null);
    const [riskData, setRiskData] = useState(null);
    const [demographics, setDemographics] = useState(null);
    const [statistics, setStatistics] = useState(null);

    // OMI Zone state for large cities
    const [omiZoneScores, setOmiZoneScores] = useState([]);
    const [selectedZone, setSelectedZone] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);

            try {
                const results = await Promise.allSettled([
                    locationAPI.getMunicipality(id),
                    propertyAPI.getPriceHistory(id),
                    scoreAPI.getScore(id),
                    riskAPI.getRisks(id),
                    demographicsAPI.getDemographics(id),
                    propertyAPI.getMunicipalityStatistics(id),
                ]);

                if (results[0].status === 'fulfilled') {
                    setMunicipality(results[0].value);
                } else {
                    throw new Error('Failed to load municipality data');
                }

                if (results[1].status === 'fulfilled') {
                    setPriceHistory((results[1].value || []).slice().reverse());
                }

                if (results[2].status === 'fulfilled') {
                    setScoreData(results[2].value);
                }

                if (results[3].status === 'fulfilled') {
                    setRiskData(results[3].value);
                }

                if (results[4].status === 'fulfilled') {
                    setDemographics(results[4].value);
                }

                if (results[5].status === 'fulfilled') {
                    setStatistics(results[5].value);
                }
            } catch (err) {
                logger.error('Error fetching property details:', err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchData();
        }
    }, [id]);

    // Fetch OMI zone scores for potential large cities
    useEffect(() => {
        if (!municipality?.id) return;

        scoreAPI.getOMIZoneScores(municipality.id)
            .then(data => setOmiZoneScores(data || []))
            .catch(err => {
                logger.error('Failed to load OMI zone scores:', err);
                setOmiZoneScores([]);
            });
    }, [municipality?.id]);

    if (loading) return <PageSkeleton />;

    if (error) {
        return (
            <div className="min-h-screen bg-surface-50 flex items-center justify-center px-4">
                <div className="text-center max-w-md">
                    <div className="w-20 h-20 bg-danger-100 rounded-3xl flex items-center justify-center mx-auto mb-6">
                        <svg className="w-10 h-10 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Unable to Load Data</h2>
                    <p className="text-gray-500 mb-6">{error}</p>
                    <div className="flex justify-center space-x-4">
                        <button
                            onClick={() => navigate(-1)}
                            className="btn btn-secondary"
                        >
                            Go Back
                        </button>
                        <button
                            onClick={() => window.location.reload()}
                            className="btn btn-primary"
                        >
                            Retry
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const investmentScore = scoreData?.overall_score || municipality?.investment_score || 5.0;
    const componentScores = scoreData?.component_scores || {};
    const population = municipality?.population || demographics?.population || 0;
    const incomeIndex = demographics?.median_income_eur ? ((demographics.median_income_eur / 30000) * 100).toFixed(1) : null;

    // Determine if this is a "large city" that warrants zone breakdown
    const isLargeCity = useMemo(() => {
        const pop = municipality?.population || demographics?.population || 0;
        return pop > 100000 || omiZoneScores.length > 5;
    }, [municipality?.population, demographics?.population, omiZoneScores.length]);

    // Map location for the mini-map
    const mapLocations = municipality?.coordinates ? [{
        name: municipality.name,
        coordinates: municipality.coordinates,
        municipalityId: municipality.id,
        score: investmentScore
    }] : [];

    return (
        <div className="bg-surface-50 min-h-screen pb-20">
            {/* Header Section */}
            <div className="bg-white border-b border-gray-100">
                <div className="container mx-auto px-4 py-8 lg:py-12">
                    {/* Breadcrumb */}
                    <nav className="flex items-center space-x-2 text-sm mb-6">
                        <Link to="/" className="text-gray-400 hover:text-primary-600 transition-colors">Home</Link>
                        <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                        <Link to="/search" className="text-gray-400 hover:text-primary-600 transition-colors">Discover</Link>
                        <svg className="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                        <span className="text-gray-900 font-semibold">{municipality?.name}</span>
                    </nav>

                    <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
                        <div>
                            {/* Region Badge */}
                            <div className="flex items-center space-x-2 mb-3">
                                <span className="inline-flex items-center px-3 py-1 rounded-lg bg-primary-50 text-primary-700 text-xs font-bold uppercase tracking-wider">
                                    {municipality?.region_name}
                                </span>
                                <span className="inline-flex items-center px-3 py-1 rounded-lg bg-gray-100 text-gray-600 text-xs font-bold uppercase tracking-wider">
                                    {municipality?.province_code}
                                </span>
                            </div>

                            {/* Municipality Name */}
                            <h1 className="text-4xl lg:text-5xl font-black text-gray-900 tracking-tight mb-2">
                                {municipality?.name}
                            </h1>

                            {/* Quick Stats */}
                            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                                <div className="flex items-center">
                                    <svg className="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                    <span>{formatNumber(population)} residents</span>
                                </div>
                                {municipality?.altitude && (
                                    <div className="flex items-center">
                                        <svg className="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                        </svg>
                                        <span>{municipality.altitude}m altitude</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center space-x-3">
                            <button className="btn btn-secondary">
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                                </svg>
                                Share
                            </button>
                            <button className="btn btn-secondary">
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Export
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Dashboard Content */}
            <div className="container mx-auto px-4 mt-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Column */}
                    <div className="lg:col-span-2 space-y-8">
                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                            <StatCard
                                title="Avg Price"
                                value={statistics?.avg_price_per_sqm ? `€${formatNumber(Math.round(statistics.avg_price_per_sqm))}` : 'N/A'}
                                subtitle="per m²"
                                trend={priceHistory.length >= 2 ?
                                    ((priceHistory[priceHistory.length - 1]?.avg_price - priceHistory[0]?.avg_price) / priceHistory[0]?.avg_price * 100) : null
                                }
                                icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                            />
                            <StatCard
                                title="Population"
                                value={formatNumber(population)}
                                subtitle="residents"
                                trend={demographics?.population_trend}
                                icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" /></svg>}
                            />
                            <StatCard
                                title="Income Index"
                                value={incomeIndex || 'N/A'}
                                subtitle="vs national"
                                icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>}
                            />
                            <StatCard
                                title="Risk Level"
                                value={riskData?.overall_risk_level || 'Low'}
                                subtitle="composite"
                                icon={<svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>}
                            />
                        </div>

                        {/* OMI Zone Breakdown - Large Cities Only */}
                        {isLargeCity && omiZoneScores.length > 0 && (
                            <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                                <div className="p-6 border-b border-gray-100">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="text-lg font-bold text-gray-900">Neighborhood Analysis</h3>
                                            <p className="text-sm text-gray-500 mt-1">
                                                Investment scores by OMI market zone within {municipality?.name}
                                            </p>
                                        </div>
                                        <div className="flex items-center px-3 py-1.5 rounded-xl bg-primary-50">
                                            <span className="text-xs font-bold text-primary-700">
                                                {omiZoneScores.length} Zones
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-0">
                                    {/* Zone List */}
                                    <div className="border-r border-gray-100">
                                        <ZoneList
                                            zones={omiZoneScores}
                                            selectedZoneId={selectedZone?.zone_id}
                                            onZoneSelect={setSelectedZone}
                                            maxHeight="350px"
                                        />
                                    </div>
                                    {/* Selected Zone Detail */}
                                    <div className="p-6 bg-surface-50 flex flex-col">
                                        {selectedZone ? (
                                            <div className="flex-1">
                                                <div className="flex items-start justify-between mb-4">
                                                    <div>
                                                        <h4 className="text-xl font-bold text-gray-900">
                                                            {selectedZone.zone_name || selectedZone.zone_code}
                                                        </h4>
                                                        <p className="text-sm text-gray-500 mt-1">
                                                            {selectedZone.zone_type || 'Zone'} • {selectedZone.zone_code}
                                                        </p>
                                                    </div>
                                                    <button
                                                        onClick={() => setSelectedZone(null)}
                                                        className="text-gray-400 hover:text-gray-600"
                                                    >
                                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                        </svg>
                                                    </button>
                                                </div>
                                                <div className="bg-white rounded-2xl p-6 border border-gray-100 mb-4">
                                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">
                                                        Investment Score
                                                    </p>
                                                    <div className="flex items-end space-x-2">
                                                        <span className={`text-4xl font-black ${
                                                            selectedZone.overall_score >= 7 ? 'text-success-600' :
                                                            selectedZone.overall_score >= 5 ? 'text-warning-600' :
                                                            selectedZone.overall_score ? 'text-danger-600' : 'text-gray-400'
                                                        }`}>
                                                            {selectedZone.overall_score?.toFixed(1) || 'N/A'}
                                                        </span>
                                                        <span className="text-gray-400 font-bold mb-1">/ 10</span>
                                                    </div>
                                                    {selectedZone.confidence && (
                                                        <p className="text-xs text-gray-500 mt-2">
                                                            {Math.round(selectedZone.confidence * 100)}% confidence
                                                        </p>
                                                    )}
                                                </div>
                                                <Link
                                                    to={`/zone/${selectedZone.zone_id}`}
                                                    className="btn btn-primary w-full justify-center"
                                                >
                                                    View Full Zone Analysis
                                                </Link>
                                            </div>
                                        ) : (
                                            <div className="flex-1 flex flex-col items-center justify-center text-center py-8">
                                                <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mb-4">
                                                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                                                    </svg>
                                                </div>
                                                <h4 className="font-bold text-gray-700 mb-2">Select a Zone</h4>
                                                <p className="text-sm text-gray-500 max-w-xs">
                                                    Click on a neighborhood zone from the list or map to view detailed investment analysis
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Price Chart */}
                        <PriceTrendChart data={priceHistory} title="Property Price History" />

                        {/* Risk Map Section */}
                        <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                            <div className="p-6 border-b border-gray-100">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-lg font-bold text-gray-900">Location & Risk Assessment</h3>
                                        <p className="text-sm text-gray-500 mt-1">Geographic positioning and hazard exposure</p>
                                    </div>
                                    {riskData && (
                                        <div className="flex items-center space-x-2">
                                            {riskData.seismic_risk && <RiskBadge level={riskData.seismic_risk.hazard_level?.toLowerCase()} label="Seismic" />}
                                            {riskData.flood_risk && <RiskBadge level={riskData.flood_risk.hazard_level?.toLowerCase()} label="Flood" />}
                                            {riskData.landslide_risk && <RiskBadge level={riskData.landslide_risk.hazard_level?.toLowerCase()} label="Landslide" />}
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div className="h-[400px]">
                                <PropertyMap
                                    center={municipality?.coordinates ? [municipality.coordinates.latitude, municipality.coordinates.longitude] : [41.9, 12.5]}
                                    zoom={isLargeCity && omiZoneScores.length > 0 ? 12 : 11}
                                    locations={mapLocations}
                                    height="100%"
                                    discoveryMode={false}
                                    showControls={false}
                                    onLocationClick={() => { }}
                                >
                                    {/* Render OMI zone polygons for large cities */}
                                    {isLargeCity && omiZoneScores.length > 0 && (
                                        <ZonePolygonLayer
                                            zones={omiZoneScores}
                                            selectedZoneId={selectedZone?.zone_id}
                                            onZoneClick={setSelectedZone}
                                        />
                                    )}
                                </PropertyMap>
                            </div>
                        </div>
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-8">
                        {/* Score Card */}
                        <ScoreCard
                            score={investmentScore}
                            category="Investment Score"
                            description={`Based on comprehensive analysis of market conditions, demographic trends, and risk factors for ${municipality?.name}.`}
                        />

                        {/* Radar Chart */}
                        <ScoreRadarChart componentScores={componentScores} title="Score Breakdown" />

                        {/* AI Verdict */}
                        <AIVerdict
                            municipality={municipality}
                            score={investmentScore}
                            riskData={riskData}
                            population={population}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PropertyDetailsPage;
