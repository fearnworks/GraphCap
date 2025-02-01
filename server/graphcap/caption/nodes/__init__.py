"""
# SPDX-License-Identifier: Apache-2.0
graphcap.caption.nodes

Node implementations for image captioning.

Classes:
    PerspectiveNode: Node for running caption perspectives
    PerspectiveOutputNode: Node for managing perspective outputs
"""

from .output import PerspectiveOutputNode
from .perspective import PerspectiveNode

# Register available node types
NODE_TYPES = {
    "PerspectiveNode": PerspectiveNode,
    "PerspectiveOutputNode": PerspectiveOutputNode,
}

__all__ = ["PerspectiveNode", "PerspectiveOutputNode", "NODE_TYPES"]
