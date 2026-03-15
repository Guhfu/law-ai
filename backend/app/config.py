from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Settings(BaseModel):
    app_name: str = "UA Law LLM Backend"
    debug: bool = Field(default=False)

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/ua_law_llm",
        description="SQLAlchemy database URL for PostgreSQL",
    )

    # Gemini API settings
    gemini_api_key: str = Field(default=os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = Field(
        default=os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    )
    gemini_embedding_model: str = Field(
        default=os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    )

    laws_source_url: str = Field(
        default=os.getenv(
            "LAWS_SOURCE_URL",
            "https://data.gov.ua/dataset/c98e830c-e39e-4da6-a13c-f9ba32a79bec/resource/5616dd04-949a-489c-8efc-54004293b238/download",
        ),
        description="Base URL for ZIP archive with UA laws",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

