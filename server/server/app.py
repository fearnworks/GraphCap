"""
# SPDX-License-Identifier: Apache-2.0
Server Application Module

Main FastAPI application setup and configuration.

Key features:
- Server initialization
- CORS configuration
- Router registration
- Lifespan management
- Environment loading

Components:
    app: FastAPI application instance
    lifespan: Server lifecycle manager
"""

# SPDX-License-Identifier: Apache-2.0
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config.router import router as server_router

# from server.providers.router import router as providers_router
from server.utils.logger import logger

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_time = time.time()
    logger.info("Starting server initialization...")
    initialization_time = time.time() - start_time
    logger.info(f"Server initialization completed in {initialization_time:.2f} seconds")
    logger.info("Server available at http://localhost:32100/api/v1")
    yield
    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routers
api_version = "/api/v1"
app.include_router(prefix=api_version, router=server_router)
# app.include_router(prefix=api_version, router=providers_router)
