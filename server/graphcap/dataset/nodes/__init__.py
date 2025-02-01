"""
# SPDX-License-Identifier: Apache-2.0
graphcap.dataset.nodes

Node implementations for dataset operations.

Classes:
    DatasetExportNode: Node for exporting results to dataset format
"""

from .export import DatasetExportNode

# Register available node types
NODE_TYPES = {
    "DatasetExportNode": DatasetExportNode,
}

__all__ = ["DatasetExportNode", "NODE_TYPES"]
