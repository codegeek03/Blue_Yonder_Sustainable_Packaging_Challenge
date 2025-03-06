import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: Optional[str] = None
    
    # Agent weights for final scoring
    QUALITY_WEIGHT: float = 0.20
    ENVIRONMENTAL_WEIGHT: float = 0.25
    REGULATORY_CONSUMER_WEIGHT: float = 0.20
    LOGISTICS_COST_WEIGHT: float = 0.35

    class Config:
        env_file = ".env"

    def validate_api_keys(self):
        if not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set. Please add it to your .env file or environment variables.\n"
                "You can get a Groq API key by signing up at https://console.groq.com"
            )

@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    try:
        settings.validate_api_keys()
    except ValueError as e:
        print("\n" + "="*50)
        print("Configuration Error:")
        print(str(e))
        print("="*50 + "\n")
        raise
    return settings

settings = get_settings()