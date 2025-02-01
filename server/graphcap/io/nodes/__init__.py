"""
# SPDX-License-Identifier: Apache-2.0
graphcap.io.nodes

Collection of IO-related DAG nodes.

Nodes:
    ImageSamplingNode: Image loading and sampling functionality
"""

from .image_sampling import ImageSamplingNode

__all__ = ["ImageSamplingNode"]
