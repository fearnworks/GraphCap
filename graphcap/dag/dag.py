"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.dag

Provides DAG implementation for workflow management.

Key features:
- DAG validation and execution
- Node dependency management
- Topological sorting
- Configuration loading
"""

import json
from typing import Any, Dict, List, Optional, Type

from loguru import logger

from .node import BaseNode
from .nodes.meta import DAGVisualizerNode


class DAG:
    """
    Directed Acyclic Graph implementation for workflow management.

    Attributes:
        nodes (Dict[str, BaseNode]): Dictionary of nodes in the DAG
    """

    def __init__(self, nodes: Optional[List[BaseNode]] = None):
        self.nodes: Dict[str, BaseNode] = {}
        if nodes:
            for node in nodes:
                self.add_node(node)

    def add_node(self, node: BaseNode) -> None:
        """Add a node to the DAG."""
        if node.id in self.nodes:
            raise ValueError(f"Node with id {node.id} already exists")
        self.nodes[node.id] = node

    def validate(self) -> bool:
        """
        Validate the DAG structure.

        Returns:
            bool: True if valid, raises ValueError if invalid
        """
        # Check dependencies exist
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    raise ValueError(f"Node '{node.id}' depends on undefined node '{dep}'")

        # Check for cycles
        visited = set()
        rec_stack = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for dep in self.nodes[node_id].dependencies:
                if dep not in visited:
                    if dfs(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    raise ValueError("Cycle detected in the DAG")

        return True

    def topological_sort(self) -> List[str]:
        """Return nodes in execution order."""
        in_degree = {node_id: 0 for node_id in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                in_degree[node.id] += 1

        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        sorted_order = []

        while queue:
            current = queue.pop(0)
            sorted_order.append(current)

            for node in self.nodes.values():
                if current in node.dependencies:
                    in_degree[node.id] -= 1
                    if in_degree[node.id] == 0:
                        queue.append(node.id)

        if len(sorted_order) != len(self.nodes):
            raise ValueError("Cycle detected, topological sort not possible")

        return sorted_order

    @classmethod
    def from_json(cls, json_data: str, node_classes: Dict[str, Type[BaseNode]]) -> "DAG":
        """
        Create DAG from JSON configuration.

        Args:
            json_data: JSON string defining the DAG
            node_classes: Dictionary mapping node type names to classes

        Returns:
            DAG: Constructed DAG instance
        """
        data = json.loads(json_data)
        nodes = []

        for item in data.get("nodes", []):
            if "type" not in item:
                raise ValueError(f"Node {item.get('id')} missing required 'type' field")

            node_type = item["type"]
            if node_type not in node_classes:
                raise ValueError(f"Unknown node type: {node_type}")

            node_class = node_classes[node_type]
            node = node_class(id=item["id"], dependencies=item.get("dependencies", []))

            # Store node configuration if provided
            if "config" in item:
                node.config = item["config"]

            nodes.append(node)

        return cls(nodes)

    async def execute(self, start_node: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the DAG starting from a specific node or all root nodes.

        Args:
            start_node: Optional node ID to start from. If None, executes from all roots.

        Returns:
            Dict mapping node IDs to their execution results

        Raises:
            ValueError: If start_node is invalid or DAG is invalid
        """
        # Validate DAG first
        self.validate()

        # Get execution order
        execution_order = self.topological_sort()
        if start_node:
            if start_node not in self.nodes:
                raise ValueError(f"Start node '{start_node}' not found in DAG")
            # Filter order to only include start_node and its descendants
            start_idx = execution_order.index(start_node)
            execution_order = execution_order[start_idx:]

        # Store results for each node
        results: Dict[str, Any] = {}

        # Execute nodes in order
        for node_id in execution_order:
            node = self.nodes[node_id]

            # Get input values from dependencies
            input_values = {}
            for dep_id in node.dependencies:
                if dep_id not in results:
                    raise ValueError(f"Dependency '{dep_id}' not executed before '{node_id}'")
                input_values.update(results[dep_id])

            # Add node configuration if available
            if hasattr(node, "config"):
                input_values.update(node.config)

            # Special handling for DAGVisualizerNode
            if isinstance(node, DAGVisualizerNode):
                input_values["dag"] = self

            # Execute node
            logger.info(f"Executing node: {node_id}")
            try:
                result = await node.execute(**input_values)
                results[node_id] = result
                logger.info(f"Node {node_id} completed successfully")
            except Exception as e:
                logger.error(f"Node {node_id} failed: {str(e)}")
                raise

        return results

    @classmethod
    def validate_config(cls, config_path: str, node_classes: Dict[str, Type[BaseNode]]) -> "DAG":
        """
        Validate a DAG configuration file and return the constructed DAG.

        Args:
            config_path: Path to the JSON configuration file
            node_classes: Dictionary mapping node type names to classes

        Returns:
            Validated DAG instance

        Raises:
            ValueError: If configuration is invalid
        """
        try:
            with open(config_path) as f:
                json_data = f.read()

            dag = cls.from_json(json_data, node_classes)
            if dag.validate():
                logger.info("DAG configuration is valid")

                # Show execution order
                order = dag.topological_sort()
                logger.info("Execution order:")
                for i, node_id in enumerate(order, 1):
                    logger.info(f"{i}. {node_id}")

            return dag

        except Exception as e:
            raise ValueError(f"DAG validation failed: {str(e)}")

    @classmethod
    def from_dict(cls, config: Dict[str, Any], node_classes: Dict[str, str]) -> "DAG":
        """
        Create a DAG instance from a dictionary configuration.

        Args:
            config: Dictionary containing DAG configuration
            node_classes: Mapping of node type names to class paths

        Returns:
            DAG instance

        Raises:
            ValueError: If configuration is invalid
        """
        # Create DAG instance
        dag = cls()

        # Import and instantiate node classes
        for node_config in config["nodes"]:
            node_type = node_config["type"]
            if node_type not in node_classes:
                raise ValueError(f"Unknown node type: {node_type}")

            # Import node class
            module_path, class_name = node_classes[node_type].rsplit(".", 1)
            module = __import__(module_path, fromlist=[class_name])
            node_class = getattr(module, class_name)

            # Create node instance
            node = node_class(id=node_config["id"], dependencies=node_config.get("dependencies", []))
            dag.add_node(node)

        return dag
