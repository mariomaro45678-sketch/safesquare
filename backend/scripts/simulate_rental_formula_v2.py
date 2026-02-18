def simulate_v2(correction=1.25, exponent=0.6):
    print(f"\n--- Model V2: Correction={correction}x, Exp={exponent} ---")
    
    city_avg_rent_omi = 117.0
    city_avg_price = 2800.0
    
    # Corrected Base Rent (Market Estimate)
    base_rent_market = city_avg_rent_omi * correction
    base_yield = (base_rent_market / city_avg_price) * 100
    print(f"Base Market Rent: €{base_rent_market/12:.2f}/mo | Base Yield: {base_yield:.2f}%")
    
    zones = [
        {"name": "Centro Storico", "price": 7500.0},
        {"name": "Prati / Parioli", "price": 5200.0},
        {"name": "Tuscolana", "price": 2800.0},
        {"name": "Tor Bella Monaca", "price": 1400.0},
    ]

    for z in zones:
        p_ratio = z['price'] / city_avg_price
        
        # Rent_z = Rent_Base * (Price_z / Price_Base) ^ k
        rent_z = base_rent_market * (p_ratio ** exponent)
        yield_z = (rent_z / z['price']) * 100
        
        print(f"{z['name']:<20} | Price: €{z['price']} | Rent: €{rent_z/12:.2f}/mo | Yield: {yield_z:.2f}%")

if __name__ == "__main__":
    simulate_v2(1.25, 0.6)
    simulate_v2(1.30, 0.6)
