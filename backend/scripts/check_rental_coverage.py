import pandas as pd

f = "/app/data/raw/Dati_locazioni_capoluoghi_2018_2024.csv"
try:
    df = pd.read_csv(f, sep=';', encoding='latin1')
    cities = df['Comune'].unique()
    print(f"Total Unique Municipalities: {len(cities)}")
    print(f"Sample Cities: {cities[:10]}")
    
    # specific check for Rome
    rome_data = df[df['Comune'].str.contains('ROMA', case=False, na=False)]
    if not rome_data.empty:
        print("\nRome Data Found:")
        print(rome_data.iloc[0].to_dict())
        
        # Calculate derived rent/sqm
        # Canone is often formatted with commas like '705846,182'
        try:
            canone_str = str(rome_data.iloc[0]['Canone annuo in euro  delle abitazioni locate (per le unit\x85 B)'])
            surf_str = str(rome_data.iloc[0]['Superficie in mq delle abitazioni locate (per le unit\x85 B)'])
            
            canone = float(canone_str.replace('.', '').replace(',', '.'))
            surf = float(surf_str.replace('.', '').replace(',', '.'))
            
            rent_sqm_annual = canone / surf
            print(f"Calculated Annual Rent/sqm for Rome: €{rent_sqm_annual:.2f}")
            print(f"Monthly Rent/sqm: €{rent_sqm_annual/12:.2f}")
        except Exception as ex:
            print(f"Calc error: {ex}")
            
    else:
        print("Rome not found.")
        
except Exception as e:
    print(f"Error: {e}")
