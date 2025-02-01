"""
# SPDX-License-Identifier: Apache-2.0
graphcap.caption.nodes

Node implementations for image captioning.

Classes:
    PerspectiveNode: Node for running caption perspectives
"""

from .perspective import PerspectiveNode

# Register available node types
NODE_TYPES = {
    "PerspectiveNode": PerspectiveNode,
}

__all__ = ["PerspectiveNode", "NODE_TYPES"]
