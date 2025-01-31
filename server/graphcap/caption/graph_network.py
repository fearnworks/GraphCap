"""
# SPDX-License-Identifier: Apache-2.0
Graph Network Visualization Module

Provides functionality for generating network diagrams from graph captions
using networkx for visualization.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import networkx as nx
from loguru import logger


def generate_network_diagram(captions: List[Dict[str, Any]], job_dir: Path) -> None:
    """
    Generate a network diagram from graph captions.

    Args:
        captions: List of caption data dictionaries
        job_dir: Directory to write the diagram to
    """
    # Create network graph
    G = nx.Graph()

    # Process each caption
    for caption in captions:
        try:
            # Extract entities and relationships from tags
            entities = set()
            relationships = []

            for tag in caption["parsed"]["tags_list"]:
                if tag["category"] == "Entity":
                    entities.add(tag["tag"])
                elif tag["category"] == "Relationship":
                    # Try to extract relationship components
                    rel = tag["tag"].lower()
                    for entity in entities:
                        if entity.lower() in rel:
                            # Found a relationship involving this entity
                            for other_entity in entities:
                                if other_entity != entity and other_entity.lower() in rel:
                                    relationships.append((entity, other_entity, tag["confidence"]))

            # Add nodes and edges to graph
            for entity in entities:
                if not G.has_node(entity):
                    G.add_node(entity)

            for src, dst, weight in relationships:
                G.add_edge(src, dst, weight=weight)

        except Exception as e:
            logger.error(f"Error processing caption for network diagram: {e}")

    # Create visualization
    plt.figure(figsize=(15, 10))

    # Calculate node sizes based on degree
    node_sizes = [3000 * (1 + G.degree(node)) for node in G.nodes()]

    # Calculate edge weights for thickness
    edge_weights = [G[u][v]["weight"] * 2 for u, v in G.edges()]

    # Spring layout with more space
    pos = nx.spring_layout(G, k=1, iterations=50)

    # Draw network
    nx.draw(
        G,
        pos,
        node_color="lightblue",
        node_size=node_sizes,
        width=edge_weights,
        edge_color="gray",
        with_labels=True,
        font_size=10,
        font_weight="bold",
    )

    # Save diagram
    diagram_file = job_dir / "network_diagram.png"
    plt.savefig(diagram_file, bbox_inches="tight", dpi=300)
    plt.close()

    # Save graph data as JSON for potential reuse
    graph_data = {"nodes": list(G.nodes()), "edges": [(u, v, d) for u, v, d in G.edges(data=True)]}
    data_file = job_dir / "network_data.json"
    data_file.write_text(json.dumps(graph_data, indent=2))
