"""
# SPDX-License-Identifier: Apache-2.0
Image Metadata Pipeline Job (Midjourney)

Orchestrates the image metadata pipeline for open datasets with a custom source format.

"""

import dagster as dg

midjourney_metadata_pipeline = dg.define_asset_job(
    name="midjourney_metadata_pipeline",
    selection=[
        "image_dataset_config",
        "image_list",
        "image_list_exif_data",
        "midjourney_metadata",
        "iptc_metadata",
        "xmp_metadata",
    ],
    description="Example of indexing images and storing metadata from a custom source format.",
)
