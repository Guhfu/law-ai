from typing import Sequence

import httpx

from ..config import get_settings
from ..schemas import AskRequest, AskResponse, LawChunkSource


settings = get_settings()


SYSTEM_PROMPT_UA = """
Ви — помічник-юрист з права України.
Відповідайте українською мовою, використовуючи ТІЛЬКИ надані нижче фрагменти законів і кодексів.
Надавайте ПОДРОБНІ, структуровані відповіді: спочатку короткий висновок, потім детальне пояснення з умовами, винятками та практичними нюансами.
ДОЗВОЛЕНО цитувати норми законів і кодексів, обов’язково вказуючи назву акта та номер статті (а також частину/пункт, якщо це очевидно з контексту).
Не надавайте індивідуальних юридичних консультацій, а лише загальну інформацію.
Якщо відповідь неможливо зробити на основі фрагментів, чесно скажіть про це.
"""


def build_context_from_sources(sources: Sequence[LawChunkSource]) -> str:
    lines: list[str] = []
    for s in sources:
        header = (
            f"{s.title} (тип: {s.act_type}, зовн. ID: {s.external_id}, "
            f"стаття: {s.article_number or '-'}, частина: {s.part_number or '-'})"
        )
        lines.append(header)
        lines.append(s.text)
        lines.append("")
    return "\n".join(lines)


async def _call_gemini(messages: list[dict[str, str]]) -> str:
    """
    Вызов Gemini generateContent через REST API.
    """
    if not settings.gemini_api_key:
        return ""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
        f"?key={settings.gemini_api_key}"
    )

    # Преобразуем сообщения в формат Gemini: system_instruction + contents
    system_texts = [m["content"] for m in messages if m["role"] == "system"]
    user_texts = [m["content"] for m in messages if m["role"] == "user"]

    payload: dict = {
        "system_instruction": {
            "parts": [{"text": "\n\n".join(system_texts)}],
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "\n\n".join(user_texts)}],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
        },
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts") or []
    texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
    return "\n".join(t for t in texts if t)


async def generate_answer(
    ask: AskRequest,
    sources: Sequence[LawChunkSource],
) -> AskResponse:
    """
    Генерация ответа через Gemini на основе найденных фрагментов законов.
    """
    context = build_context_from_sources(sources)

    if not settings.gemini_api_key:
        # Заглушка, если ключ не настроен
        fallback_answer = (
            "LLM не налаштована (немає GEMINI_API_KEY). "
            "Ось релевантні фрагменти законодавства, на основі яких слід шукати відповідь:\n\n"
            f"{context}"
        )
        return AskResponse(answer=fallback_answer, sources=list(sources), raw_context=context)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_UA.strip()},
        {
            "role": "user",
            "content": f"Питання користувача:\n{ask.question}\n\nФрагменти законодавства:\n{context}",
        },
    ]

    answer = await _call_gemini(messages)
    return AskResponse(answer=answer, sources=list(sources), raw_context=context)

