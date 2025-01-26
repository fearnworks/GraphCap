# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

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

            # Use the provider's vision method with its default model and user prompt
            completion = await provider.vision(
                prompt=prompt,
                image=temp_path,
                model=provider.default_model,
                **model_params,  # Pass through any provided model parameters
            )

            return JSONResponse(content={"description": completion.choices[0].message.content})

        finally:
            # Clean up temporary file
            temp_path.unlink()

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
