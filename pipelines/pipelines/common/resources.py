# SPDX-License-Identifier: Apache-2.0
"""Shared resources for pipeline operations."""

import dagster as dg
from typing import Dict, Any

class PostgresConfig(dg.ConfigurableResource):
    """Configuration for Postgres connections."""
    host: str = "gcap_postgres"
    port: int = 5432
    database: str = "graphcap"
    user: str = "graphcap"
    password: str = "graphcap"

class FileSystemConfig(dg.ConfigurableResource):
    """Configuration for file system operations."""
    workspace_dir: str = "/workspace"
    dataset_dir: str = "/workspace/datasets"
    output_dir: str = "/workspace/.local/output" 