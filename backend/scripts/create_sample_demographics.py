import pandas as pd
import os

def create_sample_demographics():
    # Codes for Milan (015146), Bergamo (016024), Brescia (017029)
    data = [
        ["015146", 2023, 1354196, 32500, 5.2],
        ["016024", 2023, 120207, 28400, 4.1],
        ["017029", 2023, 196670, 26800, 4.8],
    ]
    
    df = pd.DataFrame(data, columns=[
        "Codice_Comune", "Anno", "Popolazione_Totale", "Reddito_Medio", "Tasso_Disoccupazione"
    ])
    
    data_dir = "backend/data/raw"
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, "demographics_sample_lombardia.xlsx")
    df.to_excel(file_path, index=False)
    print(f"Sample demographics data created at: {file_path}")

if __name__ == "__main__":
    create_sample_demographics()
