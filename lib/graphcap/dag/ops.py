"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.ops

Provides the base OpNode class for representing computational operations in the graphcap DAG system.

Key features:
- Base class for computational operation nodes
- Optional output schema validation
- Flexible input handling
- Integration with DAG execution context

Classes:
    OpNode: Base class for nodes that perform computational operations
"""

from typing import Any, Optional, Sequence

from .decorators import op_node
from .node import BaseNode, NodeExecutionContext


@op_node
class OpNode(BaseNode):
    """
    Base class for nodes that perform computational operations in the graphcap pipeline.

    OpNodes represent computational steps like image processing, data transformation,
    analysis, or visualization. They focus on computation and logic rather than
    data persistence.

    Attributes:
        id (str): Unique identifier for the op node
        dependencies (list[str]): List of node IDs this node depends on
        config (BaseModel): Node configuration (when using @config_class)
        _node_type (ClassVar[str]): Set to "op" by @op_node decorator
        _output_schema (ClassVar[type[BaseModel]] | None): Set by @output_schema decorator
        _config_schema (ClassVar[type[BaseModel]] | None): Set by @config_class decorator
        _tags (ClassVar[dict[str, str]]): Set by @tag decorator
        _metadata (ClassVar[dict[str, Any]]): Set by @metadata decorator

    Note:
        Subclasses must:
        1. Implement the execute() method to perform their computation
        2. Optionally use @output_schema if they produce structured output data
    """

    def __init__(
        self, id: str, dependencies: Optional[Sequence[str]] = None, config_data: Optional[dict[str, Any]] = None
    ) -> None:
        """
        Initialize an OpNode.

        Args:
            id: Unique identifier for this node
            dependencies: Optional list of node IDs this node depends on
            config_data: Optional configuration data (validated against @config_class schema)

        Raises:
            TypeError: If config_data doesn't match the @config_class schema
        """
        super().__init__(id=id, dependencies=dependencies)

        # Initialize config if @config_class was used
        if hasattr(self, "_config_schema") and config_data is not None:
            self.config = self._config_schema(**config_data)

    async def execute(self, context: NodeExecutionContext) -> dict[str, Any]:
        """
        Execute the node to perform its computation.

        Args:
            context: Execution context containing input data and runtime information

        Returns:
            A dictionary containing any output data. If @output_schema is used,
            the output must conform to that schema. Otherwise, can return an
            empty dict or minimal output data.

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError(f"OpNode subclass {self.__class__.__name__} must implement execute()")

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

    def validate_outputs(self, output_data: dict[str, Any]) -> None:
        """
        Validate output data against the output schema if one is defined.

        Args:
            output_data: The data to validate

        Raises:
            ValueError: If output validation fails
        """
        if hasattr(self, "_output_schema"):
            try:
                self._output_schema(**output_data)
            except Exception as e:
                raise ValueError(f"Output validation failed: {str(e)}")

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
