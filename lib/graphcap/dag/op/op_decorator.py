# graphcap/dag/decorators.py
# Note: placing op_decorator implementation in decorators.py as per the existing structure.
# If a separate file is needed, move this code to graphcap/dag/op_decorator.py

"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.op.op_decorator

Provides decorators for node type definition, schema enforcement, and metadata handling.

Includes:
    - @op_node: Decorator to mark a class as an Op Node.
"""

from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from .node import BaseNode

T = TypeVar("T", bound=BaseNode)


def op_node(
    name: Optional[str] = None,  
    description: Optional[str] = None 
) -> Callable[[type[T]], type[T]]:
    """
    Marks a node class as an operation node, representing computational steps.

    Args:
        name (Optional[str]):  Optional name for the op node. If None, the class name will be used.
        description (Optional[str]): Optional description for the op node.

    Returns:
        A decorator function that applies the op node type and optional metadata to a node class.

    Raises:
        TypeError: If the decorated class does not inherit from BaseNode.
    """
    def decorator(node_class: type[T]) -> type[T]:
        if not issubclass(node_class, BaseNode):
            raise TypeError("@op_node can only be applied to BaseNode subclasses")

        node_class._node_type = "op"

        if name:
            node_class._op_name_override = name # Store name override if provided
        if description:
            node_class._op_description_override = description # Store description override if provided

        return node_class

    return decorator