import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (2 levels up from this file)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"

# Load .env from project root
load_dotenv(dotenv_path=ENV_PATH)

class Settings:
    """Application settings"""
    app_name = "Job Match Analyzer API"
    app_version = "1.0.0"
    frontend_url = "http://localhost:5173"
    openai_api_key = os.getenv("OPENAI_API_KEY")

settings = Settings()

# Validate on import
if not settings.openai_api_key:
    print(f"ERROR: Looking for .env at: {ENV_PATH}")
    print(f"File exists: {ENV_PATH.exists()}")
    raise ValueError("OPENAI_API_KEY not found in .env file!")