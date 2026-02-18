import pandas as pd
import os

def create_sample_omi():
    # Codes for a few Lombardia municipalities (Milan, Bergamo, Brescia)
    # Milan ISTAT: 015146
    # Bergamo ISTAT: 016024
    # Brescia ISTAT: 017029
    
    data = [
        # Milan
        ["015146B1", 2023, 1, "Abitazioni civili", "Vendita", 4500, 7000, "Ottimo"],
        ["015146B1", 2023, 1, "Abitazioni civili", "Locazione", 15, 25, "Ottimo"],
        ["015146C2", 2023, 1, "Abitazioni di tipo economico", "Vendita", 2800, 4200, "Normale"],
        
        # Bergamo
        ["016024A1", 2023, 1, "Abitazioni civili", "Vendita", 3200, 4800, "Ottimo"],
        ["016024B2", 2023, 1, "Abitazioni civili", "Vendita", 2100, 3100, "Normale"],
        
        # Brescia
        ["017029D1", 2023, 1, "Abitazioni civili", "Vendita", 1800, 2600, "Normale"],
    ]
    
    df = pd.DataFrame(data, columns=[
        "Codice_Zona", "Anno", "Semestre", "Tipologia", 
        "Stato_Mercato", "Valore_Minimo", "Valore_Massimo", "Stato_Conservazione"
    ])
    
    data_dir = "backend/data/raw"
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, "omi_sample_lombardia.xlsx")
    df.to_excel(file_path, index=False)
    print(f"Sample OMI data created at: {file_path}")

if __name__ == "__main__":
    create_sample_omi()
