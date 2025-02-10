.. SPDX-License-Identifier: Apache-2.0
.. graphcap.module.doc.midjourney_data

===============================================
Midjourney Metadata Extraction and Documentation
===============================================

Overview
========
This document outlines the extraction process for Midjourney style metadata within graphcap.
The extraction asset is implemented in the module:

   ``pipelines/pipelines/io/image/image_metadata/common_formats/midjourney_metadata.py``

This asset processes image descriptions (extracted from Exif metadata) to parse Midjourney-specific parameters,
and then merges these results with the core Exif metadata. The extracted metadata adheres to a defined TypedDict
schema (``MidjourneyMetadata``) that includes parameters such as aspect ratio, chaos level, quality, seed, stylize, and more.

Key Features
------------
- **Typed Metadata Extraction:**  
  Uses a ``MidjourneyMetadata`` TypedDict to enforce a consistent schema for extracted fields including:
  - Aspect Ratio
  - Chaos
  - Quality, Seed, Stylize, and other numerical or textual parameters.
- **Integration with Exif Data:**  
  Merges the original Exif metadata with the parsed Midjourney parameters to provide a comprehensive data record
  for each image.
- **Flexible Output Formats:**  
  The final, combined metadata is exported in both Parquet and newline-delimited JSON formats.
- **Robust Parsing:**  
  Designed to gracefully handle missing or malformed parameters within image descriptions.

Asset Implementation Details
============================
The Midjourney metadata extraction asset follows these steps:

1. **Reading Exif Data:**  
   The asset begins by loading a Parquet file containing Exif metadata.
2. **Iterating Over Records:**  
   Each image record is processed to extract the "Description" field where Midjourney parameters are embedded.
3. **Parameter Extraction:**  
   The helper function ``extract_midjourney_parameters(description)`` is called to parse the description text
   and extract all relevant Midjourney-specific parameters.
4. **Data Aggregation:**  
   The extracted parameters from all images are compiled into a separate DataFrame.
5. **Data Merging:**  
   The asset merges the original Exif DataFrame with the Midjourney parameters DataFrame, ensuring that each image's record
   is enriched with both low-level (Exif) and high-level (Midjourney) metadata.
6. **Output Generation:**  
   The combined DataFrame is saved to disk as:
   - A Parquet file for efficient storage and querying.
   - A newline-delimited JSON file for interoperability with other systems.

File Location
=============
The Midjourney metadata extraction asset is defined in:

   ``pipelines/pipelines/io/image/image_metadata/common_formats/midjourney_metadata.py``

