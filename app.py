from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_logger, get_settings
from models import HealthResponse
from routers import (
    drivers_license,
    ghana_card,
    ghana_card_number,
    passport,
    tin,
    voters_id,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def health() -> HealthResponse:
    logger = get_logger()
    logger.info("Open Ghana ID API started successfully.")
    return HealthResponse(message="Welcome to the Open Ghana ID pre-verification API")


app.include_router(passport.router)
app.include_router(ghana_card.router)
app.include_router(voters_id.router)
app.include_router(drivers_license.router)
app.include_router(tin.router)
app.include_router(ghana_card_number.router)
