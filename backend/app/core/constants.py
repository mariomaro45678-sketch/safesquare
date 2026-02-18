"""
Centralized constants for the SafeSquare application.

This module contains all magic numbers and configuration constants
used throughout the application, making them easier to maintain and modify.
"""

# =============================================================================
# SCORING ENGINE CONSTANTS
# =============================================================================

# Score Range
MIN_SCORE = 1.0  # Minimum allowed investment score
MAX_SCORE = 10.0  # Maximum allowed investment score

# Statistical Normalization & Calibration
SCORE_PIVOT = 5.5  # Centered pivot (previously 6.5 was too aggressive)
CONTRAST_MULTIPLIER = 1.3  # Reduced from 1.8 for gentler spread (prevents excessive penalty)
NEUTRAL_FALLBACK_SCORE = 5.5  # Default score when data is unavailable (used when exclusion not possible)
Z_SCORE_SPREAD_FACTOR = 1.414  # sqrt(2) for error function calculation in Z-score normalization

# =============================================================================
# CONNECTIVITY SCORING THRESHOLDS
# =============================================================================

# Train Station Distance Thresholds (kilometers)
TRAIN_EXCELLENT_KM = 3.0  # Distance for excellent train access (10 pts)
TRAIN_GOOD_KM = 10.0      # Distance for good train access (8 pts)
TRAIN_FAIR_KM = 30.0      # Distance for fair train access (5 pts)
# Beyond TRAIN_FAIR_KM = poor access (3 pts)

# Highway Exit Distance Thresholds (kilometers)
HIGHWAY_EXCELLENT_KM = 5.0   # Distance for excellent highway access (10 pts)
HIGHWAY_GOOD_KM = 15.0       # Distance for good highway access (7.5 pts)
HIGHWAY_FAIR_KM = 30.0       # Distance for fair highway access (5 pts)
# Beyond HIGHWAY_FAIR_KM = poor access (2.5 pts)

# Connectivity Weight Distribution
TRAIN_WEIGHT = 0.6    # Train importance in connectivity score
HIGHWAY_WEIGHT = 0.4  # Highway importance in connectivity score

# =============================================================================
# DIGITAL CONNECTIVITY SCORING
# =============================================================================

FTTH_SCORE_DIVISOR = 10.0  # Convert FTTH coverage percentage (0-100) to score (0-10)
TOWER_DENSITY_MULTIPLIER = 2.5  # Mobile tower density to score conversion factor
BROADBAND_WEIGHT = 0.6  # Broadband importance in digital connectivity score
MOBILE_WEIGHT = 0.4     # Mobile importance in digital connectivity score

# =============================================================================
# SERVICES & AMENITIES SCORING
# =============================================================================

# Service count to score conversion multipliers
HOSPITAL_SCORE_MULTIPLIER = 3.0  # sqrt(hospital_count) * multiplier
SCHOOL_SCORE_MULTIPLIER = 1.5    # sqrt(school_count) * multiplier
SUPERMARKET_SCORE_MULTIPLIER = 1.5  # sqrt(supermarket_count) * multiplier

# Service category weights
HOSPITAL_WEIGHT = 0.4      # Healthcare importance
SCHOOL_WEIGHT = 0.3        # Education importance
SUPERMARKET_WEIGHT = 0.3   # Retail importance

# =============================================================================
# CACHE TTL CONFIGURATION
# =============================================================================

CACHE_TTL_SCORES = 21600  # 6 hours - Investment score caching duration (seconds)
CACHE_TTL_FEATURED_LOCATIONS = 21600  # 6 hours - Featured cities caching duration (seconds)

# =============================================================================
# RENTAL YIELD CONSTANTS
# =============================================================================

YIELD_COMPRESSION_EXPONENT = 0.6  # Elasticity factor for rent/price relationship
OMI_RENT_MARKET_CORRECTION = 1.25  # OMI rent vs actual market rent correction factor
BASE_YIELD_ASSUMPTION = 0.052  # 5.2% base yield for capital cities
MAX_RURAL_YIELD = 10.5  # Maximum realistic residential yield for rural areas (%)
MIN_YIELD_CAP = 2.0     # Minimum yield cap (%)
MAX_YIELD_CAP = 9.0     # Maximum yield cap for zone-level calculations (%)

# Fallback yields by property type
FALLBACK_YIELD_COMMERCIAL = 7.5  # High yield for commercial properties
FALLBACK_YIELD_OFFICE = 5.5      # Medium yield for office properties
FALLBACK_YIELD_RESIDENTIAL = 4.5  # Base yield for residential properties

# =============================================================================
# DEFAULT POPULATION (for safety calculations)
# =============================================================================

DEFAULT_POPULATION = 1000  # Fallback population for density calculations
