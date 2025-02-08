# SPDX-License-Identifier: Apache-2.0
"""
Graph Network Visualization

Provides functionality for generating network diagrams from graph captions
using networkx for visualization.
"""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import cast

import matplotlib.pyplot as plt
import networkx as nx
from loguru import logger
from matplotlib.figure import Figure

from .types import CaptionData


def generate_network_diagram(captions: Sequence[CaptionData], job_dir: Path) -> None:
    """
    Generate a network diagram from graph captions.

    Args:
        captions: List of caption data dictionaries.
        job_dir: Directory to write the diagram to.
    """
    # Create a network graph. Only parameterize the node type (str) because networkx stubs
    # expect a single type parameter.
    G: nx.Graph[str] = nx.Graph()

    # Process each caption to extract entities and weighted relationships.
    for caption in captions:
        try:
            entities: set[str] = set()
            relationships: list[tuple[str, str, float]] = []
            for tag in caption["parsed"]["tags_list"]:
                category = tag["category"]
                tag_value = str(tag["tag"])
                if category == "Entity":
                    entities.add(tag_value)
                elif category == "Relationship":
                    rel = tag_value.lower()
                    for entity in entities:
                        if entity.lower() in rel:
                            for other_entity in entities:
                                if other_entity != entity and other_entity.lower() in rel:
                                    try:
                                        confidence = float(tag["confidence"])
                                    except (TypeError, ValueError):
                                        confidence = 1.0
                                    relationships.append((entity, other_entity, confidence))
            G.add_nodes_from(list(entities))
            G.add_weighted_edges_from(relationships)
        except Exception as e:
            logger.error(f"Error processing caption for network diagram: {e}")

    if len(G.nodes) == 0:
        logger.warning("No nodes found for network diagram")
        return

    # Create a matplotlib figure.
    fig: Figure = plt.figure(figsize=(15, 10))

    # Compute node sizes based on degree.
    node_sizes: list[int] = [3000 * (1 + int(G.degree[node])) for node in G.nodes()]

    # Compute edge weights explicitly using the edge data.
    edge_weights: list[float] = []
    for _u, _v, data in G.edges(data=True):
        weight_val = data.get("weight", 1.0)
        if not isinstance(weight_val, (int, float)):
            weight_val = 1.0
        edge_weights.append(2.0 * float(weight_val))

    # Compute spring layout positions.
    pos = nx.spring_layout(G, k=1, iterations=50)
    pos = cast(dict[str, tuple[float, float]], pos)

    # Draw the network graph.
    nx.draw(
        G,
        pos=pos,
        node_color="lightblue",
        node_size=node_sizes,
        width=edge_weights,
        edge_color="gray",
        with_labels=True,
        font_size=10,
        font_weight="bold",
    )

    # Save the diagram image.
    diagram_file = job_dir / "network_diagram.png"
    plt.savefig(diagram_file, bbox_inches="tight", dpi=300)
    plt.close(fig)

    # Save graph data as JSON for potential reuse.
    graph_data = {
        "nodes": list(G.nodes()),
        "edges": [
            (
                u,
                v,
                {
                    "weight": float(data.get("weight", 1.0))
                    if isinstance(data.get("weight", 1.0), (int, float))
                    else 1.0
                },
            )
            for u, v, data in G.edges(data=True)
        ],
    }
    data_file = job_dir / "network_data.json"
    _ = data_file.write_text(json.dumps(graph_data, indent=2))
