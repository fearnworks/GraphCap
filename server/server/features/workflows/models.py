"""
# SPDX-License-Identifier: Apache-2.0
Workflow Models

SQLAlchemy models for workflow management and persistence.

Key features:
- Workflow configuration storage
- Version tracking
- Metadata management

Models:
    Workflow: Stores DAG configurations
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from server.db import Base
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column


class Workflow(Base):
    """
    Workflow model for storing DAG configurations.

    Stores reusable pipeline configurations along with metadata
    for version tracking and organization.

    Attributes:
        id (UUID): Unique identifier
        name (str): Human-readable workflow name
        description (str): Optional workflow description
        config (dict): DAG configuration dictionary
        workflow_metadata (dict): Optional workflow metadata
        created_at (datetime): Creation timestamp
        updated_at (datetime): Last update timestamp
        file_hash (str): File hash for version tracking
    """

    __tablename__ = "workflows"

    id: Mapped[UUID] = mapped_column(PgUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    workflow_metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    file_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())
