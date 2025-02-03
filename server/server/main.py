"""
# SPDX-License-Identifier: Apache-2.0
Main Server Entry Point

Configures and starts the FastAPI server application.
"""

import asyncio
import signal
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_app_db
from .features.workflows.loader import load_stock_workflows
from .features.workflows.router import router as workflow_router
from .providers.router import router as provider_router
from .routers import pipeline
from .utils.logger import logger


class GracefulExit(SystemExit):
    """Custom exception for graceful shutdown."""

    pass


def handle_sigterm(*_: Any) -> None:
    """Handle SIGTERM signal."""
    raise GracefulExit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.

    Handles startup and shutdown events.
    """
    # Setup signal handlers
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    retries = 5
    retry_delay = 5  # seconds

    # Startup
    try:
        for attempt in range(retries):
            try:
                # Initialize database
                await init_app_db(app)
                logger.info("Database initialized")

                # Load stock workflows
                async with app.state.db_session() as session:
                    await load_stock_workflows(session)
                    logger.info("Stock workflows loaded")
                break
            except GracefulExit:
                logger.info("Received shutdown signal during startup")
                raise
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"Startup attempt {attempt + 1} failed: {e}")
                    logger.info(f"Retrying in {retry_delay} seconds... (Press Ctrl+C to cancel)")
                    try:
                        await asyncio.sleep(retry_delay)
                    except asyncio.CancelledError:
                        logger.info("Startup cancelled by user")
                        raise GracefulExit()
                else:
                    logger.error(f"All startup attempts failed: {e}")
                    raise
    except GracefulExit:
        logger.info("Shutting down during startup")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title="GraphCap Server",
    description="API server for GraphCap image processing and graph generation",
    version="0.0.2",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipeline.router)
app.include_router(workflow_router)
app.include_router(provider_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
