===========================
Dataset Nodes
===========================

Overview
========
Dataset Nodes in GraphCap are a specialized set of nodes designed to transform raw caption outputs into structured datasets that can be used for analysis, model training, or sharing on platforms like HuggingFace Hub. These nodes interact with the dataset management modules to handle exporting, metadata generation, and (optionally) uploading the generated datasets.

Major Node Types
================

1. **DatasetExportNode**
   
   - **Purpose:**  
     Converts perspective outputs from the image captioning pipeline into a standardized dataset. It aggregates captions, formats metadata (including configuration, version, and provider details), and exports the results in JSONL format.
   
   - **Features:**
     - Aggregates caption outputs from multiple perspectives.
     - Formats metadata including configuration details and versioning.
     - Exports the data to a JSONL file.
     - Optionally triggers an upload to the HuggingFace Hub using provided API tokens.
   
   - **Usage Example:**
   
     .. code-block:: python

         from graphcap.dataset.nodes.export import DatasetExportNode

         # Example inputs for the node; in a real-world scenario, these would be provided by the DAG infrastructure.
         node_inputs = {
             "output_paths": {
                 "image": "/path/to/image.jpg",
                 "caption_formal": "/path/to/formal_caption.txt",
             },
             "batch_dir": "/path/to/batch",
             "dataset_config": {
                 "name": "My Dataset",
                 "description": "A dataset generated from image captions",
                 "tags": ["image-captioning", "graphcap"],
                 "include_images": True,
                 "use_hf_urls": False,
             },
             "push_to_hub": True,
             "hf_token_env": "HUGGING_FACE_HUB_TOKEN",
             "private": False,
         }

         # In an asynchronous execution context, the node is executed as follows:
         results = await DatasetExportNode().execute(**node_inputs)
         print(results)

Future Extensions
=================
GraphCap is designed for extensibility. Future dataset nodes may include:
- **DatasetImportNode:** To import and validate existing dataset structures.
- **DatasetMergeNode:** To combine multiple datasets into a unified dataset.
- **DatasetCleanseNode:** For filtering and cleansing caption data before export.

