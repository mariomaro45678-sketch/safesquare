import pandas as pd
import os

def create_sample_risks():
    # Codes for Milan (015146), Bergamo (016024), Brescia (017029)
    # Risk types: seismic, flood, landslide
    data = [
        # Milan
        ["015146", "seismic", "Low", 15, 0.05, 0],
        ["015146", "flood", "Medium", 40, 0, 12.5],
        
        # Bergamo
        ["016024", "seismic", "Medium", 35, 0.12, 0],
        ["016024", "landslide", "High", 70, 0, 15.0],
        
        # Brescia
        ["017029", "seismic", "Medium", 45, 0.15, 0],
        ["017029", "flood", "High", 65, 0, 18.0],
    ]
    
    df = pd.DataFrame(data, columns=[
        "Codice_Comune", "Tipo_Rischio", "Livello", "Score", "PGA", "Area_Pct"
    ])
    
    data_dir = "backend/data/raw"
    os.makedirs(data_dir, exist_ok=True)
    
    file_path = os.path.join(data_dir, "risks_sample_lombardia.xlsx")
    df.to_excel(file_path, index=False)
    print(f"Sample risk data created at: {file_path}")

if __name__ == "__main__":
    create_sample_risks()
