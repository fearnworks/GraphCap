"""
# SPDX-License-Identifier: Apache-2.0
Server Initialization Module

Handles server initialization including CUDA setup and controller configuration.

Key features:
- CUDA device detection
- Server controller initialization
- CORS middleware setup
- Router configuration
- Async initialization support

Functions:
    initialize: Async server initialization
    create_app: Synchronous app creation wrapper
"""

# SPDX-License-Identifier: Apache-2.0
import asyncio
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from graphcap.config.router import router as server_router
from graphcap.utils.logger import logger


async def initialize():
    start_time = time.time()
    logger.info("Starting server initialization...")

    app = FastAPI()

    # Add CORS middleware
    logger.info("Configuring CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add routers to the app
    app.include_router(server_router)

    initialization_time = time.time() - start_time
    logger.info(f"Server initialization completed in {initialization_time:.2f} seconds")

    return app, controller


# Create an event loop and run the initialization
def create_app():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(initialize())


app, controller = create_app()
