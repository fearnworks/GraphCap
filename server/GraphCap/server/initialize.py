# SPDX-License-Identifier: Apache-2.0
import asyncio
import time

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from GraphCap.config.router import router as server_router
from GraphCap.config.server_controller import ServerController
from GraphCap.utils.logger import logger


async def initialize():
    start_time = time.time()
    logger.info("Starting server initialization...")

    logger.info(f"CUDA available: {torch.cuda.is_available()}")
    logger.info(f"Current device: {torch.cuda.current_device()}")
    logger.info(f"Device name: {torch.cuda.get_device_name(0)}")

    app = FastAPI()

    # Get the singleton instance and initialize the model
    logger.info("Initializing server controller...")
    controller = ServerController()
    await controller.initialize_model()  # Await the async initialization

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
