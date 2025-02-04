# from graphcap.caption.graph_caption import GraphCaptionProcessor
from graphcap.caption.nodes import PerspectiveNode, PerspectiveOutputNode
from graphcap.dag.nodes import DAGVisualizerNode
from graphcap.dataset.nodes import DatasetExportNode

from .io import ImageSamplingNode

# Add this dictionary to map node types to their classes
NODE_CLASS_MAPPINGS = {
    "ImageSamplingNode": ImageSamplingNode,
    "PerspectiveNode": PerspectiveNode,
    "PerspectiveOutputNode": PerspectiveOutputNode,
    "DAGVisualizerNode": DAGVisualizerNode,
    "DatasetExportNode": DatasetExportNode,
}
