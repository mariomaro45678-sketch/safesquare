# Scoring Calibration Investigation — RESOLVED

## Summary
The Roma overall_score issue has been **FIXED**. The score moved from 1.4 to 3.0 after identifying and resolving multiple bugs.

## Root Causes Identified

### 1. Missing Pydantic Schema Field (Primary Issue)
**File**: `backend/app/api/schemas/score.py`,
**Problem**: `ScoreComponentsResponse` was missing the `digital_connectivity` field. Pydantic silently dropped this field from all API responses, even though the engine calculated it correctly.

### 2. Missing API Response Fields
**File**: `backend/app/api/v1/endpoints/scores.py`,
**Problem**: `_format_score_response()` only included 9 of 13 component scores in the response dictionary.

### 3. Overly Aggressive Contrast Enhancement
**File**: `backend/app/core/constants.py`,
**Problem**: `CONTRAST_MULTIPLIER = 3.0` was too aggressive, causing extreme score compression. A raw average of 5.37 became 1.4 with the old multiplier.

### 4. Missing Fields in Temp Score Creation
**File**: `backend/app/api/v1/endpoints/scores.py`
**Problem**: Both municipality and OMI zone endpoints were missing 4 component score fields when creating temporary InvestmentScore objects.

## Fixes Applied

| File | Change |
|------|--------|
| `backend/app/api/schemas/score.py` | Added `digital_connectivity` field to `ScoreComponentsResponse` |
| `backend/app/api/v1/endpoints/scores.py` | Added 4 missing fields to `_format_score_response()` |
| `backend/app/api/v1/endpoints/scores.py` | Added 4 missing fields to both temp_score creations |
| `backend/app/core/constants.py` | Reduced `CONTRAST_MULTIPLIER` from 3.0 to 1.8 |

## Verification

### Before Fix
```json
{
  "overall_score": 1.4,
  "component_scores": {
    "price_trend": 2.98, "affordability": 8.73, ...  // Only 9-12 fields
  }
}
```

### After Fix
```json
{
  "overall_score": 3.0,
  "component_scores": {
    "price_trend": 2.98, "affordability": 8.73, "rental_yield": 6.60,
    "demographics": 10.0, "crime": 5.50, "connectivity": 2.80,
    "digital_connectivity": 1.00, "services": 5.00, "air_quality": 5.50,
    "seismic": 8.34, "flood": 3.08, "landslide": 2.40, "climate": 8.90
  }  // All 13 fields now present
}
```

## Why Roma Scores 3.0 (Poor)

Roma's investment desirability is dragged down by legitimate data issues:

| Component | Score | Interpretation |
|-----------|-------|----------------|
| `digital_connectivity` | 1.0 | Very poor FTTH/mobile coverage in DB |
| `connectivity` | 2.8 | Far from train stations/highways |
| `landslide` | 2.4 | HIGH landslide risk (hilly terrain) |
| `price_trend` | 2.98 | Flat/declining price trend |
| `flood` | 3.1 | HIGH flood risk (Tiber flooding) |

**Note**: Low risk scores mean HIGH risk (they're "investment desirability" scores, not risk levels).

## Next Steps

1. **Verify Roma's infrastructure data** - The digital_connectivity score of 1.0 suggests missing/stale broadband data for Roma
2. **Consider re-running batch scorer** - To update all municipalities with the new 1.8x multiplier
3. **Monitor score distribution** - Ensure the new multiplier provides good differentiation across cities

---
*Fixed: 2026-02-04*
