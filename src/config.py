# src/config.py
import os
from pathlib import Path

# 1. Get the project root directory dynamically
# We are in src/config.py, so we go up two levels: src -> cryptoflow (root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 2. Define standard directories
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"

# 3. (Optional) Define specific file paths
MARKET_DATA_CSV = DATA_DIR / "market_data.csv"

# Debug print to ensure it works when you import it
print(f"Project Root is: {PROJECT_ROOT}")