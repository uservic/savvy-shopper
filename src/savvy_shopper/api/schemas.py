import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000, description="Запрос покупателя в свободной форме")
    domain: str = Field(default="smartphones", description="Идентификатор YAML-профиля домена")


class SessionResponse(BaseModel):
    id: uuid.UUID
    domain: str
    user_query: str
    status: str
    current_step: str
    price_corridor: dict | None = None
    result_markdown: str | None = None
    error_message: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
