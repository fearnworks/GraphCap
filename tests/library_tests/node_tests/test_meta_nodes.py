"""
# SPDX-License-Identifier: Apache-2.0
graphcap.tests.lib.node_tests.test_meta_nodes

Tests for DAG meta nodes functionality.

Key features:
- DAG visualization generation
- Output format handling
- Layout algorithm testing
- Node and edge visualization
- Graph metadata validation

Classes:
    None (contains test functions only)
"""

from pathlib import Path

import pytest
from graphcap.dag.dag import DAG
from graphcap.dag.nodes.meta import DAGVisualizerNode


@pytest.fixture
def test_dag():
    """Create a test DAG with multiple nodes."""
    dag = DAG()

    # Add some test nodes
    node1 = DAGVisualizerNode(id="node1")
    node2 = DAGVisualizerNode(id="node2", dependencies=["node1"])
    node3 = DAGVisualizerNode(id="node3", dependencies=["node1"])
    node4 = DAGVisualizerNode(id="node4", dependencies=["node2", "node3"])

    dag.add_node(node1)
    dag.add_node(node2)
    dag.add_node(node3)
    dag.add_node(node4)

    return dag


@pytest.mark.asyncio
async def test_dag_visualizer(test_dag, tmp_path):
    """Test DAG visualization node."""
    # Create visualizer node
    viz_node = DAGVisualizerNode(id="viz")

    # Execute visualization
    result = await viz_node.execute(
        dag=test_dag,
        output_dir=str(tmp_path),
        layout="spring",
        format="png",
        style={
            "node_size": 1500,
            "node_color": "lightgreen",
            "edge_color": "darkgray",
            "font_size": 12,
        },
        timestamp="test",
    )

    # Check results
    assert "visualization" in result
    viz_info = result["visualization"]

    # Verify output file
    output_path = Path(viz_info["path"])
    assert output_path.exists()
    assert output_path.suffix == ".png"

    # Check metadata
    assert viz_info["format"] == "png"
    assert viz_info["node_count"] == 4
    assert viz_info["edge_count"] == 4


@pytest.mark.asyncio
async def test_dag_visualizer_formats(test_dag, tmp_path):
    """Test different output formats."""
    viz_node = DAGVisualizerNode(id="viz")

    for fmt in ["png", "pdf", "svg"]:
        result = await viz_node.execute(
            dag=test_dag,
            output_dir=str(tmp_path),
            format=fmt,
            timestamp=f"test_{fmt}",
        )

        output_path = Path(result["visualization"]["path"])
        assert output_path.exists()
        assert output_path.suffix == f".{fmt}"


@pytest.mark.asyncio
async def test_dag_visualizer_layouts(test_dag, tmp_path):
    """Test different layout algorithms."""
    viz_node = DAGVisualizerNode(id="viz")

    for layout in ["spring", "circular", "kamada_kawai", "planar"]:
        result = await viz_node.execute(
            dag=test_dag,
            output_dir=str(tmp_path),
            layout=layout,
            format="png",
            timestamp=f"test_{layout}",
        )

        assert "visualization" in result
        viz_info = result["visualization"]
        assert viz_info["format"] == "png"
        assert viz_info["node_count"] == 4
        assert viz_info["edge_count"] == 4

        output_path = Path(viz_info["path"])
        assert output_path.exists()
