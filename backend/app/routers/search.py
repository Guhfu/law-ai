from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..schemas import AskRequest, AskResponse
from ..services.llm import generate_answer
from ..services.search import search_relevant_chunks


router = APIRouter(prefix="/api", tags=["search"])


@router.post("/ask", response_model=AskResponse)
async def ask_law_question(
    payload: AskRequest,
    session: AsyncSession = Depends(get_session),
) -> AskResponse:
    sources = await search_relevant_chunks(session, payload)
    answer = await generate_answer(payload, sources)
    return answer

