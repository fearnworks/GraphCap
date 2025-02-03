"""
# SPDX-License-Identifier: Apache-2.0
Database Connection Management

Provides database connection and session management.
"""

from typing import AsyncGenerator

from fastapi import FastAPI
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


@retry(
    retry=retry_if_exception_type(Exception),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(5),
)
async def init_db_pool() -> None:
    """Initialize the database connection pool with retry logic."""
    global engine, SessionLocal

    try:
        logger.info(f"Connecting to database at {settings.DATABASE_URL}")
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.SQL_DEBUG,
            pool_pre_ping=True,
        )

        # Test the connection with proper SQL text object
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

        SessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("Database pool initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database pool: {e}")
        raise


async def init_app_db(app: FastAPI) -> None:
    """Initialize database and attach session maker to app state."""
    await init_db_pool()
    app.state.db_session = SessionLocal


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    if SessionLocal is None:
        await init_db_pool()

    async with SessionLocal() as session:  # type: ignore
        try:
            yield session
        finally:
            await session.close()
