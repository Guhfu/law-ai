import io
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..models import LawAct, LawChunk


settings = get_settings()


async def download_laws_zip() -> bytes:
    """
    Скачивает ZIP-архив с законами с data.gov.ua.
    В плані зазначено, що в архіві є метадані і повний текст.
    Тут реализуем общий загрузчик по URL.
    """
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(settings.laws_source_url)
        resp.raise_for_status()
        return resp.content


def iter_law_files_from_zip(zip_bytes: bytes) -> Iterable[tuple[str, bytes]]:
    """
    Итерация по файлам внутри ZIP.
    Возвращает пары (имя_файла, содержимое).
    Конкретный формат (XML/JSON/CSV) зависит от архива data.gov.ua;
    здесь мы только извлекаем файлы, а конкретный парсинг оставляем
    в функции parse_and_store_laws, чтобы было проще адаптировать под реальный формат.
    """
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            with zf.open(info) as f:
                yield info.filename, f.read()


async def parse_and_store_laws(session: AsyncSession, zip_bytes: bytes) -> None:
    """
    Общий каркас парсинга:
      - проход по файлам архива;
      - разбор метаданных и текста;
      - фильтрация только действующих актов;
      - разбиение на фрагменты (статьи/частини) и сохранение в БД.

    Поскольку точный формат архива может меняться, здесь оставляем заглушку,
    которую нужно будет адаптировать под реальную структуру файлов.
    """
    # TODO: адаптировать под реальный формат (XML/JSON/CSV) из архива.
    # Для MVP пометим все существующие акты как неактивные, чтобы
    # затем загрузить новые данные, когда форматы будут уточнены.
    await session.execute(update(LawAct).values(is_active=False))
    await session.commit()

    # В этом месте надо распарсить файлы и создать LawAct/LawChunk.
    # Сейчас оставляем "скелет", чтобы не ломать обновление.
    # Пример (псевдокод, НЕ вызывается):
    #
    # acts_to_add: List[LawAct] = []
    # chunks_to_add: List[LawChunk] = []
    # for filename, content in iter_law_files_from_zip(zip_bytes):
    #     ... разобрать content ...
    #     if статус != "чинний": continue
    #     act = LawAct(...)
    #     acts_to_add.append(act)
    #     ...
    # session.add_all(acts_to_add + chunks_to_add)
    # await session.commit()

    return None


async def update_laws_from_source(session: AsyncSession) -> None:
    """
    Высокоуровневая функция: скачать ZIP и обновить базу законов.
    """
    zip_bytes = await download_laws_zip()
    await parse_and_store_laws(session, zip_bytes)

