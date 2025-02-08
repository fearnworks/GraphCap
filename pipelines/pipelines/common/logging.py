# SPDX-License-Identifier: Apache-2.0
"""Custom logging setup for Dagster pipelines."""

import logging


def configure_loggers():
    """Configures custom loggers for different levels."""
    dagster_logger = logging.getLogger("dagster")
    dagster_logger.setLevel(logging.DEBUG)  # Set default Dagster logger level

    # Create handlers for different log levels
    debug_handler = logging.FileHandler("/workspace/logs/gcap_pipelines/debug.log")
    debug_handler.setLevel(logging.DEBUG)
    error_handler = logging.FileHandler("/workspace/logs/gcap_pipelines/error.log")
    error_handler.setLevel(logging.ERROR)

    # Define formatters
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    debug_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # Add handlers to the Dagster logger
    dagster_logger.addHandler(debug_handler)
    dagster_logger.addHandler(error_handler)

    return {"custom_logger": dagster_logger}
