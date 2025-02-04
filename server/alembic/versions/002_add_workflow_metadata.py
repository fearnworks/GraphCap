"""
Add workflow metadata column to workflows table.
# SPDX-License-Identifier: Apache-2.0
Add Workflow Metadata

Revision ID: 002_add_workflow_metadata
Create Date: 2024-03-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_add_workflow_metadata"
down_revision: str = "001_create_workflows"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add workflow_metadata column and make name unique."""
    # Add workflow_metadata column
    op.add_column(
        "workflows",
        sa.Column(
            "workflow_metadata",
            postgresql.JSONB(),
            nullable=True,
            comment="Optional workflow metadata like version and additional info",
        ),
    )

    # Drop existing index if it exists
    op.drop_index("ix_workflows_name", table_name="workflows")

    # Add unique constraint to name column
    op.create_unique_constraint("uq_workflows_name", "workflows", ["name"])


def downgrade() -> None:
    """Remove workflow_metadata column and revert name to non-unique."""
    # Remove unique constraint
    op.drop_constraint("uq_workflows_name", "workflows")

    # Recreate original index
    op.create_index("ix_workflows_name", "workflows", ["name"])

    # Drop workflow_metadata column
    op.drop_column("workflows", "workflow_metadata")
