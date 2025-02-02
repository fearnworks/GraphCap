"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dag.nodes

Node implementations for DAG workflow.

Key features:
- Node registration
- Base node types
- Meta nodes
"""

from .meta import DAGVisualizerNode

# Register available node types
NODE_TYPES = {
    "DAGVisualizerNode": DAGVisualizerNode,
}

__all__ = ["DAGVisualizerNode", "NODE_TYPES"]
