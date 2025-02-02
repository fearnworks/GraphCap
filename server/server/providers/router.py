"""
# SPDX-License-Identifier: Apache-2.0
Provider Router Module

This module implements FastAPI routes for provider operations including
vision analysis and batch processing.

Key features:
- Provider listing and details
- Image analysis endpoints
- Batch processing support
- Structured caption generation
- JSONL export capabilities

Routes:
    GET /providers/: List all providers
    GET /providers/{name}: Get provider details
    POST /providers/{name}/vision: Analyze single image
    POST /providers/{name}/graph_caption: Generate graph caption
    POST /providers/{name}/art_critic: Generate art critic analysis
    POST /providers/{name}/batch_caption: Process multiple images
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from graphcap.providers.provider_manager import ProviderManager
from pydantic import BaseModel, Field

from server.utils.logger import logger

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
)

# Initialize the provider manager
provider_manager = ProviderManager()


class ModelParams(BaseModel):
    """Common parameters for AI model configuration"""

    max_tokens: Optional[int] = Field(default=None, description="Maximum number of tokens to generate")
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Nucleus sampling threshold")


@router.get("/", response_model=List[Dict[str, Any]])
async def list_providers():
    """Get a list of all available providers"""
    try:
        providers = provider_manager.clients().values()
        return [
            {
                "name": provider.name,
                "kind": provider.kind,
                "environment": provider.environment,
                "default_model": provider.default_model,
            }
            for provider in providers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


logger.info("Providers router initialized")
