"""
# SPDX-License-Identifier: Apache-2.0
FastAPI Dependencies

Provides dependency injection for FastAPI endpoints.
"""

from typing import AsyncGenerator

import asyncpg
from fastapi import Depends
from graphcap.job_manager import JobManager

from .db import init_db_pool


async def get_db_pool() -> AsyncGenerator[asyncpg.Pool, None]:
    """Get database connection pool."""
    pool = await init_db_pool()
    try:
        yield pool
    finally:
        await pool.close()


async def get_job_manager(
    pool: asyncpg.Pool = Depends(get_db_pool),
) -> JobManager:
    """Get job manager instance."""
    return JobManager(pool)
