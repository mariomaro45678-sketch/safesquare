
from pathlib import Path

def find_table():
    path = Path("Rete di Monitoraggio Regionale - Arpac.html")
    if not path.exists():
        print("File not found")
        return

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "LatLng" in line or "marker" in line or "coordinate" in line or "google.maps" in line:
            print(f"Match at line {i+1}: {line.strip()[:150]}")
            # Print next few lines
            for j in range(1, 5):
                if i+j < len(lines):
                    print(f"  {i+1+j}: {lines[i+j].strip()[:150]}")
            
if __name__ == "__main__":
    find_table()
