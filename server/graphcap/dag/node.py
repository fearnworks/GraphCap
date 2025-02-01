"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.node

Provides base node class for DAG operations.

Key features:
- Input/output type definitions
- Node configuration management
- Execution control
- Dependency tracking
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseNode(ABC):
    """
    Base class for all DAG nodes.

    Provides a framework for defining node behavior, inputs, outputs,
    and execution control. Similar in concept to workflow nodes but
    with a simplified interface focused on our needs.

    Attributes:
        id (str): Unique identifier for the node
        dependencies (List[str]): List of node IDs this node depends on
        config (Dict): Node configuration parameters
    """

    def __init__(self, id: str, dependencies: Optional[List[str]] = None):
        self.id = id
        self.dependencies = dependencies or []
        self.config = {}

    @classmethod
    @abstractmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """
        Define node schema including inputs and configuration.

        Returns:
            Dict with required and optional parameters
        """
        return {
            "required": {},  # Required parameters
            "optional": {},  # Optional parameters with defaults
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

    def validate_inputs(self, **kwargs) -> bool:
        """
        Validate input parameters against schema.

        Args:
            **kwargs: Input parameters to validate

        Returns:
            True if valid, raises ValueError if invalid
        """
        schema = self.schema()

        # Check required parameters
        for name, spec in schema.get("required", {}).items():
            if name not in kwargs:
                raise ValueError(f"Missing required parameter: {name}")
            # Could add type checking here if needed

        return True

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute node operation.

        Args:
            **kwargs: Input parameters from dependencies and config

        Returns:
            Dict mapping output names to values

        Raises:
            NotImplementedError: If node doesn't implement execution
        """
        raise NotImplementedError("Node must implement execute method")

    def should_execute(self, **kwargs) -> bool:
        """
        Check if node needs to execute.

        Args:
            **kwargs: Current input parameters

        Returns:
            True if node should execute
        """
        return True
