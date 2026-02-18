import math

def calculate_yield(price_sqm, ref_rent_sqm_annual, context=""):
    # REPLICATING THE LOGIC FROM scoring_engine.py
    
    # 1. Derive Reference Price from Reference Rent (assuming 5.2% base yield for Capital)
    ref_price_sqm = ref_rent_sqm_annual / 0.052
    
    # 2. Calculate Ratio
    p_ratio = price_sqm / ref_price_sqm
    exponent = 0.6
    
    # 3. Derive Local Rent
    derived_rent_sqm_annual = ref_rent_sqm_annual * (p_ratio ** exponent)
    
    # 4. Calculate Final Yield
    derived_yield = (derived_rent_sqm_annual / price_sqm) * 100
    
    # 5. Apply Cap (as implemented in scoring engine)
    # The scoring engine applies: y = max(3.0, min(12.0, y)) for regional
    # and max(2.0, min(9.0, y)) for city.
    # We will show both raw and capped.
    
    cap_min, cap_max = (3.0, 12.0) if "Rural" in context else (2.0, 9.0)
    final_yield = max(cap_min, min(cap_max, derived_yield))
    
    status = "OK"
    if derived_yield > 10.0: status = "HIGH!"
    if derived_yield < 2.5: status = "LOW!"
    
    print(f"{context:<30} | Price: €{price_sqm:>5.0f} | RefPrice: €{ref_price_sqm:>5.0f} | Raw Yield: {derived_yield:>5.2f}% | Capped: {final_yield:>5.2f}% | {status}")
    return derived_yield

print("-" * 110)
print(f"{'SCENARIO':<30} | {'PRICE':>7} | {'REF_PRC':>8} | {'RAW_%':>8} | {'CAP_%':>8} | {'STATUS'}")
print("-" * 110)

# SCENARIO 1: ROME (Capital)
# Ref Rent from OMI Ingestion ~ €117 (with 1.25x market correction -> ~€146)
rome_ref_rent = 117.0 * 1.25 
calculate_yield(7500, rome_ref_rent, "Rome: Centro Storico")
calculate_yield(5200, rome_ref_rent, "Rome: Parioli")
calculate_yield(2800, rome_ref_rent, "Rome: Tuscolana (Mid)")
calculate_yield(1800, rome_ref_rent, "Rome: Periphery")
calculate_yield(1200, rome_ref_rent, "Rome: Deep Periphery")

print("-" * 110)

# SCENARIO 2: RURAL LAZIO (Inherits Rome Baseline)
# Same ref_rent, but prices drops significantly
calculate_yield(1000, rome_ref_rent, "Lazio: Small Town (Rural)")
calculate_yield(600, rome_ref_rent,  "Lazio: Depressed Village (Rural)")
calculate_yield(400, rome_ref_rent,  "Lazio: Ghost Town (Rural)")

# SCENARIO 3: RURAL WEALTHY (Inherits Rome Baseline)
# High prices in province (e.g. Fregene, Castelli)
calculate_yield(4000, rome_ref_rent, "Lazio: Luxury Rural (Rural)")

print("-" * 110)

# SCENARIO 4: MILAN (Higher Base)
# Let's say Milan Avg Rent OMI is €180 -> x1.25 = €225
milan_ref_rent = 180.0 * 1.25
calculate_yield(10000, milan_ref_rent, "Milan: Duomo")
calculate_yield(4000, milan_ref_rent, "Milan: Hinterland")
calculate_yield(2000, milan_ref_rent, "Lombardy: Commuter Town (Rural)")

print("-" * 110)

# SCENARIO 5: POOR REGION (Calabria/Sicily)
# Lower Base. Say Reggio Calabria OMI Rent €50 -> x1.25 = €62.5
south_ref_rent = 50.0 * 1.25
calculate_yield(1200, south_ref_rent, "South: City Center")
calculate_yield(500, south_ref_rent,  "South: Village (Rural)")
calculate_yield(200, south_ref_rent,  "South: Extreme Cheap (Rural)")
