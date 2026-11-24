from contextlib import asynccontextmanager
from fastapi import FastAPI
from savvy_shopper.api.routes import router as sessions_router
from savvy_shopper.db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="SavvyShopper API",
    description="Локальный мультиагентный конвейер для исследования товаров и анализа цен",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(sessions_router)


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok"}
