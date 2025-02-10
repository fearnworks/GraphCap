.. SPDX-License-Identifier: Apache-2.0
.. graphcap.module.doc.exif_extraction

===============================
Exif Metadata Extraction Assets
===============================

Overview
========
The Exif Metadata Extraction asset in graphcap is responsible for extracting detailed metadata
from image files using ExifTool. This asset is implemented in
``pipelines/pipelines/io/image/image_metadata/extract_exif.py`` and serves as the primary entry point
for gathering comprehensive metadata from images. The metadata is then stored in both Parquet and JSON formats,
making it easily accessible for downstream processing and integration with other metadata assets.

Key Features
------------
- **Automated Extraction:** 
  - Iterates over a list of image paths.
  - Runs ExifTool on each image to extract detailed metadata.
- **Output Formats:** 
  - Saves the results in a Parquet file for efficient storage and querying.
  - Also serializes the results as newline-delimited JSON for interoperability.
- **Directory Management:**
  - Ensures that the output directory (``metadata/`` subdirectory) exists before writing files.
- **Robust Error Handling:**
  - Catches exceptions during metadata extraction to ensure that the asset completes processing for all images,
    even if some images fail.
- **Logging:**
  - Provides debug and info level logging to track the extraction progress and any errors encountered.

Asset Implementation Details
=============================
The asset is defined as an asynchronous function that uses the Dagster framework to manage execution,
logging, and output file generation. The general steps are as follows:

1. **Image Iteration:** The asset loops through a provided list of image paths.
2. **Metadata Extraction:** For each image, metadata is extracted using ExifTool via the helper function
   ``run_exiftool(image_path)``.
3. **Data Aggregation:** Collected metadata is accumulated into a list of dictionaries.
4. **DataFrame Conversion:** The aggregated metadata is converted into a Pandas DataFrame.
5. **Output Directory Creation:** Before saving, the code ensures that the target output directory exists using
   ``mkdir(parents=True, exist_ok=True)``.
6. **File Storage:** The DataFrame is saved as a Parquet file and also serialized to a JSON file.
7. **Logging:** Information about the file paths is logged for debugging and operational review.

File Location
=============
- The Exif extraction asset is located at:
  
  ``pipelines/pipelines/io/image/image_metadata/extract_exif.py``

Usage
=====
The Exif extraction asset is typically invoked as part of a larger metadata extraction pipeline.
It receives a list of image file paths and outputs the path to the generated Parquet file containing the
metadata. Downstream metadata extraction assets (such as those for  XMP, IPTC, etc.)
can then use this Parquet file as their input source.


