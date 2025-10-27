from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # App settings
    app_name: str = "Job Matcher API"
    app_version: str = "1.0.0"
    
    # OpenAI API key
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # CORS settings
    frontend_url: str = "http://localhost:5173"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()