"""
Creates workflow, pipeline jobs, and node state tables.
# SPDX-License-Identifier: Apache-2.0
Create Initial Schema

Revision ID: 001_create_workflows
Create Date: 2024-03-20
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_create_workflows"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial schema."""
    # Create job_status enum type
    job_status = postgresql.ENUM(
        "pending",
        "running",
        "completed",
        "failed",
        "cancelled",
        name="job_status",
        create_type=False,
    )
    job_status.create(op.get_bind(), checkfirst=True)

    # Create pipeline_jobs table
    op.create_table(
        "pipeline_jobs",
        sa.Column("id", postgresql.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("pipeline_id", sa.Text(), nullable=False),
        sa.Column("status", job_status, nullable=False, server_default="pending"),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text()),
        sa.Column("results", postgresql.JSONB()),
        sa.Column("job_metadata", postgresql.JSONB()),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create pipeline_node_states table
    op.create_table(
        "pipeline_node_states",
        sa.Column("id", postgresql.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("job_id", postgresql.UUID(), nullable=False),
        sa.Column("node_id", sa.Text(), nullable=False),
        sa.Column("status", job_status, nullable=False, server_default="pending"),
        sa.Column("result", postgresql.JSONB()),
        sa.Column("error_message", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["job_id"], ["pipeline_jobs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_id", "node_id"),
    )

    # Create workflows table
    op.create_table(
        "workflows",
        sa.Column("id", postgresql.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("config", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index("idx_pipeline_jobs_status", "pipeline_jobs", ["status"])
    op.create_index("idx_pipeline_jobs_created_at", "pipeline_jobs", ["created_at"])
    op.create_index("ix_workflows_name", "workflows", ["name"])


def downgrade() -> None:
    """Remove all created tables and types."""
    # Drop tables in correct order
    op.drop_index("ix_workflows_name")
    op.drop_index("idx_pipeline_jobs_created_at")
    op.drop_index("idx_pipeline_jobs_status")
    op.drop_table("pipeline_node_states")
    op.drop_table("pipeline_jobs")
    op.drop_table("workflows")

    # Drop enum type
    job_status = postgresql.ENUM(name="job_status")
    job_status.drop(op.get_bind(), checkfirst=True)
