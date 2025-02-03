"""
# SPDX-License-Identifier: Apache-2.0
graphcap.io.nodes

Collection of IO-related DAG nodes.

Nodes:
    ImageSamplingNode: Image loading and sampling functionality
"""

from .image_sampling import ImageSamplingNode

# Register available node types
NODE_TYPES = {
    "ImageSamplingNode": ImageSamplingNode,
}

__all__ = ["ImageSamplingNode", "NODE_TYPES"]
