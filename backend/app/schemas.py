from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class LawChunkSource(BaseModel):
    law_act_id: int
    external_id: str
    title: str
    act_type: str
    article_number: Optional[str] = None
    part_number: Optional[str] = None
    chunk_index: int
    text: str


class AskRequest(BaseModel):
    question: str
    language: str = "uk"
    max_chunks: int = 8


class AskResponse(BaseModel):
    answer: str
    sources: List[LawChunkSource]
    raw_context: str


class HealthResponse(BaseModel):
    status: str
    time: date

