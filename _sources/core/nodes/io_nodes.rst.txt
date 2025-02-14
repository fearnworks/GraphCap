=======================
IO Nodes
=======================

Overview
========
IO Nodes in graphcap handle file and data input/output operations. They provide functionality for loading, sampling, and copying images as well as managing file system interactions for datasets. These nodes ensure that image assets are efficiently and correctly prepared for further processing within the graphcap pipeline.

Major IO Node Types
===================

1. **ImageSamplingNode**
  
   - **Purpose:**  
     Loads images from a specified directory or file and applies sampling methods—such as random, incremental, or latest—to select a subset of images for processing.
     
   - **Features:**  
     - Scans directories for image files while filtering by allowed file extensions.
     - Supports multiple sampling strategies: `random`, `incremental`, and `latest`.
     - Returns a list of selected image paths along with sampling statistics.
     
   - **Usage Example:**
     
     .. code-block:: python
     
         from graphcap.io.nodes.image_sampling import ImageSamplingNode
         
         sampling_node = ImageSamplingNode()
         results = await sampling_node.sample(path="./images", sample_size=10, sample_method="random")
         print(results)
         

2. **CopyImagesNode**
  
   - **Purpose:**  
     Copies images from a source directory to a designated target directory in batch mode while optionally preserving the original directory structure.
     
   - **Features:**  
     - Performs batch image copying.
     - Optionally preserves source directory structure relative to a common parent.
     - Tracks progress and logs copy statistics (e.g., total size, number of failures).
     - Returns a list of copied image paths along with detailed copy information.
     
   - **Usage Example:**
  
     .. code-block:: python
     
         from graphcap.io.nodes.copy_images import CopyImagesNode
         
         copy_node = CopyImagesNode()
         results = await copy_node.execute(
             image_paths=["/path/to/image1.jpg", "/path/to/image2.jpg"],
             target_dir="./output",
             preserve_structure=True
         )
         print(results)

