from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class BotSettings(BaseModel):
    telegram_bot_token: str = Field(default=os.getenv("TELEGRAM_BOT_TOKEN", ""))
    backend_base_url: str = Field(
        default=os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
    )


@lru_cache
def get_bot_settings() -> BotSettings:
    return BotSettings()

