import logging
import json
import os
import math
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, date
from app.models.geography import Municipality, OMIZone, Province
from app.models.property import PropertyPrice, PropertyType, TransactionType
from app.models.demographics import Demographics, CrimeStatistics
from app.models.risk import SeismicRisk, FloodRisk, LandslideRisk, ClimateProjection, AirQuality
from app.models.score import InvestmentScore
from app.core.constants import (
    MIN_SCORE, MAX_SCORE, SCORE_PIVOT, CONTRAST_MULTIPLIER, NEUTRAL_FALLBACK_SCORE,
    Z_SCORE_SPREAD_FACTOR, TRAIN_EXCELLENT_KM, TRAIN_GOOD_KM, TRAIN_FAIR_KM,
    HIGHWAY_EXCELLENT_KM, HIGHWAY_GOOD_KM, HIGHWAY_FAIR_KM, TRAIN_WEIGHT, HIGHWAY_WEIGHT,
    FTTH_SCORE_DIVISOR, TOWER_DENSITY_MULTIPLIER, BROADBAND_WEIGHT, MOBILE_WEIGHT,
    HOSPITAL_SCORE_MULTIPLIER, SCHOOL_SCORE_MULTIPLIER, SUPERMARKET_SCORE_MULTIPLIER,
    HOSPITAL_WEIGHT, SCHOOL_WEIGHT, SUPERMARKET_WEIGHT, YIELD_COMPRESSION_EXPONENT,
    OMI_RENT_MARKET_CORRECTION, BASE_YIELD_ASSUMPTION, MAX_RURAL_YIELD,
    MIN_YIELD_CAP, MAX_YIELD_CAP, FALLBACK_YIELD_COMMERCIAL, FALLBACK_YIELD_OFFICE,
    FALLBACK_YIELD_RESIDENTIAL, DEFAULT_POPULATION
)

logger = logging.getLogger(__name__)

class ScoringEngine:
    """
    Investment scoring engine.
    Calculates a 1-10 investment score based on Z-Score normalization.
    """
    
    def __init__(self):
        # Optimized weights summing to 1.0
        # Refined based on technical review: Climate increased to 10%, Services decreased to 5%
        self.weights = {
            'price_trend': 0.10,
            'affordability': 0.10,
            'rental_yield': 0.10,
            'demographics': 0.05,
            'crime': 0.05,
            'connectivity': 0.10, 
            'digital_connectivity': 0.10, 
            'services': 0.05,        # DECREASED from 0.10
            'air_quality': 0.10,
            'seismic': 0.05,
            'flood': 0.05,
            'landslide': 0.05,
            'climate': 0.10,         # INCREASED from 0.05
        }
        self.stats = self._load_stats()
        
        # Data Transparency Links
        self.data_links = {
            'price_trend': 'https://www.agenziaentrate.gov.it/portale/schede/fabbricati/omi',
            'affordability': 'https://www.istat.it/',
            'rental_yield': 'https://www.agenziaentrate.gov.it/portale/schede/fabbricati/omi',
            'demographics': 'https://www.istat.it/',
            'crime': 'https://www.istat.it/',
            'connectivity': 'https://www.openstreetmap.org/',
            'digital_connectivity': 'https://maps.agcom.it/',
            'services': 'https://www.openstreetmap.org/',
            'air_quality': 'https://www.snpambiente.it/',
            'seismic': 'https://ingvterremoti.com/',
            'flood': 'https://www.isprambiente.gov.it/',
            'landslide': 'https://www.isprambiente.gov.it/',
            'climate': 'https://climate.copernicus.eu/',
        }

    def _load_stats(self) -> Dict[str, Any]:
        stats_path = os.path.join(os.path.dirname(__file__), "global_stats.json")
        if os.path.exists(stats_path):
            try:
                with open(stats_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load global stats: {e}")
        return {}

    def _z_score_to_points(self, value: float, metric_name: str, inverse: bool = False) -> float:
        """
        Maps a metric to a 1-10 score using Z-Score normalization.
        inverse=True means lower values are better (e.g. Crime, Pollution).
        """
        stats = self.stats.get(metric_name)
        if not stats or stats['std'] == 0:
            return NEUTRAL_FALLBACK_SCORE
            
        z = (value - stats['mean']) / stats['std']
        if inverse:
            z = -z
            
        # 0.5 * (1 + erf(z / sqrt(2))) maps (-inf, inf) to (0, 1)
        # Using 1.0 spread factor for balanced sensitivity
        score = MIN_SCORE + (MAX_SCORE - MIN_SCORE) * (0.5 * (1 + math.erf(z / (Z_SCORE_SPREAD_FACTOR * 1.0)))) 
        return max(MIN_SCORE, min(MAX_SCORE, score))

    def calculate_score(
        self,
        db: Session,
        municipality_id: Optional[int] = None,
        omi_zone_id: Optional[int] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Calculate investment score for a location using statistical normalization.
        """
        # Use a local copy to avoid thread-safety issues with concurrent requests
        weights = self.weights.copy()
        
        if custom_weights:
            # Input validation for custom weights
            for k, v in custom_weights.items():
                if k not in weights:
                    logger.warning(f"Unknown weight key: {k}")
                if not isinstance(v, (int, float)) or v < 0:
                    raise ValueError(f"Invalid weight value for {k}: {v}")
            
            weights.update(custom_weights)
            total_w = sum(weights.values())
            if not abs(total_w - 1.0) < 0.001:
                # Re-normalize to ensure sum is 1.0
                weights = {k: v / total_w for k, v in weights.items()}

        if omi_zone_id:
            target = db.query(OMIZone).filter(OMIZone.id == omi_zone_id).first()
            if not target: raise ValueError(f"OMI zone {omi_zone_id} not found")
            municipality_id = target.municipality_id
            location_name = f"{target.zone_name} ({target.zone_code})"
        elif municipality_id:
            target = db.query(Municipality).filter(Municipality.id == municipality_id).first()
            if not target: raise ValueError(f"Municipality {municipality_id} not found")
            location_name = target.name
        else:
            raise ValueError("Either municipality_id or omi_zone_id must be provided")

        # Track data availability for Confidence Badge
        # Every time a metric uses a real value, confidence increases.
        # Starting coverage counts.
        self._coverage = {}

        scores = {
            'price_trend': self._score_price_trend(db, municipality_id, omi_zone_id),
            'affordability': self._score_affordability(db, municipality_id, omi_zone_id),
            'rental_yield': self._score_rental_yield(db, municipality_id, omi_zone_id),
            'demographics': self._score_demographics(db, municipality_id),
            'crime': self._score_crime_safety(db, municipality_id, omi_zone_id),
            'air_quality': self._score_air_quality(db, municipality_id),
            'connectivity': self._score_connectivity(db, municipality_id),
            'digital_connectivity': self._score_digital_connectivity(db, municipality_id),
            'services': self._score_services(db, municipality_id),
            'seismic': self._score_seismic_risk(db, municipality_id),
            'flood': self._score_flood_risk(db, municipality_id),
            'landslide': self._score_landslide_risk(db, municipality_id),
            'climate': self._score_climate_risk(db, municipality_id),
        }

        # --- Weighted Average with Missing Data Exclusion ---
        # Only include metrics with real data in the weighted average.
        # Re-normalize weights so they sum to 1.0 for available metrics only.
        # This prevents penalizing municipalities for missing data.
        real_metrics = [k for k in scores if self._coverage.get(k) == 'real']

        if real_metrics:
            # Calculate sum of weights for available metrics
            available_weight_sum = sum(weights[k] for k in real_metrics)
            # Re-normalize and calculate weighted average
            if available_weight_sum > 0:
                overall_score = sum(scores[k] * (weights[k] / available_weight_sum) for k in real_metrics)
            else:
                overall_score = NEUTRAL_FALLBACK_SCORE
        else:
            # No real data available - use fallback average
            overall_score = sum(scores[k] * weights[k] for k in scores)
        
        # --- Contrast Enhancement & Empirical Calibration ---
        # 1. The Statistical Context (Central Limit Theorem):
        # Averaging N independent metrics reduces variance by a factor of sqrt(N).
        # For our 13 pillars: σ_average ≈ σ_individual / sqrt(13) ≈ 0.277.
        # This causes raw overall scores to cluster tightly around the mean (central clustering).
        #
        # 2. The Multiplier (3.0x):
        # We restore visual and analytical differentiation by expanding the spread.
        # σ_enhanced = 0.277 * 3.0 ≈ 0.831 (restoring standard deviation to near-individual levels).
        #
        # 3. The Pivot:
        # Empirically, Italian municipalities with high investment potential cluster slightly 
        # above the mathematical neutral mean. The pivot centers the distribution around the
        # specific "Good/Excellent" transition threshold for the Italian market.
        deviation = overall_score - SCORE_PIVOT
        enhanced_score = NEUTRAL_FALLBACK_SCORE + (deviation * CONTRAST_MULTIPLIER) 
        overall_score = max(MIN_SCORE, min(MAX_SCORE, enhanced_score))

        # Calculate Confidence (0.0 - 1.0)
        # Ratio of metrics that used real data vs fallbacks.
        real_data_count = sum(1 for k, v in self._coverage.items() if v == 'real')
        confidence = real_data_count / len(scores) if scores else 0.5

        return {
            'overall_score': round(overall_score, 1),
            'confidence_score': round(confidence, 2),
            'component_scores': scores,
            'weights': weights,
            'location': location_name,
            'data_sources': self.data_links,
            'municipality_id': municipality_id,
            'omi_zone_id': omi_zone_id,
            'calculation_date': date.today().isoformat()
        }

    def _score_connectivity(self, db: Session, mun_id: int) -> float:
        mun = db.query(Municipality).filter(Municipality.id == mun_id).first()
        if not mun:
            self._coverage['connectivity'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE

        has_train = mun.dist_train_station_km is not None
        has_highway = mun.dist_highway_exit_km is not None

        # Mark as real if we have at least one distance measurement
        if has_train or has_highway:
            self._coverage['connectivity'] = 'real'
        else:
            self._coverage['connectivity'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE

        # Train Score (Closer is better)
        train_dist = mun.dist_train_station_km if has_train else 100.0
        if train_dist <= TRAIN_EXCELLENT_KM: train_score = 10.0
        elif train_dist <= TRAIN_GOOD_KM: train_score = 8.0
        elif train_dist <= TRAIN_FAIR_KM: train_score = 5.0
        else: train_score = 3.0

        # Highway Score
        highway_dist = mun.dist_highway_exit_km if has_highway else 100.0
        if highway_dist <= HIGHWAY_EXCELLENT_KM: highway_score = 10.0
        elif highway_dist <= HIGHWAY_GOOD_KM: highway_score = 7.5
        elif highway_dist <= HIGHWAY_FAIR_KM: highway_score = 5.0
        else: highway_score = 2.5

        # Weighted Average - Trains drive value more in Italy
        return (train_score * TRAIN_WEIGHT) + (highway_score * HIGHWAY_WEIGHT)

    def _score_digital_connectivity(self, db: Session, mun_id: int) -> float:
        mun = db.query(Municipality).filter(Municipality.id == mun_id).first()
        if not mun:
            self._coverage['digital_connectivity'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE

        # Check if we have broadband data (FTTH coverage is the primary metric)
        has_ftth = mun.broadband_ftth_coverage is not None and mun.broadband_ftth_coverage > 0

        if has_ftth:
            self._coverage['digital_connectivity'] = 'real'
        else:
            self._coverage['digital_connectivity'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE

        # 1. Broadband Score (FTTH Coverage %)
        ftth = mun.broadband_ftth_coverage
        broadband_score = min(MAX_SCORE, max(MIN_SCORE, ftth / FTTH_SCORE_DIVISOR))

        # 2. Mobile Score (Tower Density)
        pop = mun.population if mun.population and mun.population > 0 else DEFAULT_POPULATION
        towers = mun.mobile_tower_count if mun.mobile_tower_count is not None else 0
        tower_density = (towers / pop) * 10000.0

        # 4 towers/10k pop is good coverage (approx).
        mobile_score = min(MAX_SCORE, max(MIN_SCORE, tower_density * TOWER_DENSITY_MULTIPLIER))

        # Combined
        return (broadband_score * BROADBAND_WEIGHT) + (mobile_score * MOBILE_WEIGHT)

    def _score_services(self, db: Session, mun_id: int) -> float:
        mun = db.query(Municipality).filter(Municipality.id == mun_id).first()
        if not mun:
            self._coverage['services'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE

        # Check if we have any service data
        has_hospitals = mun.hospital_count is not None and mun.hospital_count > 0
        has_schools = mun.school_count is not None and mun.school_count > 0
        has_supermarkets = mun.supermarket_count is not None and mun.supermarket_count > 0

        if has_hospitals or has_schools or has_supermarkets:
            self._coverage['services'] = 'real'
        else:
            self._coverage['services'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE

        # Sqrt(count) dampens the advantage of massive numbers but rewards quantity.
        h_raw = math.sqrt(mun.hospital_count) if mun.hospital_count else 0
        s_raw = math.sqrt(mun.school_count) if mun.school_count else 0
        m_raw = math.sqrt(mun.supermarket_count) if mun.supermarket_count else 0

        # Benchmarks: Hospitals 0->0, 1->3pts, 5->7pts, >10->10pts
        h_score = min(MAX_SCORE, h_raw * HOSPITAL_SCORE_MULTIPLIER)
        # Schools: >50 -> 10pts
        s_score = min(MAX_SCORE, s_raw * SCHOOL_SCORE_MULTIPLIER)
        # Supermarkets: >50 -> 10pts
        m_score = min(MAX_SCORE, m_raw * SUPERMARKET_SCORE_MULTIPLIER)

        return (h_score * HOSPITAL_WEIGHT) + (s_score * SCHOOL_WEIGHT) + (m_score * SUPERMARKET_WEIGHT)

    def save_score(self, db: Session, score_data: Dict[str, Any]) -> InvestmentScore:
        """
        Persists calculation to database with UPSERT logic.
        """
        municipality_id = score_data['municipality_id']
        omi_zone_id = score_data['omi_zone_id']
        calculation_date = date.fromisoformat(score_data['calculation_date'])

        # Check for existing record for the same location and date
        existing = db.query(InvestmentScore).filter(
            InvestmentScore.municipality_id == municipality_id,
            InvestmentScore.omi_zone_id == omi_zone_id,
            InvestmentScore.calculation_date == calculation_date
        ).first()

        cs = score_data['component_scores']
        
        if existing:
            existing.overall_score = score_data['overall_score']
            existing.price_trend_score = cs['price_trend']
            existing.affordability_score = cs['affordability']
            existing.rental_yield_score = cs['rental_yield']
            existing.demographics_score = cs['demographics']
            existing.crime_score = cs['crime']
            existing.air_quality_score = cs['air_quality'] # Added air_quality_score
            existing.connectivity_score = cs.get('connectivity', 5.0)
            existing.digital_connectivity_score = cs.get('digital_connectivity', 5.0) # [NEW]
            existing.services_score = cs.get('services', 5.0) # [NEW]
            existing.seismic_risk_score = cs['seismic']
            existing.flood_risk_score = cs['flood']
            existing.landslide_risk_score = cs['landslide']
            existing.climate_risk_score = cs['climate']
            existing.confidence_score = score_data.get('confidence_score', 0.5)
            existing.weights = score_data['weights']
            score_record = existing
        else:
            score_record = InvestmentScore(
                municipality_id=municipality_id,
                omi_zone_id=omi_zone_id,
                overall_score=score_data['overall_score'],
                confidence_score=score_data.get('confidence_score', 0.5),
                calculation_date=calculation_date,
                price_trend_score=cs['price_trend'],
                affordability_score=cs['affordability'],
                rental_yield_score=cs['rental_yield'],
                demographics_score=cs['demographics'],
                crime_score=cs['crime'],
                air_quality_score=cs['air_quality'],
                connectivity_score=cs.get('connectivity', 5.0),
                digital_connectivity_score=cs.get('digital_connectivity', 5.0), # [NEW]
                services_score=cs.get('services', 5.0), # [NEW]
                seismic_risk_score=cs['seismic'],
                flood_risk_score=cs['flood'],
                landslide_risk_score=cs['landslide'],
                climate_risk_score=cs['climate'],
                weights=score_data['weights']
            )
            db.add(score_record)
        
        db.commit()
        db.refresh(score_record)
        return score_record

    def _score_price_trend(self, db: Session, mun_id: int, zone_id: Optional[int]) -> float:
        """Score based on YoY price growth Z-Score."""
        query = db.query(PropertyPrice).filter(PropertyPrice.property_type == PropertyType.RESIDENTIAL)
        if zone_id: query = query.filter(PropertyPrice.omi_zone_id == zone_id)
        else: query = query.join(OMIZone).filter(OMIZone.municipality_id == mun_id)
        
        prices = query.order_by(desc(PropertyPrice.year), desc(PropertyPrice.semester)).limit(4).all()
        if len(prices) < 2: 
            self._coverage['price_trend'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
        
        old_price = prices[-1].avg_price
        if old_price <= 0: 
            self._coverage['price_trend'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
            
        growth = (prices[0].avg_price - old_price) / old_price * 100
        self._coverage['price_trend'] = 'real'
        return self._z_score_to_points(growth, 'price_trend')

    def _score_affordability(self, db: Session, mun_id: int, zone_id: Optional[int]) -> float:
        """Score based on Income/Price ratio Z-Score."""
        price = db.query(PropertyPrice).filter(PropertyPrice.property_type == PropertyType.RESIDENTIAL)
        if zone_id: price = price.filter(PropertyPrice.omi_zone_id == zone_id)
        else: price = price.join(OMIZone).filter(OMIZone.municipality_id == mun_id)
        
        latest = price.order_by(desc(PropertyPrice.year)).first()
        demog = db.query(Demographics).filter(Demographics.municipality_id == mun_id).order_by(desc(Demographics.year)).first()
        
        if not latest or not demog or not demog.avg_income_euro: 
            self._coverage['affordability'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
        
        # We normalize Income itself (higher is better)
        self._coverage['affordability'] = 'real'
        return self._z_score_to_points(demog.avg_income_euro, 'income')

    def _score_rental_yield(self, db: Session, mun_id: int, zone_id: Optional[int]) -> float:
        """
        Score based on Rental Yield (Rent/Price).
        Target: 4-8% is healthy. <3% is low, >8% is high/risky or undervalued.
        """
        query = db.query(PropertyPrice).filter(PropertyPrice.property_type == PropertyType.RESIDENTIAL)
        if zone_id: query = query.filter(PropertyPrice.omi_zone_id == zone_id)
        else: query = query.join(OMIZone).filter(OMIZone.municipality_id == mun_id)
        
        # Get latest
        price_record = query.order_by(desc(PropertyPrice.year), desc(PropertyPrice.semester)).first()
        
        if not price_record: 
            self._coverage['rental_yield'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
        
        # 1. Use Granular Data if available (Phase 6b)
        if getattr(price_record, 'rental_yield', 0) and price_record.rental_yield > 0:
            y = price_record.rental_yield
            self._coverage['rental_yield'] = 'real'
        elif getattr(price_record, 'min_rent', 0) and price_record.min_rent > 0:
            # Calculate from Zone-level Rent
            annual_rent = ((price_record.min_rent + price_record.max_rent) / 2) * 12
            y = (annual_rent / price_record.avg_price) * 100
            self._coverage['rental_yield'] = 'real'
            
        # 2. Use City-Level Data fallback (Phase 6a - "Silver Tier" + Smart Model)
        else:
            # Fetch municipality rent if available
            mun = db.query(Municipality).filter(Municipality.id == mun_id).first()
            if mun and mun.avg_rent_sqm and mun.avg_rent_sqm > 0:
                # SMART MODEL: Derive Zone Yield from City Average
                # Formula: Rent_z = (Rent_CityAvg * Correction) * (Price_z / Price_CityAvg) ^ k
                
                # Fetch City Average Price (Residential)
                city_avg_price = db.query(func.avg(PropertyPrice.avg_price))\
                    .join(OMIZone)\
                    .filter(OMIZone.municipality_id == mun_id)\
                    .filter(PropertyPrice.year == price_record.year)\
                    .filter(PropertyPrice.property_type == PropertyType.RESIDENTIAL)\
                    .scalar()
                
                if city_avg_price and city_avg_price > 0:
                    market_rent_city = mun.avg_rent_sqm * OMI_RENT_MARKET_CORRECTION
                    p_ratio = price_record.avg_price / city_avg_price
                    
                    derived_rent_sqm = market_rent_city * (p_ratio ** YIELD_COMPRESSION_EXPONENT)
                    y = (derived_rent_sqm / price_record.avg_price) * 100
                    
                    # Cap extreme values to realistic range
                    y = max(MIN_YIELD_CAP, min(MAX_YIELD_CAP, y))
                else:
                    # Fallback if city price calc fails
                    y = (mun.avg_rent_sqm / price_record.avg_price) * 100
            
            # 3. Regional/Province Fallback (Phase 6b - "Countryside Model")
            else:
                # Try getting baseline from Province
                prov = db.query(Province).filter(Province.id == mun.province_id).first()
                if prov and prov.avg_rent_sqm and prov.avg_rent_sqm > 0:
                    # Calculate Province Average Price for calibration
                    # This might be heavy, so we can approximate using the Capital's Rent 
                    # applied to the local price with the standard curve.
                    
                    # Logic: 
                    # Capital Rent ~ €10/sqm (High demand)
                    # Small Town Price ~ €1000 (Low demand) 
                    # Capital Price ~ €3000
                    # Rent_Town = Rent_Cap * (Price_Town / Price_Cap)^0.6
                    
                    # We need a proxy for "Reference Price" associated with "Reference Rent".
                    # Let's assume Reference Price = Reference Rent / 0.05 (5% Yield assumption for Capital)
                    # This allows us to scale purely based on the Rent value.
                    
                    ref_rent = prov.avg_rent_sqm
                    ref_price = ref_rent / BASE_YIELD_ASSUMPTION
                    
                    p_ratio = price_record.avg_price / ref_price
                    
                    derived_rent_sqm = ref_rent * (p_ratio ** YIELD_COMPRESSION_EXPONENT)
                    y = (derived_rent_sqm / price_record.avg_price) * 100
                    
                    # Rural Bonus: Small towns often have higher yields due to illiquidity risk.
                    # We naturally get higher yields from the formula because Price drops faster than Rent.
                    # e.g. Price 30% of Capital -> Rent 48% of Capital -> Yield 1.6x Capital Yield.
                    # So 5% Capital -> 8% Rural. Correct behavior.
                    
                    y = max(MIN_YIELD_CAP, min(MAX_RURAL_YIELD, y))
                    
                else:
                    # 4. Synthetic Fallback (Base Yields)
                    ptype = str(price_record.property_type).upper()
                    if 'COMMERCIALE' in ptype or 'NEGOZIO' in ptype:
                        y = FALLBACK_YIELD_COMMERCIAL
                    elif 'UFFICIO' in ptype:
                        y = FALLBACK_YIELD_OFFICE
                    else:
                        y = FALLBACK_YIELD_RESIDENTIAL
                    
                    # Contextual adjustment (Prices rising fast -> Yield compression)
                    trend = price_record.price_change_yoy or 0
                    if trend > 5.0: y -= 0.5
                    if trend < -2.0: y += 0.5

        # Score Logic (Target 4-8%)
        # > 8% = 10, 6% = 7, 4% = 4, < 3% = 2
        score = min(10.0, max(0.0, (y - 2.0) * 1.6))
        return score

    def _score_demographics(self, db: Session, mun_id: int) -> float:
        demog = db.query(Demographics).filter(Demographics.municipality_id == mun_id).order_by(desc(Demographics.year)).first()
        if not demog or not demog.total_population: 
            self._coverage['demographics'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
        # Use Population Z-score as a proxy for market liquidity
        self._coverage['demographics'] = 'real'
        return self._z_score_to_points(demog.total_population, 'population')

    def _score_crime_safety(self, db: Session, mun_id: int, zone_id: Optional[int] = None) -> float:
        """
        Score based on Crime Risk. 
        Supports sub-municipal granularity for Rome/Milan (Step 25).
        """
        # 1. Try Granular Lookup if Zone is provided
        if zone_id:
            zone = db.query(OMIZone).filter(OMIZone.id == zone_id).first()
            if zone:
                # Fuzzy matching Logic: 
                # Check if we have a sub-municipal stat that matches the zone name
                # Simple containment check for now (e.g. "Parioli" in "Municipio II (Parioli)")
                
                granular_stats = db.query(CrimeStatistics).filter(
                    CrimeStatistics.municipality_id == mun_id,
                    CrimeStatistics.granularity_level == 'sub_municipal'
                ).all()
                
                for stat in granular_stats:
                    if stat.sub_municipal_area and zone.zone_name and \
                       (zone.zone_name.lower() in stat.sub_municipal_area.lower() or \
                        stat.sub_municipal_area.lower() in zone.zone_name.lower()):
                        
                        # Use Granular Risk Index (0-100 where 100=High Risk)
                        # Invert for Score (Higher Score = Safer)
                        # 0 Risk -> 10 Score
                        # 100 Risk -> 0 Score
                        if stat.crime_index is not None:
                            return max(1.0, min(10.0, 10.0 - (stat.crime_index / 10.0)))

        # 2. Fallback to Municipality Level
        crime = db.query(CrimeStatistics).filter(
            CrimeStatistics.municipality_id == mun_id,
            CrimeStatistics.granularity_level == 'municipality' # Explicitly prefer muni-level
        ).first()
        
        # If no explicit 'municipality' record, try any record for that muni (legacy)
        if not crime:
            crime = db.query(CrimeStatistics).filter(CrimeStatistics.municipality_id == mun_id).first()
            
        if not crime or crime.crime_index is None: 
            self._coverage['crime'] = 'fallback'
            # FIXME: Implement spatial inference (3 nearest neighbors weighted avg)
            # instead of neutral fallback. (Priority: Post-MVP)
            return NEUTRAL_FALLBACK_SCORE
        
        # Assuming crime.crime_index is standardized
        self._coverage['crime'] = 'real'
        return self._z_score_to_points(crime.crime_index, 'crime', inverse=True)

    def _score_air_quality(self, db: Session, mun_id: int) -> float:
        aq = db.query(AirQuality).filter(AirQuality.municipality_id == mun_id).order_by(desc(AirQuality.year)).first()
        if not aq or aq.pm25_avg is None: 
            self._coverage['air_quality'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
        self._coverage['air_quality'] = 'real'
        return self._z_score_to_points(aq.pm25_avg, 'air_quality', inverse=True)

    def _score_seismic_risk(self, db: Session, mun_id: int) -> float:
        risk = db.query(SeismicRisk).filter(SeismicRisk.municipality_id == mun_id).first()
        if not risk or risk.risk_score is None: 
            self._coverage['seismic'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
        
        # Standardizing to Z-Score for scientific consistency (Review Priority 3)
        self._coverage['seismic'] = 'real'
        return self._z_score_to_points(risk.risk_score, 'seismic', inverse=True)

    def _score_flood_risk(self, db: Session, mun_id: int) -> float:
        risk = db.query(FloodRisk).filter(FloodRisk.municipality_id == mun_id).first()
        if not risk or risk.risk_score is None: 
            self._coverage['flood'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
            
        self._coverage['flood'] = 'real'
        return self._z_score_to_points(risk.risk_score, 'flood', inverse=True)

    def _score_landslide_risk(self, db: Session, mun_id: int) -> float:
        risk = db.query(LandslideRisk).filter(LandslideRisk.municipality_id == mun_id).first()
        if not risk or risk.risk_score is None: 
            self._coverage['landslide'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
            
        self._coverage['landslide'] = 'real'
        return self._z_score_to_points(risk.risk_score, 'landslide', inverse=True)

    def _score_climate_risk(self, db: Session, mun_id: int) -> float:
        proj = db.query(ClimateProjection).filter(ClimateProjection.municipality_id == mun_id).order_by(desc(ClimateProjection.target_year)).first()
        if not proj or proj.heatwave_days_increase is None: 
            self._coverage['climate'] = 'fallback'
            return NEUTRAL_FALLBACK_SCORE
            
        self._coverage['climate'] = 'real'
        return self._z_score_to_points(proj.heatwave_days_increase, 'climate_heat', inverse=True)
