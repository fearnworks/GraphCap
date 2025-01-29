# SPDX-License-Identifier: Apache-2.0
import asyncio
import io
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field

from ..caption.graph_caption import graphcap_vision_config
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
        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

        completion = await _process_image(
            provider=provider,
            image=image,
            prompt=graphcap_vision_config.prompt,
            schema=graphcap_vision_config.schema,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        # If using schema, the completion will already be parsed into the schema model
        if isinstance(completion, BaseModel):
            return completion

        # Get just the parsed content from the message
        parsed_content = completion.choices[0].message.parsed
        return JSONResponse(content={"parsed": parsed_content})

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider_name}/batch_caption")
async def batch_caption(
    provider_name: str,
    files: List[UploadFile] = File(description="Multiple image files to process", allow_multiple=True),
    max_tokens: Optional[int] = Form(default=1024),
    temperature: Optional[float] = Form(default=0.8),
    top_p: Optional[float] = Form(default=0.9),
):
    """Process multiple images and return structured captions as JSONL

    Accepts multiple image files uploaded simultaneously and processes them in parallel.
    Returns a JSONL file with captions for each image.
    """
    try:
        provider = provider_manager.get_client(provider_name)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_name} not found")

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
                temp_files.append((file.filename, temp_path))

            # Process images concurrently
            async def process_single_image(filename: str, image_path: Path):
                try:
                    completion = await provider.vision(
                        prompt=graphcap_vision_config.prompt,
                        image=image_path,
                        schema=graphcap_vision_config.schema,
                        model=provider.default_model,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        top_p=top_p,
                    )

                    logger.debug(f"Raw completion for {filename}: {completion}")

                    # Handle both Pydantic model and raw completion responses
                    if isinstance(completion, BaseModel):
                        # Extract just the parsed content from the Pydantic model and convert to dict
                        result = completion.choices[0].message.parsed
                        if isinstance(result, BaseModel):
                            result = result.model_dump()
                        logger.debug(f"Pydantic model parsed result for {filename}: {result}")
                    else:
                        # Navigate through the nested structure to get the final parsed data
                        result = completion.choices[0].message.parsed
                        logger.debug(f"Initial parsed result for {filename}: {result}")

                        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

                        if "choices" in result:
                            logger.debug(f"Found nested choices in result for {filename}")
                            # Get the innermost parsed data
                            result = result["choices"][0]["message"]["parsed"]["parsed"]
                        elif "message" in result:
                            logger.debug(f"Found nested message in result for {filename}")
                            result = result["message"]["parsed"]

                    logger.debug(f"Final parsed result for {filename}: {result}")

                    return {"filename": filename, "parsed": result}
                except Exception as e:
                    logger.error(f"Error processing {filename}: {str(e)}")
                    logger.exception(e)
                    return {"filename": filename, "error": str(e)}

            # Process all images concurrently
            tasks = [process_single_image(filename, image_path) for filename, image_path in temp_files]
            results = await asyncio.gather(*tasks)

            # Create JSONL response
            output = io.StringIO()
            for result in results:
                output.write(json.dumps(result) + "\n")

            output.seek(0)

            # Return streaming response with JSONL file
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="application/x-jsonlines",
                headers={"Content-Disposition": "attachment; filename=captions.jsonl"},
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
