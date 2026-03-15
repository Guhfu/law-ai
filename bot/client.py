from typing import Any, Dict

import httpx

from .config import get_bot_settings


settings = get_bot_settings()


async def ask_backend(question: str, language: str = "uk") -> Dict[str, Any]:
    """
    Отправляет запрос к backend /api/ask и возвращает JSON-ответ.
    """
    url = f"{settings.backend_base_url.rstrip('/')}/api/ask"
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json={"question": question, "language": language})
        resp.raise_for_status()
        return resp.json()

