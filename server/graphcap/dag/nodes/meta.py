"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.nodes.meta

Meta nodes for DAG visualization and analysis.

Key features:
- DAG visualization
- Dependency analysis
- Graph metrics
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import networkx as nx
from loguru import logger

from ..node import BaseNode


class DAGVisualizerNode(BaseNode):
    """
    Node for visualizing DAG structure and dependencies.

    Creates network diagrams of the DAG using networkx and matplotlib.
    Supports multiple layout algorithms and styling options.
    """

    def __init__(self, id: str, dependencies: Optional[List[str]] = None):
        super().__init__(id, dependencies)

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "dag": {
                    "type": "DAG",
                    "description": "DAG instance to visualize",
                },
                "output_dir": {
                    "type": "STRING",
                    "description": "Directory to save visualization",
                    "default": "./dag_viz",
                },
            },
            "optional": {
                "layout": {
                    "type": "STRING",
                    "description": "Graph layout algorithm",
                    "default": "spring",
                    "choices": ["spring", "circular", "kamada_kawai", "planar"],
                },
                "format": {
                    "type": "STRING",
                    "description": "Output file format",
                    "default": "png",
                    "choices": ["png", "pdf", "svg"],
                },
                "style": {
                    "type": "DICT",
                    "description": "Visualization style options",
                    "default": {
                        "node_size": 2000,
                        "node_color": "lightblue",
                        "edge_color": "gray",
                        "font_size": 10,
                        "width": 12,
                        "height": 8,
                    },
                },
            },
        }

    @classmethod
    def outputs(cls) -> Dict[str, Any]:
        """Define node outputs."""
        return {
            "visualization": {
                "type": "DICT",
                "description": "Visualization metadata and paths",
            }
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the visualization node.

        Args:
            **kwargs: Node parameters including DAG and style options

        Returns:
            Dict containing visualization metadata and paths
        """
        self.validate_inputs(**kwargs)

        dag = kwargs["dag"]
        output_dir = Path(kwargs.get("output_dir", "./dag_viz"))
        layout = kwargs.get("layout", "spring")
        fmt = kwargs.get("format", "png")
        style = kwargs.get("style", {})

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create networkx graph
        G = nx.DiGraph()

        # Add nodes and edges
        for node_id, node in dag.nodes.items():
            G.add_node(node_id, type=node.__class__.__name__)
            for dep in node.dependencies:
                G.add_edge(dep, node_id)

        # Set up plot
        plt.figure(figsize=(style.get("width", 12), style.get("height", 8)))

        # Get layout
        if layout == "spring":
            pos = nx.spring_layout(G)
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        elif layout == "planar":
            pos = nx.planar_layout(G)
        else:
            pos = nx.spring_layout(G)

        # Draw graph
        nx.draw(
            G,
            pos,
            node_color=style.get("node_color", "lightblue"),
            node_size=style.get("node_size", 2000),
            edge_color=style.get("edge_color", "gray"),
            with_labels=True,
            font_size=style.get("font_size", 10),
            arrows=True,
        )

        # Add node type labels
        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] - 0.08)
        node_types = nx.get_node_attributes(G, "type")
        nx.draw_networkx_labels(G, pos_attrs, node_types, font_size=8)

        # Save visualization
        timestamp = kwargs.get("timestamp", "latest")
        output_path = output_dir / f"dag_viz_{timestamp}.{fmt}"
        plt.savefig(output_path, format=fmt, bbox_inches="tight")
        plt.close()

        logger.info(f"DAG visualization saved to {output_path}")

        return {
            "visualization": {
                "path": str(output_path),
                "format": fmt,
                "layout": layout,
                "node_count": len(G.nodes),
                "edge_count": len(G.edges),
            }
        }
