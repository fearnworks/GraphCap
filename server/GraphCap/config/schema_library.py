import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type

import outlines
import outlines.samplers
from GraphCap.models.get_vision_model import VisionModel
from GraphCap.utils.logger import logger
from pydantic import BaseModel, Field


class SchemaStatus(str, Enum):
    NOT_LOADED = "not_loaded"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"


class SchemaMetadata(BaseModel):
    name: str
    version: str
    status: SchemaStatus = SchemaStatus.NOT_LOADED
    error_message: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    last_updated: Optional[datetime] = None


class SchemaEntry(BaseModel):
    metadata: SchemaMetadata
    schema: Type[BaseModel]
    fsm: Optional[Any] = None
    generator: Optional[Callable] = None


class SchemaLibrary:
    def __init__(self, max_workers: int = 4):
        self.schemas: Dict[str, SchemaEntry] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = asyncio.Lock()
        logger.info(f"Initialized SchemaLibrary with {max_workers} workers")

    async def register_schema(self, name: str, schema: Type[BaseModel], dependencies: List[str] = []) -> SchemaEntry:
        async with self._lock:
            entry = SchemaEntry(
                metadata=SchemaMetadata(name=name, version="1.0.0", dependencies=dependencies), schema=schema
            )
            self.schemas[name] = entry
            logger.info(f"Registered schema: {name}")
            return entry

    async def create_generator(
        self, name: str, model: VisionModel, temperature: float = 0.5, **generator_kwargs
    ) -> Callable:
        """Create a generator for a schema with the given model."""
        logger.info(f"Creating generator for schema: {name}")

        try:
            entry = await self.get_schema(name)
            if entry.metadata.status != SchemaStatus.LOADED:
                status = await self.compile_schema(name)
                if status != SchemaStatus.LOADED:
                    raise RuntimeError(f"Failed to compile schema: {name}")

            sampler = outlines.samplers.multinomial(temperature=temperature)
            generator = outlines.generate.json(model.model, entry.schema, sampler=sampler, **generator_kwargs)

            # Store the generator in the schema entry
            async with self._lock:
                entry.generator = generator

            logger.info(f"Successfully created generator for schema: {name}")
            return generator

        except Exception as e:
            logger.error(f"Error creating generator for schema {name}: {e}")
            raise

    async def compile_schema(self, name: str) -> SchemaStatus:
        if name not in self.schemas:
            raise KeyError(f"Schema {name} not found")

        entry = self.schemas[name]
        entry.metadata.status = SchemaStatus.LOADING

        try:
            # Compile dependencies first
            for dep in entry.metadata.dependencies:
                await self.wait_for_schema(dep)

            # Compile schema in thread pool
            fsm = await asyncio.get_event_loop().run_in_executor(self.executor, self._compile_fsm, entry.schema)

            async with self._lock:
                entry.fsm = fsm
                entry.metadata.status = SchemaStatus.LOADED
                entry.metadata.last_updated = datetime.now()

            logger.info(f"Successfully compiled schema: {name}")
            return SchemaStatus.LOADED

        except Exception as e:
            entry.metadata.status = SchemaStatus.ERROR
            entry.metadata.error_message = str(e)
            logger.error(f"Error compiling schema {name}: {e}")
            return SchemaStatus.ERROR

    def _compile_fsm(self, schema: BaseModel) -> Any:
        """Actual FSM compilation logic"""
        # TODO: Implement actual FSM compilation
        pass

    async def get_schema(self, name: str) -> SchemaEntry:
        if name not in self.schemas:
            raise KeyError(f"Schema {name} not found")
        return self.schemas[name]

    async def get_generator(self, name: str) -> Optional[Callable]:
        """Get the generator for a schema if it exists."""
        entry = await self.get_schema(name)
        return entry.generator

    async def wait_for_schema(self, name: str, timeout: float = 30.0) -> bool:
        try:
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < timeout:
                entry = await self.get_schema(name)
                if entry.metadata.status == SchemaStatus.LOADED:
                    return True
                elif entry.metadata.status == SchemaStatus.ERROR:
                    raise RuntimeError(f"Schema {name} failed to load: {entry.metadata.error_message}")
                await asyncio.sleep(0.1)
            return False
        except Exception as e:
            logger.error(f"Error waiting for schema {name}: {e}")
            return False
