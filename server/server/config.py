"""
# SPDX-License-Identifier: Apache-2.0
Server Configuration

Manages server configuration settings using Pydantic.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server configuration settings."""

    DATABASE_URL: str = "postgresql+asyncpg://graphcap:graphcap@gcap_postgres:5432/graphcap"
    MAX_CONCURRENT_JOBS: int = 5
    JOB_TIMEOUT_SECONDS: int = 3600  # 1 hour default timeout
    SQL_DEBUG: bool = False

    class Config:
        """Pydantic config."""

        env_file = ".env"


settings = Settings()
