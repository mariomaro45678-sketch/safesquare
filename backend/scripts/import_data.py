import sys
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.data_pipeline.manager import DataPipelineManager

def main():
    if len(sys.argv) < 3:
        print("Usage: python import_data.py <type> <file_path>")
        sys.exit(1)
        
    ingestor_type = sys.argv[1]
    file_path = sys.argv[2]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
        
    db = SessionLocal()
    try:
        manager = DataPipelineManager(db)
        print(f"Starting ingestion for {ingestor_type} from {file_path}...")
        count = manager.run_ingestion(ingestor_type, file_path)
        print(f"Success! Ingested {count} records.")
    except Exception as e:
        print(f"Failed to ingest data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
