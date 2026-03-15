from datetime import datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class LawAct(Base):
    __tablename__ = "law_acts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    act_type: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(8), index=True, default="uk")
    adopted_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    effective_date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    chunks: Mapped[list["LawChunk"]] = relationship(
        "LawChunk", back_populates="law_act", cascade="all, delete-orphan"
    )


class LawChunk(Base):
    __tablename__ = "law_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    law_act_id: Mapped[int] = mapped_column(
        ForeignKey("law_acts.id", ondelete="CASCADE"), index=True
    )

    article_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    part_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer)

    text: Mapped[str] = mapped_column(Text)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Вектор храним как массив float через pgvector или как JSON,
    # здесь оставляем JSONB для простоты, подключение pgvector можно добавить позже.
    embedding: Mapped[list[float] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    law_act: Mapped[LawAct] = relationship("LawAct", back_populates="chunks")

