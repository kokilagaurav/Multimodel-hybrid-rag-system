from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENVIRONMENT = os.getenv("APP_ENV", "development")
DEBUG = ENVIRONMENT == "development"
