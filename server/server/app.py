"""
# SPDX-License-Identifier: Apache-2.0
Main Application Module

Configures and runs the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import async_sessionmaker

from .db import engine
from .features.workflows.loader import load_stock_workflows
from .features.workflows.router import router as workflow_router
from .routers import pipeline

app = FastAPI(title="GraphCap Server")

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


@app.on_event("startup")
async def startup_event():
    """Load stock workflows on startup."""
    async with async_sessionmaker(engine)() as session:
        await load_stock_workflows(session)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
