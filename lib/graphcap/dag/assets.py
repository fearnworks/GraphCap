"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.assets

Provides the base AssetNode class for representing data assets in the graphcap DAG system.

Key features:
- Base class for data-producing nodes
- Output schema validation
- Asset identity and metadata tracking
- Integration with DAG execution context

Classes:
    AssetNode: Base class for nodes that produce data assets
"""

from typing import Any, Optional, Sequence

from .decorators import asset_node
from .node import BaseNode, NodeExecutionContext


@asset_node
class AssetNode(BaseNode):
    """
    Base class for nodes that produce data assets in the graphcap pipeline.

    AssetNodes represent tangible data objects like datasets, image collections,
    processed outputs, and exported files. They focus on data production and
    persistence rather than computational operations.

    Attributes:
        id (str): Unique identifier for the asset node
        dependencies (list[str]): List of node IDs this node depends on
        config (BaseModel): Node configuration (when using @config_class)
        _node_type (ClassVar[str]): Set to "asset" by @asset_node decorator
        _output_schema (ClassVar[type[BaseModel]]): Set by @output_schema decorator
        _config_schema (ClassVar[type[BaseModel]]): Set by @config_class decorator
        _tags (ClassVar[dict[str, str]]): Set by @tag decorator
        _metadata (ClassVar[dict[str, Any]]): Set by @metadata decorator

    Note:
        Subclasses must:
        1. Use the @output_schema decorator to define their output structure
        2. Implement the execute() method to produce their data asset
    """

    def __init__(
        self, id: str, dependencies: Optional[Sequence[str]] = None, config_data: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Initialize an AssetNode.

        Args:
            id: Unique identifier for this node
            dependencies: Optional list of node IDs this node depends on
            config_data: Optional configuration data (validated against @config_class schema)

        Raises:
            ValueError: If required decorators (@output_schema) are not applied
            TypeError: If config_data doesn't match the @config_class schema
        """
        super().__init__(id=id, dependencies=dependencies)

        # Verify @output_schema was applied
        if not hasattr(self, "_output_schema"):
            raise ValueError(f"AssetNode subclass {self.__class__.__name__} must use @output_schema decorator")

        # Initialize config if @config_class was used
        if hasattr(self, "_config_schema") and config_data is not None:
            self.config = self._config_schema(**config_data)

    async def execute(self, context: NodeExecutionContext) -> dict[str, Any]:
        """
        Execute the node to produce its data asset.

        Args:
            context: Execution context containing input data and runtime information

        Returns:
            A dictionary containing the produced data asset, conforming to the
            schema defined by the @output_schema decorator

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError(f"AssetNode subclass {self.__class__.__name__} must implement execute()")

    def validate_inputs(self, context: NodeExecutionContext) -> None:
        """
        Validate inputs received from dependencies via the execution context.

        Args:
            context: Execution context containing input data

        Raises:
            ValueError: If required inputs are missing or invalid
        """
        # Validate presence of required dependencies
        for dep_id in self.dependencies:
            if not context.has_input(dep_id):
                raise ValueError(f"Missing required input from dependency '{dep_id}'")

        # If @input_schema was used, validate input data structure
        if hasattr(self, "_input_schema"):
            input_data = {dep_id: context.get_input(dep_id) for dep_id in self.dependencies}
            try:
                self._input_schema(**input_data)
            except Exception as e:
                raise ValueError(f"Input validation failed: {str(e)}")

    def should_execute(self, context: NodeExecutionContext) -> bool:
        """
        Determine if the node should execute based on the context.

        Args:
            context: Execution context containing runtime state

        Returns:
            True if the node should execute, False otherwise
        """
        # Base implementation always executes
        # Subclasses can override for conditional execution
        return True
