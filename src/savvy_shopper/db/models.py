import uuid
from datetime import datetime
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from savvy_shopper.db.database import Base


class ResearchSession(Base):
    """Единая таблица исследовательских сессий (с заделом user_id под Инкремент 4)."""
    __tablename__ = "research_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    domain: Mapped[str] = mapped_column(String(64), default="smartphones")
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="PENDING", index=True)
    current_step: Mapped[str] = mapped_column(String(128), default="Ожидание в очереди GPU")
    chat_history: Mapped[list] = mapped_column(JSONB, default=list)
    price_corridor: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    result_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
