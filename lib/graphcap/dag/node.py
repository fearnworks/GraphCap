"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.node

Provides the base node classes and execution context for the graphcap DAG system.

Key features:
- Base node class definition
- Execution context management
- Input/output validation
- Node lifecycle management

Classes:
    NodeExecutionContext: Execution context for node operations
    BaseNode: Abstract base class for all DAG nodes
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Sequence

from loguru import logger


class NodeExecutionContext:
    """
    Execution context for node operations in the graphcap DAG system.

    Provides structured access to input data from dependencies and standardized
    logging during node execution.

    Attributes:
        node_id (str): Unique identifier of the executing node
        _dag_results (dict[str, Any]): Results from upstream dependencies
    """

    def __init__(self, node_id: str, dag_results: dict[str, Any]) -> None:
        """
        Initialize a NodeExecutionContext.

        Args:
            node_id: Unique identifier of the executing node
            dag_results: Dictionary of results from upstream dependencies
        """
        self.node_id = node_id
        self._dag_results = dag_results

    def get_input(self, dependency_id: str) -> Any:
        """
        Safely retrieve output data from a dependency node.

        Args:
            dependency_id: ID of the dependency node

        Returns:
            The output data produced by the dependency node

        Raises:
            ValueError: If dependency_id is not found in available results
        """
        if dependency_id not in self._dag_results:
            raise ValueError(f"Node [{self.node_id}]: Missing required input from dependency '{dependency_id}'")
        return self._dag_results[dependency_id]

    def has_input(self, dependency_id: str) -> bool:
        """
        Check if input data from a dependency is available.

        Args:
            dependency_id: ID of the dependency node

        Returns:
            True if the dependency's output is available, False otherwise
        """
        return dependency_id in self._dag_results

    def log_info(self, message: str) -> None:
        """
        Log an info message with node context.

        Args:
            message: The message to log
        """
        logger.info(f"Node [{self.node_id}]: {message}")

    def log_warning(self, message: str) -> None:
        """
        Log a warning message with node context.

        Args:
            message: The warning message to log
        """
        logger.warning(f"Node [{self.node_id}]: {message}")

    def log_error(self, message: str) -> None:
        """
        Log an error message with node context.

        Args:
            message: The error message to log
        """
        logger.error(f"Node [{self.node_id}]: {message}")


class BaseNode(ABC):
    """
    Abstract base class for all nodes in the graphcap DAG system.

    Provides core functionality for node identification, dependency management,
    and execution lifecycle.

    Attributes:
        id (str): Unique identifier for the node
        dependencies (list[str]): List of node IDs this node depends on
    """

    def __init__(self, id: str, dependencies: Optional[Sequence[str]] = None) -> None:
        """
        Initialize a BaseNode.

        Args:
            id: Unique identifier for this node
            dependencies: Optional list of node IDs this node depends on
        """
        self.id = id
        self.dependencies = list(dependencies) if dependencies is not None else []

    @classmethod
    @abstractmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get the node's schema information.

        Returns:
            A dictionary containing the node's schema definition
        """
        # Base implementation returns minimal schema
        # Subclasses and decorators can extend this
        return {
            "type": "node",
            "id": {"type": "string", "description": "Unique identifier for the node"},
            "dependencies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of node IDs this node depends on",
            },
        }

    @property
    @abstractmethod
    def outputs(self) -> Dict[str, str]:
        """
        Define node output schema.

        Returns:
            Dict mapping output names to their types
        """
        return {}

    @property
    def is_output(self) -> bool:
        """Whether this node produces final output."""
        return False

    @property
    def category(self) -> str:
        """Node category for organization."""
        return "Default"

    @property
    def version(self) -> str:
        """Node implementation version."""
        return "1.0"

    def validate_inputs(self, context: NodeExecutionContext) -> None:
        """
        Validate inputs received from dependencies via the execution context.

        Args:
            context: Execution context containing input data

        Raises:
            ValueError: If required inputs are missing or invalid
        """
        # Base implementation just checks for presence of required dependencies
        for dep_id in self.dependencies:
            if not context.has_input(dep_id):
                raise ValueError(f"Missing required input from dependency '{dep_id}'")

    async def execute(self, context: NodeExecutionContext) -> Dict[str, Any]:
        """
        Execute the node's operation.

        Args:
            context: Execution context containing input data and runtime information

        Returns:
            A dictionary containing the node's output data

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError(f"BaseNode subclass {self.__class__.__name__} must implement execute()")

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
