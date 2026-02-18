import math

def simulate_yields(exponent=0.5):
    print(f"\n--- Simulation with Exponent k={exponent} ---")
    
    # ROME DATA (Silver Tier Ingested)
    city_avg_rent_annual_sqm = 117.0  # From ingestion
    city_avg_rent_yield_gross = 0.058 # Market Report says ~5.8% gross for big cities
    
    # But wait, our data has prices too.
    # Let's assume a City Avg Price to calibrate.
    # If Yield=5.8% and Rent=117 -> Price = 117 / 0.058 = ~2017 eur/sqm.
    # But OMI prices for Rome are higher (~3000?).
    # Let's use relative scaling.
    
    city_avg_price_sqm = 2800.0 # Approx Rome Avg
    
    # Scenarios
    zones = [
        {"name": "Centro Storico (Top)", "price": 7500.0},
        {"name": "Prati / Parioli (High)", "price": 5200.0},
        {"name": "Tuscolana (Mid)", "price": 2800.0},
        {"name": "Tor Bella Monaca (Low)", "price": 1400.0},
    ]
    
    print(f"Baseline: City Rent €{city_avg_rent_annual_sqm}/sqm/yr | Avg Price €{city_avg_price_sqm}/sqm")
    
    for z in zones:
        p_ratio = z['price'] / city_avg_price_sqm
        
        # MODEL: Rent scales with Price, but sub-linearly (diminishing returns)
        # Rent_z = Rent_avg * (Price_z / Price_avg) ^ k
        rent_sqm_annual = city_avg_rent_annual_sqm * (p_ratio ** exponent)
        
        calc_yield = (rent_sqm_annual / z['price']) * 100
        
        print(f"{z['name']:<20} | Price: €{z['price']}/m2 | Rent: €{rent_sqm_annual/12:.2f}/m2/mo | Yield: {calc_yield:.2f}%")

if __name__ == "__main__":
    simulate_yields(0.5)
    simulate_yields(0.6)
    simulate_yields(0.7)
