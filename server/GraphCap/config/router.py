# src/embedding/retrieve_router.py
from typing import List

import torch
from fastapi import APIRouter, Body, HTTPException, Path
from pydantic import BaseModel

# Import your service functions or classes here
from GraphCap.config.server_controller import controller
from GraphCap.utils.logger import logger

router = APIRouter(prefix="/server", tags=["server"])


@router.get("/health")
async def health_check():
    logger.debug("Health check requested")
    return {"status": "healthy"}


@router.get("/model_info")
async def model_info():
    """Get information about the currently loaded model."""
    logger.info("Model info requested")
    try:
        model_info = {
            "model_name": controller.model.model_name,
            "model_class": controller.model.model_class.__name__,
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
        logger.debug(f"Model info: {model_info}")
        return model_info
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@router.get("/schemas")
async def list_schemas():
    """Get list of all registered schemas and their status."""
    logger.info("Schema list requested")
    try:
        schemas = {}
        for name, entry in controller._schema_library.schemas.items():
            schemas[name] = {
                "status": entry.metadata.status,
                "version": entry.metadata.version,
                "last_updated": entry.metadata.last_updated,
                "dependencies": entry.metadata.dependencies,
            }
        return schemas
    except Exception as e:
        logger.error(f"Error listing schemas: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing schemas: {str(e)}")


@router.get("/schemas/{name}")
async def get_schema_info(name: str = Path(..., description="Name of the schema")):
    """Get detailed information about a specific schema."""
    logger.info(f"Schema info requested for: {name}")
    try:
        entry = await controller._schema_library.get_schema(name)
        return {
            "name": entry.metadata.name,
            "status": entry.metadata.status,
            "version": entry.metadata.version,
            "last_updated": entry.metadata.last_updated,
            "dependencies": entry.metadata.dependencies,
            "error_message": entry.metadata.error_message,
            "has_fsm": entry.fsm is not None,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Schema {name} not found")
    except Exception as e:
        logger.error(f"Error getting schema info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting schema info: {str(e)}")


class SchemaRegistration(BaseModel):
    """Schema for registering a new schema."""

    name: str
    schema: BaseModel
    dependencies: List[str] = []


@router.post("/schemas")
async def register_schema(schema_reg: SchemaRegistration = Body(...)):
    """Register a new schema."""
    logger.info(f"Registering new schema: {schema_reg.name}")
    try:
        entry = await controller.register_schema(schema_reg.name, schema_reg.schema, schema_reg.dependencies)
        return {"name": entry.metadata.name, "status": entry.metadata.status, "version": entry.metadata.version}
    except Exception as e:
        logger.error(f"Error registering schema: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error registering schema: {str(e)}")


@router.post("/schemas/{name}/compile")
async def compile_schema(name: str = Path(..., description="Name of the schema")):
    """Trigger compilation of a specific schema."""
    logger.info(f"Compiling schema: {name}")
    try:
        status = await controller._schema_library.compile_schema(name)
        return {"name": name, "status": status}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Schema {name} not found")
    except Exception as e:
        logger.error(f"Error compiling schema: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error compiling schema: {str(e)}")
