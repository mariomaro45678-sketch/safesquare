import pandas as pd
import sys

def inspect_excel(path):
    print(f"Inspecting: {path}")
    df = pd.read_excel(path, nrows=5)
    print("Columns:", df.columns.tolist())
    print("Head:\n", df.head())

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inspect_excel(sys.argv[1])
    else:
        print("Please provide a file path.")
