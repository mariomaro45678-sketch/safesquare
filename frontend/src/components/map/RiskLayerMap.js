import React, { useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Helper component to update map view when center changes
const MapAutoCenter = ({ center, zoom }) => {
    const map = useMap();
    useEffect(() => {
        map.setView(center, zoom);
    }, [center, zoom, map]);
    return null;
};

const RiskLayerMap = ({
    center = [41.9028, 12.4964],
    zoom = 6,
    riskData = null,
    riskType = 'seismic',
    height = '500px',
}) => {
    // Color mapping for different risk levels
    const getRiskColor = (riskScore) => {
        if (riskScore >= 70) return '#b91c1c'; // Red
        if (riskScore >= 40) return '#ea580c'; // Orange
        if (riskScore >= 20) return '#ca8a04'; // Yellow
        return '#16a34a'; // Green
    };

    // Style function for vector layers (GeoJSON features)
    const style = (feature) => {
        const riskScore = feature.properties?.risk_score || 0;
        return {
            fillColor: getRiskColor(riskScore),
            weight: 1,
            opacity: 1,
            color: 'white',
            fillOpacity: 0.6,
        };
    };

    // Handler for point features (Centroids)
    const pointToLayer = (feature, latlng) => {
        const riskScore = feature.properties?.risk_score || 0;
        return L.circleMarker(latlng, {
            radius: 12,
            fillColor: getRiskColor(riskScore),
            color: "#fff",
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
    };

    // Popup and Hover effects for each feature
    const onEachFeature = (feature, layer) => {
        if (feature.properties) {
            const props = feature.properties;
            layer.bindPopup(`
                <div class="p-2 min-w-[150px]">
                    <h3 class="font-bold border-b pb-1 mb-1 text-gray-800">${props.name || 'Unknown Area'}</h3>
                    <div class="flex justify-between items-center mt-2">
                        <span class="text-xs text-gray-500 uppercase font-bold">Risk Score</span>
                        <span class="font-black text-sm" style="color: ${getRiskColor(props.risk_score)}">${props.risk_score?.toFixed(1) || 'N/A'}</span>
                    </div>
                    <div class="flex justify-between items-center mt-1">
                        <span class="text-xs text-gray-500 uppercase font-bold">Severity</span>
                        <span class="font-bold text-xs">${props.hazard_level || 'N/A'}</span>
                    </div>
                </div>
            `);

            layer.on({
                mouseover: (e) => {
                    const l = e.target;
                    l.setStyle({
                        fillOpacity: 0.9,
                        weight: 3,
                        color: '#3b82f6'
                    });
                },
                mouseout: (e) => {
                    const l = e.target;
                    l.setStyle({
                        fillOpacity: 0.6,
                        weight: 1,
                        color: 'white'
                    });
                }
            });
        }
    };

    return (
        <div className="w-full relative rounded-lg overflow-hidden shadow-lg border border-gray-200" style={{ height }}>
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

                <MapAutoCenter center={center} zoom={zoom} />

                {riskData && (
                    <GeoJSON
                        key={`${riskType}-${JSON.stringify(riskData)}`}
                        data={riskData}
                        style={style}
                        pointToLayer={pointToLayer}
                        onEachFeature={onEachFeature}
                    />
                )}
            </MapContainer>

            {/* Legend */}
            <div className="absolute bottom-4 left-4 bg-white/95 backdrop-blur-sm p-3 rounded-xl shadow-xl z-[1000] border border-gray-100 min-w-[140px]">
                <h4 className="text-[10px] uppercase tracking-widest font-black text-gray-400 mb-3">{riskType} Risk Legend</h4>
                <div className="space-y-2 text-[11px] font-bold text-gray-700">
                    <div className="flex items-center">
                        <div className="w-2.5 h-2.5 rounded-sm bg-red-700 mr-2 border border-white/50 shadow-sm"></div>
                        <span>High (70+)</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-2.5 h-2.5 rounded-sm bg-orange-600 mr-2 border border-white/50 shadow-sm"></div>
                        <span>Moderate (40-69)</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-2.5 h-2.5 rounded-sm bg-yellow-500 mr-2 border border-white/50 shadow-sm"></div>
                        <span>Low (20-39)</span>
                    </div>
                    <div className="flex items-center">
                        <div className="w-2.5 h-2.5 rounded-sm bg-green-600 mr-2 border border-white/50 shadow-sm"></div>
                        <span>Negligible (0-19)</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RiskLayerMap;
