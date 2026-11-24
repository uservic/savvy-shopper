import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from savvy_shopper.api.schemas import SessionCreateRequest, SessionResponse
from savvy_shopper.core.state_machine import run_research_pipeline
from savvy_shopper.db.database import get_db
from savvy_shopper.db.models import ResearchSession

router = APIRouter(prefix="/api/v1/sessions", tags=["Research Sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    payload: SessionCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    new_session = ResearchSession(user_query=payload.query, domain=payload.domain)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    background_tasks.add_task(run_research_pipeline, new_session.id)
    return new_session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Исследовательская сессия не найдена")
    return session
