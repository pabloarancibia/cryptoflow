import os
from pathlib import Path

# project root directory dynamically
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define standard directories
DATA_DIR = PROJECT_ROOT / "data"

# Define specific file paths
MARKET_DATA_CSV = DATA_DIR / "market_data.csv"

# --- Database Config ---
# We use the async driver: postgresql+asyncpg
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/cryptoflow"
)

# Debug print to ensure it works when you import it
print(f"Project Root is: {PROJECT_ROOT}")