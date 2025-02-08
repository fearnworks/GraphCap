# SPDX-License-Identifier: Apache-2.0
"""Pipeline definitions combining all assets and resources."""

import dagster as dg


from .caption_generation.perspectives import (
    image_selection_asset,
    provider_selection_asset,
    caption_generation_asset
)
from .huggingface.dataset_export import (
    dataset_metadata_asset,
    dataset_verification_asset,
    huggingface_upload_asset
)
from .huggingface.dataset_import import (
    dataset_download_asset,
    dataset_validation_asset
)
from .assets import (
    raw_images_asset,
    art_analysis_results_asset,
    final_dataset_asset
)

# Import resources and IO managers
from .common.resources import PostgresConfig, FileSystemConfig
from .common.io import SimpleFileSystemIOManager

# # Import sensors
# from .sensors.image_sensors import (
#     new_image_sensor,
#     art_analysis_asset_sensor
# )

# Define jobs
caption_job = dg.define_asset_job(
    "caption_generation",
    selection=[
        image_selection_asset,
        provider_selection_asset,
        caption_generation_asset
    ]
)

export_job = dg.define_asset_job(
    "dataset_export",
    selection=[
        dataset_metadata_asset,
        dataset_verification_asset,
        huggingface_upload_asset
    ]
)

import_job = dg.define_asset_job(
    "dataset_import",
    selection=[
        dataset_download_asset,
        dataset_validation_asset
    ]
)

# Define schedules
daily_caption_schedule = dg.ScheduleDefinition(
    job=caption_job,
    cron_schedule="0 0 * * *"
)

# Combine all definitions
defs = dg.Definitions(
    assets=[
        raw_images_asset,
        art_analysis_results_asset,
        final_dataset_asset,
        image_selection_asset,
        provider_selection_asset,
        caption_generation_asset,
        dataset_metadata_asset,
        dataset_verification_asset,
        huggingface_upload_asset,
        dataset_download_asset,
        dataset_validation_asset
    ],
    resources={
        "postgres": PostgresConfig(),
        "fs": FileSystemConfig(),
        "fs_io_manager": SimpleFileSystemIOManager()
    },
    jobs=[caption_job, export_job, import_job],
    schedules=[daily_caption_schedule],
    # sensors=[new_image_sensor, art_analysis_asset_sensor]
)