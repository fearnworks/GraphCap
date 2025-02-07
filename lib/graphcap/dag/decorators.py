"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.decorators

Provides decorators for node type definition, schema enforcement, and metadata handling.

Key features:
- Node type definition (@asset_node, @op_node)
- Schema validation (@input_schema, @output_schema)
- Configuration management (@config_class)
- Metadata handling (@tag, @metadata)
"""

from typing import Any, Callable, TypeVar

from pydantic import BaseModel

from .node import BaseNode

T = TypeVar("T", bound=BaseNode)


def asset_node(node_class: type[T]) -> type[T]:
    """
    Marks a node class as an asset node, representing data assets in the pipeline.

    Args:
        node_class: A class inheriting from BaseNode

    Returns:
        The decorated node class

    Raises:
        TypeError: If node_class does not inherit from BaseNode
    """
    if not issubclass(node_class, BaseNode):
        raise TypeError("@asset_node can only be applied to BaseNode subclasses")

    node_class._node_type = "asset"
    return node_class


def op_node(node_class: type[T]) -> type[T]:
    """
    Marks a node class as an operation node, representing computational steps.

    Args:
        node_class: A class inheriting from BaseNode

    Returns:
        The decorated node class

    Raises:
        TypeError: If node_class does not inherit from BaseNode
    """
    if not issubclass(node_class, BaseNode):
        raise TypeError("@op_node can only be applied to BaseNode subclasses")

    node_class._node_type = "op"
    return node_class


def input_schema(schema_cls: type[BaseModel]) -> Callable[[type[T]], type[T]]:
    """
    Defines the input schema for a node using a Pydantic model.

    Args:
        schema_cls: A Pydantic model class defining the input schema

    Returns:
        A decorator function that applies the schema to a node class
    """

    def decorator(node_class: type[T]) -> type[T]:
        if not issubclass(node_class, BaseNode):
            raise TypeError("@input_schema can only be applied to BaseNode subclasses")

        node_class._input_schema = schema_cls
        return node_class

    return decorator


def output_schema(schema_cls: type[BaseModel]) -> Callable[[type[T]], type[T]]:
    """
    Defines the output schema for a node using a Pydantic model.

    Args:
        schema_cls: A Pydantic model class defining the output schema

    Returns:
        A decorator function that applies the schema to a node class
    """

    def decorator(node_class: type[T]) -> type[T]:
        if not issubclass(node_class, BaseNode):
            raise TypeError("@output_schema can only be applied to BaseNode subclasses")

        node_class._output_schema = schema_cls
        # Add outputs property that returns schema
        node_class.outputs = property(lambda _: schema_cls.schema())
        return node_class

    return decorator


def config_class(config_cls: type[BaseModel]) -> Callable[[type[T]], type[T]]:
    """
    Associates a Pydantic configuration model with a node class.

    Args:
        config_cls: A Pydantic model class defining the node configuration

    Returns:
        A decorator function that applies the config to a node class
    """

    def decorator(node_class: type[T]) -> type[T]:
        if not issubclass(node_class, BaseNode):
            raise TypeError("@config_class can only be applied to BaseNode subclasses")

        node_class._config_schema = config_cls
        # Store original schema method
        original_schema = node_class.schema

        @classmethod
        def new_schema(cls):
            base_schema = original_schema()
            config_schema = config_cls.schema()
            # Merge schemas under optional.config
            if "optional" not in base_schema:
                base_schema["optional"] = {}
            base_schema["optional"]["config"] = config_schema
            return base_schema

        node_class.schema = new_schema
        return node_class

    return decorator


def tag(**tags: str) -> Callable[[type[T]], type[T]]:
    """
    Adds tags to a node class for categorization and filtering.

    Args:
        **tags: Keyword arguments defining tags and their values

    Returns:
        A decorator function that applies tags to a node class
    """

    def decorator(node_class: type[T]) -> type[T]:
        if not issubclass(node_class, BaseNode):
            raise TypeError("@tag can only be applied to BaseNode subclasses")

        if not hasattr(node_class, "_tags"):
            node_class._tags = {}
        node_class._tags.update(tags)

        # Add tags property
        node_class.tags = property(lambda _: node_class._tags)
        return node_class

    return decorator


def metadata(**metadata: Any) -> Callable[[type[T]], type[T]]:
    """
    Adds metadata to a node class for additional information.

    Args:
        **metadata: Keyword arguments defining metadata keys and values

    Returns:
        A decorator function that applies metadata to a node class
    """

    def decorator(node_class: type[T]) -> type[T]:
        if not issubclass(node_class, BaseNode):
            raise TypeError("@metadata can only be applied to BaseNode subclasses")

        if not hasattr(node_class, "_metadata"):
            node_class._metadata = {}
        node_class._metadata.update(metadata)

        # Add node_metadata property
        node_class.node_metadata = property(lambda _: node_class._metadata)
        return node_class

    return decorator
