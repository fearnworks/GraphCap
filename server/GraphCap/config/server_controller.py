from threading import Lock
from typing import Dict, List, Optional

from pydantic import BaseModel

from GraphCap.agents.BasicReasoner.BasicReasoner import BasicReasoner
from GraphCap.agents.BasicReasoner.schemas import ChainOfThought
from GraphCap.agents.DenseGraphCaption import DenseGraphCaption, ImageData
from GraphCap.config.schema_library import SchemaEntry, SchemaLibrary
from GraphCap.models.get_vision_model import get_vision_model
from GraphCap.utils.logger import logger


class ServerController:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ServerController, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        with self._lock:
            self._agents: Dict[str, Optional[object]] = {"DenseGraphCaption": None, "BasicReasoner": None}
            self._schema_library = SchemaLibrary()
            self._initialized = True
            logger.info("ServerController singleton initialized")

    async def initialize_model(self) -> None:
        """Initialize all models with required generators."""
        with self._lock:
            if all(agent is not None for agent in self._agents.values()):
                return

            logger.info("Initializing models")
            try:
                # Create shared vision model
                self._model = get_vision_model()

                # Initialize DenseGraphCaption
                if self._agents["DenseGraphCaption"] is None:
                    await self._schema_library.register_schema("dense_caption", ImageData, dependencies=[])

                    caption_generator = await self._schema_library.create_generator(
                        "dense_caption", self._model, temperature=0.5
                    )

                    self._agents["DenseGraphCaption"] = DenseGraphCaption(
                        model=self._model, generator=caption_generator
                    )
                    logger.info("DenseGraphCaption model initialized successfully")

                # Initialize BasicReasoner
                if self._agents["BasicReasoner"] is None:
                    await self._schema_library.register_schema("chain_of_thought", ChainOfThought, dependencies=[])

                    reasoning_generator = await self._schema_library.create_generator(
                        "chain_of_thought", self._model, temperature=0.7
                    )

                    self._agents["BasicReasoner"] = BasicReasoner(model=self._model, generator=reasoning_generator)
                    logger.info("BasicReasoner model initialized successfully")

            except Exception as e:
                logger.error(f"Error initializing models: {str(e)}")
                raise

    def __getitem__(self, key: str) -> Optional[object]:
        """Get an agent by name."""
        with self._lock:
            if key not in self._agents:
                raise KeyError(f"Agent {key} not found")
            return self._agents[key]

    @property
    def model(self) -> Optional[DenseGraphCaption]:
        """Safely get the DenseGraphCaption instance (for backward compatibility)."""
        with self._lock:
            return self._model

    def get_model_info(self) -> dict:
        """Get information about the currently loaded models."""
        with self._lock:
            if not any(self._agents.values()):
                raise ValueError("No models initialized")
            # All agents share the same vision model, so we can use any initialized agent
            for agent in self._agents.values():
                if agent is not None:
                    return agent.model.model_info()
            raise ValueError("No models initialized")

    def shutdown(self) -> None:
        """Safely shutdown the server and cleanup resources."""
        with self._lock:
            for name, agent in self._agents.items():
                if agent is not None:
                    self._agents[name] = None
            logger.info("Server resources cleaned up")

    async def register_schema(self, name: str, schema: BaseModel, dependencies: List[str] = []):
        """Register a new schema with the library"""
        return await self._schema_library.register_schema(name, schema, dependencies)

    async def get_schema(self, name: str) -> SchemaEntry:
        """Get a schema by name"""
        return await self._schema_library.get_schema(name)


controller = ServerController()
