"""
# SPDX-License-Identifier: Apache-2.0
graphcap.io.nodes

Collection of IO-related DAG nodes.

Nodes:
    ImageSamplingNode: Image loading and sampling functionality
    CopyImagesNode: Batch image copying functionality
"""

from .copy_images import CopyImagesNode
from .image_sampling import ImageSamplingNode

# Register available node types
NODE_TYPES = {
    "ImageSamplingNode": ImageSamplingNode,
    "CopyImagesNode": CopyImagesNode,
}

__all__ = ["ImageSamplingNode", "CopyImagesNode", "NODE_TYPES"]
