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

import io
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from ..caption.art_critic import ArtCriticProcessor
from ..caption.base_caption import BaseCaptionProcessor
from ..caption.graph_caption import GraphCaptionProcessor
from .provider_manager import ProviderManager

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


@router.get("/{provider_name}", response_model=Dict[str, Any])
async def get_provider(provider_name: str):
    """Get details about a specific provider"""
    try:
        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

        return {
            "name": provider.name,
            "kind": provider.kind,
            "environment": provider.environment,
            "env_var": provider.env_var,
            "base_url": provider.base_url,
            "default_model": provider.default_model,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _process_image(
    provider,
    image: UploadFile,
    prompt: str,
    schema: Optional[BaseModel] = None,
    max_tokens: Optional[int] = 1024,
    temperature: Optional[float] = 0.8,
    top_p: Optional[float] = 0.9,
):
    """Core logic for processing images with vision models"""
    # Save uploaded file temporarily
    temp_path = Path(f"/tmp/{image.filename}")
    with temp_path.open("wb") as f:
        contents = await image.read()
        f.write(contents)

    try:
        # Create model parameters dictionary, excluding None values
        model_params = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        model_params = {k: v for k, v in model_params.items() if v is not None}

        # Use the provider's vision method
        completion = await provider.vision(
            prompt=prompt,
            image=temp_path,
            schema=schema,
            model=provider.default_model,
            **model_params,
        )

        return completion

    finally:
        # Clean up temporary file
        temp_path.unlink()


@router.post("/{provider_name}/vision")
async def analyze_image(
    provider_name: str,
    image: UploadFile,
    prompt: str = Form("What's in this image? Describe it briefly."),
    max_tokens: Optional[int] = Form(default=1024),
    temperature: Optional[float] = Form(default=0.8),
    top_p: Optional[float] = Form(default=0.9),
):
    """Analyze an image using the specified provider's default model"""
    try:
        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

        completion = await _process_image(
            provider=provider,
            image=image,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        return JSONResponse(content={"description": completion.choices[0].message.content})

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _process_single_image(
    provider_name: str,
    image: UploadFile,
    processor: BaseCaptionProcessor,
    max_tokens: Optional[int] = 1024,
    temperature: Optional[float] = 0.8,
    top_p: Optional[float] = 0.9,
) -> Dict:
    """Helper function to process a single image with a caption processor."""
    provider = provider_manager.get_client(provider_name)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

    # Save uploaded file temporarily
    temp_path = Path(f"/tmp/{image.filename}")
    try:
        with temp_path.open("wb") as f:
            contents = await image.read()
            f.write(contents)

        result = await processor.process_single(
            provider=provider,
            image_path=temp_path,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return {"parsed": result}
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _get_processor(caption_type: str) -> BaseCaptionProcessor:
    """Get the appropriate caption processor based on type."""
    processors = {
        "graph": GraphCaptionProcessor,
        "art": ArtCriticProcessor,
    }
    processor_class = processors.get(caption_type)
    if not processor_class:
        raise HTTPException(status_code=400, detail=f"Unsupported caption type: {caption_type}")
    return processor_class()


@router.post("/{provider_name}/graph_caption")
async def graph_caption(
    provider_name: str,
    image: UploadFile,
    max_tokens: Optional[int] = Form(default=1024),
    temperature: Optional[float] = Form(default=0.8),
    top_p: Optional[float] = Form(default=0.9),
):
    """Generate structured graph caption for an image"""
    try:
        result = await _process_single_image(
            provider_name=provider_name,
            image=image,
            processor=GraphCaptionProcessor(),
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return JSONResponse(content=result)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider_name}/art_critic")
async def art_critic(
    provider_name: str,
    image: UploadFile,
    max_tokens: Optional[int] = Form(default=1024),
    temperature: Optional[float] = Form(default=0.8),
    top_p: Optional[float] = Form(default=0.9),
):
    """Generate art critic analysis for an image"""
    try:
        result = await _process_single_image(
            provider_name=provider_name,
            image=image,
            processor=ArtCriticProcessor(),
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        return JSONResponse(content=result)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider_name}/batch_caption")
async def batch_caption(
    provider_name: str,
    files: List[UploadFile] = File(description="Multiple image files to process", allow_multiple=True),
    caption_type: str = Form(default="graph", description="Type of caption to generate (graph or art)"),
    max_tokens: Optional[int] = Form(default=1024),
    temperature: Optional[float] = Form(default=0.8),
    top_p: Optional[float] = Form(default=0.9),
):
    """Process multiple images and return structured captions as JSONL"""
    try:
        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

        processor = _get_processor(caption_type)

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            # Save all files to temporary directory
            temp_files = []
            for file in files:
                temp_path = temp_dir_path / file.filename
                with temp_path.open("wb") as f:
                    contents = await file.read()
                    f.write(contents)
                temp_files.append(temp_path)

            results = await processor.process_batch(
                provider=provider,
                image_paths=temp_files,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )

            # Create JSONL response
            output = io.StringIO()
            for result in results:
                output.write(json.dumps(result) + "\n")

            output.seek(0)
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/x-jsonlines",
                headers={"Content-Disposition": "attachment; filename=captions.jsonl"},
            )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=500, detail=str(e))
