# SPDX-License-Identifier: Apache-2.0
"""Image analysis monitoring sensors."""

import os
import time
import dagster as dg

# @dg.sensor(job="image_pipeline_asset_job", minimum_interval_seconds=30)
# def new_image_sensor(context: dg.SensorEvaluationContext):
#     """Monitor for new images."""
#     image_dir = "/workspace/datasets/os_img"
#     last_run_timestamp = float(context.cursor) if context.cursor else 0
#     current_timestamp = time.time()
#     new_images_found = False

#     for filename in os.listdir(image_dir):
#         filepath = os.path.join(image_dir, filename)
#         if os.path.isfile(filepath) and os.path.getmtime(filepath) > last_run_timestamp:
#             new_images_found = True
#             break

#     if new_images_found:
#         context.update_cursor(str(current_timestamp))
#         yield dg.RunRequest()
#     else:
#         yield dg.SkipReason("No new images found since last run.")

# @dg.asset_sensor(asset_key="art_analysis_results_asset", job="dataset_export_job")
# def art_analysis_asset_sensor(context: dg.SensorEvaluationContext, asset_event):
#     """Monitor art analysis completion."""
#     context.log.info(f"Art analysis asset materialized, triggering dataset export.")
#     return dg.RunRequest() 