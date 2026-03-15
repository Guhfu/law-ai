from typing import List, Sequence

import httpx

from ..config import get_settings


settings = get_settings()


async def _embed_single(text: str) -> List[float]:
    """
    Получить эмбеддинг одного текста через Gemini embedContent.
    """
    if not settings.gemini_api_key:
        return []

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_embedding_model}:embedContent"
        f"?key={settings.gemini_api_key}"
    )
    payload = {
        "model": f"models/{settings.gemini_embedding_model}",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_DOCUMENT",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
    embedding = data.get("embedding", {}).get("values", [])
    return embedding


async def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    """
    Возвращает эмбеддинги для списка текстов через Gemini.
    При отсутствии ключа возвращает список пустых векторов.
    """
    if not texts:
        return []

    if not settings.gemini_api_key:
        return [[] for _ in texts]

    return [await _embed_single(t) for t in texts]


async def embed_text(text: str) -> List[float]:
    vectors = await embed_texts([text])
    return vectors[0] if vectors else []

