import React, { useMemo } from 'react';
import { GeoJSON, Tooltip } from 'react-leaflet';

const ZonePolygonLayer = ({
    zones = [],
    selectedZoneId,
    onZoneClick
}) => {
    // Convert zones array to GeoJSON FeatureCollection
    const geojsonData = useMemo(() => {
        const features = zones
            .filter(zone => zone.geometry && zone.geometry.coordinates)
            .map(zone => ({
                type: 'Feature',
                properties: {
                    zone_id: zone.zone_id,
                    zone_code: zone.zone_code,
                    zone_name: zone.zone_name,
                    zone_type: zone.zone_type,
                    overall_score: zone.overall_score,
                    confidence: zone.confidence
                },
                geometry: zone.geometry
            }));

        return {
            type: 'FeatureCollection',
            features
        };
    }, [zones]);

    // Color based on score
    const getZoneColor = (score) => {
        if (score === null || score === undefined) return '#94a3b8'; // Gray for no score
        if (score >= 7) return '#16a34a'; // Green
        if (score >= 5) return '#eab308'; // Yellow
        return '#e11d48'; // Red
    };

    // Style function for GeoJSON features
    const style = (feature) => {
        const isSelected = feature.properties.zone_id === selectedZoneId;
        const score = feature.properties.overall_score;

        return {
            fillColor: getZoneColor(score),
            fillOpacity: isSelected ? 0.6 : 0.35,
            color: isSelected ? '#3b82f6' : '#ffffff',
            weight: isSelected ? 3 : 1.5,
            opacity: 1,
            dashArray: isSelected ? null : '3'
        };
    };

    // Event handlers for each feature
    const onEachFeature = (feature, layer) => {
        const { zone_name, zone_code, overall_score, zone_type } = feature.properties;
        const displayName = zone_name || zone_code;
        const scoreText = overall_score !== null && overall_score !== undefined
            ? overall_score.toFixed(1)
            : 'N/A';

        // Bind tooltip
        layer.bindTooltip(
            `<div style="padding: 4px 8px;">
                <div style="font-weight: 700; font-size: 13px; margin-bottom: 2px;">${displayName}</div>
                <div style="font-size: 11px; color: #6b7280;">${zone_type || 'Zone'}</div>
                <div style="font-size: 14px; font-weight: 800; margin-top: 4px; color: ${getZoneColor(overall_score)};">
                    Score: ${scoreText}
                </div>
            </div>`,
            {
                permanent: false,
                direction: 'top',
                className: 'zone-tooltip'
            }
        );

        // Event handlers
        layer.on({
            click: () => {
                if (onZoneClick) {
                    onZoneClick(feature.properties);
                }
            },
            mouseover: (e) => {
                const layer = e.target;
                layer.setStyle({
                    fillOpacity: 0.6,
                    weight: 2
                });
                layer.bringToFront();
            },
            mouseout: (e) => {
                const layer = e.target;
                const isSelected = feature.properties.zone_id === selectedZoneId;
                layer.setStyle({
                    fillOpacity: isSelected ? 0.6 : 0.35,
                    weight: isSelected ? 3 : 1.5
                });
            }
        });
    };

    // Don't render if no valid features
    if (geojsonData.features.length === 0) {
        return null;
    }

    // Use key to force re-render when zones or selection changes
    const key = `zones-${zones.length}-${selectedZoneId || 'none'}`;

    return (
        <GeoJSON
            key={key}
            data={geojsonData}
            style={style}
            onEachFeature={onEachFeature}
        />
    );
};

export default ZonePolygonLayer;
