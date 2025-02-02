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
import networkx as nx
from loguru import logger

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt

from ..node import BaseNode


class DAGVisualizerNode(BaseNode):
    """Node for visualizing DAG structure and dependencies."""

    def __init__(self, id: str, dependencies: Optional[List[str]] = None):
        super().__init__(id, dependencies)

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node schema."""
        return {
            "required": {
                "dag": {"type": "DAG", "description": "DAG instance to visualize"},
                "output_dir": {"type": "STRING", "description": "Output directory", "default": "./dag_viz"},
            },
            "optional": {
                "format": {
                    "type": "STRING",
                    "description": "Output format",
                    "default": "png",
                    "choices": ["png", "pdf", "svg"],
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
        """Execute the visualization node."""
        self.validate_inputs(**kwargs)

        dag = kwargs["dag"]
        output_dir = Path(kwargs.get("output_dir", "./dag_viz"))
        fmt = kwargs.get("format", "png")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create and configure graph
        G = nx.DiGraph()
        for node_id, node in dag.nodes.items():
            G.add_node(node_id, type=node.__class__.__name__)
            for dep in node.dependencies:
                G.add_edge(dep, node_id)

        # Set up plot with reasonable defaults
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=1, iterations=50)  # k=1 spreads nodes more

        # Draw the graph
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="#E6F3FF",
            node_size=3000,
            font_size=10,
            font_weight="bold",
            arrows=True,
            edge_color="#666666",
            width=2,
            arrowsize=20,
        )

        # Add node type labels
        pos_attrs = {node: (coords[0], coords[1] - 0.08) for node, coords in pos.items()}
        nx.draw_networkx_labels(
            G,
            pos_attrs,
            nx.get_node_attributes(G, "type"),
            font_size=8,
            font_color="#666666",
        )

        # Save visualization
        output_path = output_dir / f"dag_viz_{kwargs.get('timestamp', 'latest')}.{fmt}"
        plt.savefig(output_path, format=fmt, bbox_inches="tight", dpi=300)
        plt.close()

        logger.info(f"DAG visualization saved to {output_path}")
        return {
            "visualization": {
                "path": str(output_path),
                "format": fmt,
                "node_count": len(G.nodes),
                "edge_count": len(G.edges),
            }
        }
