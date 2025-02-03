"""
# SPDX-License-Identifier: Apache-2.0
DAG (Directed Acyclic Graph) Package

Provides a flexible framework for building and executing directed acyclic graphs
for image processing and analysis pipelines.

Key features:
- DAG construction and validation
- Node dependency management
- Asynchronous execution
- Built-in visualization
- Extensible node system

Components:
    DAG: Main DAG implementation for workflow management
    BaseNode: Base class for all DAG nodes
    DAGVisualizerNode: Node for generating DAG visualizations

Example:
    ```python
    from graphcap.dag import DAG, BaseNode

    # Create nodes
    nodes = [
        MyProcessingNode(id="process1"),
        MyOutputNode(id="output1", dependencies=["process1"])
    ]

    # Create and validate DAG
    dag = DAG(nodes=nodes)
    dag.validate()

    # Execute workflow
    results = await dag.execute()
    ```
"""

from .dag import DAG
from .node import BaseNode
from .nodes.meta import DAGVisualizerNode
from .nodes.visualizer import DAGVisualizerNode as LegacyVisualizerNode

# Register available node types
NODE_TYPES = {
    "DAGVisualizerNode": DAGVisualizerNode,
    "LegacyVisualizerNode": LegacyVisualizerNode,
}

__all__ = [
    "DAG",
    "BaseNode",
    "DAGVisualizerNode",
    "NODE_TYPES",
]
