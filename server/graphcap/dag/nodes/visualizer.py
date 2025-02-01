"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.nodes.visualizer

Node for visualizing DAG structure using NetworkX.

Key features:
- Topological layout generation
- Layer-based node positioning
- Customizable styling
"""

from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import networkx as nx

from ...dag.node import BaseNode


class DAGVisualizerNode(BaseNode):
    """Node for generating DAG visualizations."""

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute DAG visualization."""
        self.validate_inputs(**kwargs)

        # Get DAG structure from context
        dag = self.context.dag
        G = nx.DiGraph(dag.edges)

        # Assign layers based on topological generations
        for layer, nodes in enumerate(nx.topological_generations(G)):
            for node in nodes:
                G.nodes[node]["layer"] = layer

        # Create figure
        fig, ax = plt.subplots(figsize=(kwargs["style"].get("width", 12), kwargs["style"].get("height", 8)))

        # Get node positions using multipartite layout
        pos = nx.multipartite_layout(G, subset_key="layer")

        # Draw the graph
        nx.draw_networkx(
            G,
            pos=pos,
            ax=ax,
            node_color=kwargs["style"].get("node_color", "#E6F3FF"),
            node_size=kwargs["style"].get("node_size", 3000),
            edge_color=kwargs["style"].get("edge_color", "#666666"),
            font_size=kwargs["style"].get("font_size", 12),
            node_shape=kwargs["style"].get("node_shape", "s"),
            arrows=kwargs["style"].get("arrows", True),
            arrowsize=kwargs["style"].get("arrowsize", 20),
            with_labels=kwargs["style"].get("with_labels", True),
        )

        # Add node type labels below nodes
        node_types = {node_id: data.get("type", "") for node_id, data in dag.nodes.items()}
        pos_attrs = {}
        for node, coords in pos.items():
            pos_attrs[node] = (coords[0], coords[1] - 0.08)  # Offset for type labels
        nx.draw_networkx_labels(G, pos_attrs, node_types, font_size=8)

        # Set title and adjust layout
        ax.set_title("DAG Structure - Topological Layout")
        fig.tight_layout()

        # Save the visualization
        output_dir = Path(kwargs["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "dag_viz_latest.png"
        plt.savefig(output_path, bbox_inches="tight", dpi=300)
        plt.close()

        return {
            "visualization": {
                "path": str(output_path),
                "format": kwargs.get("format", "png"),
                "layout": "topological",
                "node_count": len(G.nodes),
                "edge_count": len(G.edges),
            }
        }
