# graphcap/dag/op_definition.py
# Note: Simplified OpDefinition for graphcap, inspired by Dagster's OpDefinition
# but without Dagster dependencies and focusing on core concepts for graphcap MVP.

from typing import Any, Callable, Optional


class OpDefinition:
    """
    Defines a computational operation (Op) in graphcap.

    This class is a simplified representation of a Dagster OpDefinition,
    tailored for graphcap's needs. It represents a single computational step
    within a graphcap pipeline.

    In graphcap, the actual computation logic is typically implemented within
    the `execute` method of an `OpNode` class, rather than directly within
    an OpDefinition instance.  This class primarily serves as a conceptual
    representation of an operation.
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        compute_fn: Optional[Callable[..., Any]] = None,  
    ):
        """
        Args:
            name (str): Name of the op. Must be unique within any graphcap DAG.
            description (Optional[str]): Human-readable description of the op.
            compute_fn (Optional[Callable[..., Any]]): Placeholder for the compute function.
                In graphcap MVP, the computation logic is within OpNode.execute, not directly here.
        """
        self._name = check_str_param(name, "name")
        self._description = check_opt_str_param(description, "description")
        self._compute_fn = check.opt_callable_param(compute_fn, "compute_fn")  # Placeholder

    @property
    def name(self) -> str:
        """str: The name of this op."""
        return self._name

    @property
    def description(self) -> Optional[str]:
        """Optional[str]: Human-readable description of the op."""
        return self._description

    @property
    def compute_fn(self) -> Optional[Callable[..., Any]]:
        """Optional[Callable[..., Any]]: Placeholder for the compute function."""
        return self._compute_fn

    @property
    def node_type_str(self) -> str:
        """str: String representation of the node type."""
        return "op"  # Indicate it's an "op" type


def check_str_param(val: str, param_name: str) -> str:
    if not isinstance(val, str):
        raise TypeError(f"Param '{param_name}' must be a string, got {type(val).__name__}")
    return val


def check_opt_str_param(val: Optional[str], param_name: str) -> Optional[str]:
    if val is not None and not isinstance(val, str):
        raise TypeError(f"Optional param '{param_name}' must be a string or None, got {type(val).__name__}")
    return val


def check_opt_callable_param(val: Optional[Callable[..., Any]], param_name: str) -> Optional[Callable[..., Any]]:
    if val is not None and not callable(val):
        raise TypeError(f"Optional param '{param_name}' must be a Callable or None, got {type(val).__name__}")
    return val
