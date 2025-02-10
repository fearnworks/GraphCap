.. SPDX-License-Identifier: Apache-2.0
.. graphcap.module.doc.xmp_data

===================================
XMP Metadata Extraction and Documentation
===================================

Overview
========
This document describes the extraction of XMP metadata from images in graphcap. The dedicated asset for extracting XMP metadata is implemented in the module:

   ``pipelines/pipelines/io/image/image_metadata/common_formats/xmp_metadata.py``

The asset targets specific XMP fields from the Exif metadata record such as:
- **XMPToolkit:** For example, "XMP Core 4.4.0-Exiv2".
- **DigitalImageGUID:** A unique identifier assigned to an image.
- **DigitalSourceType:** A URI categorizing the digital source type, e.g., "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia".

Key Features
------------
- **Scoped Extraction:** Focuses only on XMP-specific fields present in the Exif metadata.
- **Typed Data Structure:** Utilizes a TypedDict (``XMPMetadata``) to enforce a consistent schema for the extracted values.
- **Integration with Core Image Records:** Augments each XMP record with a ``source_file`` identifier, enabling correlation with the primary image data.
- **Output Flexibility:** The extracted data is stored in both Parquet and JSON formats for efficient storage and downstream processing.

Asset Implementation Details
============================
The extraction asset operates as follows:

1. **Data Extraction:**  
   The function ``extract_xmp_metadata`` scans the entire Exif metadata record (obtained via ExifTool) and pulls out:
   - ``XMPToolkit``
   - ``DigitalImageGUID``
   - ``DigitalSourceType``

2. **Aggregation:**  
   Each metadata record is processed in a loop, where the extracted XMP values are combined with the image's unique identifier (``source_file``). All extracted records are then aggregated into a Pandas DataFrame.

3. **Data Storage:**  
   The aggregated DataFrame is saved to disk in two formats:
   - A Parquet file for efficient storage and querying.
   - A newline-delimited JSON file for interoperability with other systems.

