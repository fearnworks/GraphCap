"""
# SPDX-License-Identifier: Apache-2.0
Job Dependencies

Provides dependency injection for job management.
"""

from fastapi import Depends
from loguru import logger
from server.db import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from .manager import JobManager


async def get_job_manager(session: AsyncSession = Depends(get_session)) -> JobManager:
    """
    Get job manager instance.

    Args:
        session: Database session

    Returns:
        Initialized job manager
    """
    try:
        return JobManager(session)
    except Exception as e:
        logger.error(f"Failed to initialize job manager: {e}")
        raise RuntimeError(f"Job manager initialization failed: {e}")
