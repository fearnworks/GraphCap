# SPDX-License-Identifier: Apache-2.0
from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from .provider_manager import ProviderManager

router = APIRouter(
    prefix="/providers",
    tags=["providers"],
)

# Initialize the provider manager
provider_manager = ProviderManager()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_providers():
    """Get a list of all available providers"""
    try:
        providers = provider_manager.clients().values()
        return [
            {
                "name": provider.name,
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
        # Add cloud. prefix if not provided
        if "." not in provider_name:
            provider_name = f"cloud.{provider_name}"

        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

        return {
            "name": provider.name,
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
    prompt: str = "What's in this image? Describe it briefly.",  # Added default prompt
):
    """Analyze an image using the specified provider's default model"""
    try:
        # Add cloud. prefix if not provided
        if "." not in provider_name:
            provider_name = f"cloud.{provider_name}"

        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

        # Save uploaded file temporarily
        temp_path = Path(f"/tmp/{image.filename}")
        with temp_path.open("wb") as f:
            contents = await image.read()
            f.write(contents)

        try:
            # Use the provider's vision method with its default model and user prompt
            completion = provider.vision(
                prompt=prompt,  # Using the provided prompt
                image=temp_path,
                model=provider.default_model,
            )

            return JSONResponse(content={"description": completion.choices[0].message.content})

        finally:
            # Clean up temporary file
            temp_path.unlink()

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
