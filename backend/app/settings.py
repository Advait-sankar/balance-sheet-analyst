import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATA_PATH: str = os.getenv("DATA_PATH", "data/reliance_2024.json")

settings = Settings()
