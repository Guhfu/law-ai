from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import LawAct, LawChunk
from ..schemas import AskRequest, LawChunkSource
from .embeddings import embed_text


async def search_relevant_chunks(
    session: AsyncSession,
    ask: AskRequest,
) -> List[LawChunkSource]:
    """
    Простейший поиск: первым этапом полнотекстовый/LIKE по тексту,
    затем (опционально) можно расширить до векторного поиска.
    Для MVP делаем полнотекстовый поиск с лимитом по количеству.
    """
    # TODO: при наличии pg_trgm/tsvector улучшить поиск.
    query = (
        select(LawChunk, LawAct)
        .join(LawAct, LawChunk.law_act_id == LawAct.id)
        .where(LawChunk.text.ilike(f"%{ask.question}%"), LawAct.is_active.is_(True))
        .limit(ask.max_chunks)
    )
    result = await session.execute(query)
    rows = result.all()

    sources: List[LawChunkSource] = []
    for chunk, act in rows:
        sources.append(
            LawChunkSource(
                law_act_id=act.id,
                external_id=act.external_id,
                title=act.title,
                act_type=act.act_type,
                article_number=chunk.article_number,
                part_number=chunk.part_number,
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )
        )

    # Заготовка под векторный поиск (на будущее)
    _ = await embed_text(ask.question)

    return sources

