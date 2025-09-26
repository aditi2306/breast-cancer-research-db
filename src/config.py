from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "breast_demo.db"
DB_URL = f"sqlite:///{DB_PATH}"
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = BASE_DIR / "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
