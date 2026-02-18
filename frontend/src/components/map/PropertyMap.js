import React, { useEffect, useState, useCallback, useRef } from 'react';
import logger from '../../utils/logger';
import { MapContainer, TileLayer, Marker, Popup, Tooltip, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { locationAPI } from '../../services/api';

// Fix for default marker icons in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// Custom marker icon for scored locations
const createScoreIcon = (score) => {
    // Handle missing or invalid scores gracefully
    if (score === null || score === undefined || isNaN(score)) {
        return L.divIcon({
            className: 'custom-marker marker-appear',
            html: `<div style="background-color: #94a3b8; width: 32px; height: 32px; border-radius: 50%; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.3);"></div>`,
            iconSize: [32, 32],
            iconAnchor: [16, 16],
        });
    }

    const isGreen = score >= 7;
    const isYellow = score >= 5 && score < 7;
    const color = isGreen ? '#16a34a' : isYellow ? '#eab308' : '#e11d48';
    const pulseClass = isGreen ? 'pulse-green' : isYellow ? 'pulse-yellow' : '';
    const glowColor = isGreen ? 'rgba(22, 163, 74, 0.4)' : isYellow ? 'rgba(234, 179, 8, 0.35)' : 'rgba(225, 29, 72, 0.25)';

    return L.divIcon({
        className: `custom-marker ${pulseClass}`,
        html: `
      <div style="
        background: linear-gradient(145deg, ${color} 0%, ${color}dd 100%);
        width: 38px;
        height: 38px;
        border-radius: 50%;
        border: 3px solid white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        color: white;
        box-shadow: 0 4px 16px ${glowColor}, 0 2px 8px rgba(0,0,0,0.2);
        font-size: 13px;
        font-family: 'Inter', system-ui, sans-serif;
        letter-spacing: -0.5px;
        transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        animation: marker-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
        ${isGreen ? 'z-index: 1000;' : isYellow ? 'z-index: 500;' : ''}
      ">
        ${Number(score).toFixed(1)}
      </div>
    `,
        iconSize: [38, 38],
        iconAnchor: [19, 19],
    });
};

// Component to fit map bounds
const FitBounds = ({ coordinates }) => {
    const map = useMap();

    useEffect(() => {
        if (Array.isArray(coordinates) && coordinates.length > 0) {
            try {
                // Filter out any invalid coordinates before fitting
                const validCoords = coordinates.filter(c =>
                    Array.isArray(c) &&
                    c.length === 2 &&
                    !isNaN(c[0]) &&
                    !isNaN(c[1]) &&
                    c[0] !== null &&
                    c[1] !== null &&
                    // Italy Bounding Box (Roughly) to prevent "Null Island" or ocean drifts
                    c[0] > 35 && c[0] < 48 && // Latitude
                    c[1] > 6 && c[1] < 19     // Longitude
                );

                if (validCoords.length > 0) {
                    const bounds = L.latLngBounds(validCoords);
                    if (bounds.isValid()) {
                        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 12 });
                    }
                }
            } catch (err) {
                logger.error('Error fitting map bounds:', err);
            }
        }
    }, [coordinates, map]);

    return null;
};

// Handler for map discovery events
const DiscoveryEvents = ({ onBoundsChange }) => {
    const map = useMapEvents({
        moveend: () => {
            onBoundsChange(map.getBounds(), map.getZoom());
        },
    });

    // Capture initial bounds
    useEffect(() => {
        try {
            const bounds = map.getBounds();
            if (bounds && typeof bounds.getSouthWest === 'function') {
                onBoundsChange(bounds, map.getZoom());
            }
        } catch (err) {
            logger.error('Error getting initial map bounds:', err);
        }
    }, [map, onBoundsChange]);

    return null;
};

const PropertyMap = ({
    center = [41.9028, 12.4964], // Default: Rome
    zoom = 6,
    locations = [],
    onLocationClick,
    height = '500px',
    showControls = true,
    discoveryMode = true,
    children, // Support custom layers like ZonePolygonLayer
}) => {
    const [discoveredLocations, setDiscoveredLocations] = useState([]);
    const [viewBounds, setViewBounds] = useState(null);
    const [viewZoom, setViewZoom] = useState(zoom);
    const [isExploring, setIsExploring] = useState(false);

    const handleBoundsChange = useCallback((bounds, zoomLevel) => {
        setViewBounds(bounds);
        setViewZoom(zoomLevel);
    }, []);

    const handleMarkerClick = (location) => {
        if (onLocationClick) {
            onLocationClick(location);
        }
    };

    // Extract coordinates for bounds fitting (SEARCH RESULTS ONLY)
    // Memoized to prevent referential instability from triggering FitBounds
    const coordinates = React.useMemo(() => locations
        .filter(loc => loc.coordinates)
        .map(loc => [loc.coordinates.latitude, loc.coordinates.longitude]), [locations]);

    useEffect(() => {
        if (!discoveryMode || !viewBounds) return;

        const fetchDiscovery = async () => {
            setIsExploring(true);
            try {
                // Use the robust bounds methods
                const data = await locationAPI.discover(viewBounds, viewZoom);

                // Ensure data is an array
                if (Array.isArray(data)) {
                    const mapped = data.map(m => ({
                        municipalityId: m.id,
                        name: m.name,
                        coordinates: m.coordinates,
                        score: m.investment_score,
                        isDiscovery: true
                    }));
                    setDiscoveredLocations(mapped);
                } else {
                    setDiscoveredLocations([]);
                }
            } catch (err) {
                // Keep error logging but use the standardized logger
                logger.error('Discovery error:', err);
            } finally {
                setIsExploring(false);
            }
        };

        const timer = setTimeout(fetchDiscovery, 800);
        return () => clearTimeout(timer);
    }, [viewBounds, viewZoom, discoveryMode]);

    // Merge search results with discovered locations
    const allLocations = Array.isArray(locations) ? [...locations] : [];
    const seenIds = new Set(allLocations.map(l => l.municipalityId).filter(id => id != null));

    if (Array.isArray(discoveredLocations)) {
        discoveredLocations.forEach(loc => {
            if (loc && loc.municipalityId && !seenIds.has(loc.municipalityId)) {
                allLocations.push(loc);
            }
        });
    }

    return (
        <div className="w-full relative rounded-lg overflow-hidden shadow-lg border border-gray-200" style={{ height }}>
            {/* Discovery Indicator */}
            {discoveryMode && isExploring && (
                <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur shadow-lg rounded-full px-4 py-1.5 z-[1000] border border-gray-100 flex items-center space-x-2">
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                    <span className="text-[10px] font-black uppercase tracking-widest text-gray-500">Exploring Municipalities...</span>
                </div>
            )}
            <MapContainer
                center={center}
                zoom={zoom}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                    url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                />

                {/* Fit bounds to all locations */}
                {coordinates.length > 0 && <FitBounds coordinates={coordinates} />}

                {/* Discovery Mode Events */}
                {discoveryMode && <DiscoveryEvents onBoundsChange={handleBoundsChange} />}

                {/* Custom layers (e.g., ZonePolygonLayer) rendered below markers */}
                {children}

                {/* Render location markers */}
                {allLocations.map((location, index) => {
                    if (!location || !location.coordinates) return null;

                    const { latitude, longitude } = location.coordinates;

                    // CRITICAL: Leaflet crashes if coordinates are NaN or null
                    // Also filter out non-Italian coordinates to prevent "ocean" bugs
                    if (latitude === null || longitude === null ||
                        isNaN(latitude) || isNaN(longitude) ||
                        latitude < 35 || latitude > 48 ||
                        longitude < 6 || longitude > 19) {
                        return null;
                    }

                    const icon = location.score !== undefined ? createScoreIcon(location.score) : undefined;

                    return (
                        <Marker
                            key={location.municipalityId ? `marker-${location.municipalityId}` : `idx-${index}`}
                            position={[latitude, longitude]}
                            icon={icon}
                            eventHandlers={{
                                click: () => handleMarkerClick(location),
                                mouseover: (e) => {
                                    e.target.openTooltip();
                                    if (e.target._icon && e.target._icon.style) {
                                        e.target._icon.style.transform += ' scale(1.15)';
                                        e.target._icon.style.zIndex = 1000;
                                    }
                                },
                                mouseout: (e) => {
                                    e.target.closeTooltip();
                                    if (e.target._icon && e.target._icon.style) {
                                        e.target._icon.style.transform = e.target._icon.style.transform.replace(' scale(1.15)', '');
                                        e.target._icon.style.zIndex = 100;
                                    }
                                }
                            }}
                        >
                            <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                                <div className="font-bold text-xs uppercase tracking-tighter">
                                    {location.name || 'Unknown'}
                                </div>
                            </Tooltip>
                            <Popup>
                                <div className="p-3 min-w-[200px]">
                                    <h3 className="font-bold text-gray-900 border-b pb-1 mb-1">{location.name || 'Unknown'}</h3>
                                    {location.score != null && (
                                        <div className="mt-2 flex items-center justify-between">
                                            <span className="text-xs text-gray-500 uppercase font-black tracking-tighter">Investment Score</span>
                                            <span className={`text-lg font-black ${location.score >= 7 ? 'text-green-600' : location.score >= 5 ? 'text-yellow-600' : 'text-red-600'}`}>
                                                {Number(location.score).toFixed(1)}
                                            </span>
                                        </div>
                                    )}
                                    {location.price && (
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm text-gray-600">Avg Price:</span>
                                            <span className="font-semibold">{location.price} €/m²</span>
                                        </div>
                                    )}
                                    <button
                                        onClick={() => handleMarkerClick(location)}
                                        className="w-full mt-2 bg-blue-600 text-white text-xs py-2 rounded hover:bg-blue-700 transition"
                                    >
                                        View Insights
                                    </button>
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>

            {/* Legend */}
            {showControls && allLocations.some(loc => loc.score) && (
                <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-4 rounded-2xl shadow-2xl z-[1000] border border-white/20 min-w-[180px]">
                    <h4 className="text-[10px] uppercase tracking-[0.2em] font-black text-gray-400 mb-4">Investment Potential</h4>
                    <div className="space-y-3">
                        <div className="flex items-center text-xs font-bold text-gray-700">
                            <div className="w-3 h-3 rounded-full bg-[#16a34a] mr-3 border-2 border-white shadow-sm"></div>
                            <span>High (7.0 - 10.0)</span>
                        </div>
                        <div className="flex items-center text-xs font-bold text-gray-700">
                            <div className="w-3 h-3 rounded-full bg-[#eab308] mr-3 border-2 border-white shadow-sm"></div>
                            <span>Moderate (5.0 - 6.9)</span>
                        </div>
                        <div className="flex items-center text-xs font-bold text-gray-700">
                            <div className="w-3 h-3 rounded-full bg-[#e11d48] mr-3 border-2 border-white shadow-sm"></div>
                            <span>Low/Risk (0.0 - 4.9)</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PropertyMap;
