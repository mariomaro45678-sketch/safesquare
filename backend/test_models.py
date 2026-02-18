import sys
import os

# Add the backend directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine
from app.models.base import Base
# Import models to ensure they are registered with Base.metadata
import app.models

try:
    # Try to create tables (will verify model definitions)
    print("Verifying model definitions and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("SUCCESS: All models are valid and tables can be created!")
except Exception as e:
    print(f"ERROR: Model validation failed: {e}")
    sys.exit(1)
