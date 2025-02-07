import dagster as dg
from dagster import OutputContext, InputContext, IOManager
from typing import List, Dict
import os
import time

# --- Resources ---
class ImageLoadingConfig(dg.ConfigurableResource):
    image_dir: str

@dg.resource
def image_loading_resource(context: dg.InitResourceContext) -> ImageLoadingConfig:
    return ImageLoadingConfig.from_config_value(context.resource_config)

# --- IO Managers ---
class SimpleFileSystemIOManager(IOManager):
    def handle_output(self, context: OutputContext, obj: List[str]):
        context.log.info(f"Outputting image paths: {obj}")

    def load_input(self, context: InputContext) -> List[str]:
        image_dir = "/workspace/datasets/os_img"
        return [os.path.join(image_dir, f) for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

# --- Assets ---
@dg.asset(name="raw_images")
def raw_images_asset(context: dg.AssetExecutionContext) -> List[str]:
    image_dir = "/workspace/datasets/os_img"
    context.log.info(f"Loading images from: {image_dir}")
    return [f"{image_dir}/image_{i}.jpg" for i in range(5)]

@dg.asset(name="art_analysis_results", deps=[raw_images_asset])
def art_analysis_results_asset(context: dg.AssetExecutionContext, raw_images: List[str]) -> Dict[str, str]:
    context.log.info(f"Performing art analysis on {len(raw_images)} images")
    results = {}
    for image_path in raw_images:
        results[image_path] = f"Art analysis result for {image_path}"
    return results

@dg.asset(name="final_dataset", deps=[art_analysis_results_asset])
def final_dataset_asset(context: dg.AssetExecutionContext, art_analysis_results: Dict[str, str]) -> str:
    context.log.info("Exporting dataset...")
    dataset_path = "/workspace/.local/output/dags/smoke/dataset.json"
    with open(dataset_path, 'w') as f:
        import json
        json.dump(art_analysis_results, f, indent=4)
    return dataset_path

@dg.asset(name="raw_images_resource_asset", required_resource_keys={"image_config"})
def raw_images_resource_asset(context: dg.AssetExecutionContext) -> List[str]:
    image_dir = context.resources.image_config.image_dir
    context.log.info(f"Loading images from resource config: {image_dir}")
    return [f"{image_dir}/image_{i}.jpg" for i in range(5)]

@dg.asset(io_manager_key="fs_io_manager")
def raw_images_io_asset(context: dg.AssetExecutionContext) -> List[str]:
    context.log.info("Loading images using FileSystemIOManager")
    image_dir = "/workspace/datasets/os_img"
    return [f"{image_dir}/image_{i}.jpg" for i in range(5)]

@dg.asset(deps=[raw_images_io_asset], io_manager_key="fs_io_manager")
def art_analysis_io_asset(context: dg.AssetExecutionContext, raw_images_io_asset: List[str]) -> Dict[str, str]:
    context.log.info(f"Performing art analysis with IO Manager context on {len(raw_images_io_asset)} images")
    results = {}
    for image_path in raw_images_io_asset:
        results[image_path] = f"Art analysis result from IO Asset for {image_path}"
    return results

@dg.asset(
    name="art_analysis_eager_asset",
    deps=[raw_images_asset],
    automation_condition=dg.AutomationCondition.eager()
)
def art_analysis_eager_asset(context: dg.AssetExecutionContext, raw_images: List[str]) -> Dict[str, str]:
    context.log.info(f"Eagerly performing art analysis on {len(raw_images)} images")
    results = {}
    for image_path in raw_images:
        results[image_path] = f"Eager Art analysis result for {image_path}"
    return results

# --- Ops ---
@dg.op(name="load_images_op")
def load_images_op(context: dg.OpExecutionContext) -> List[str]:
    image_dir = "/workspace/datasets/os_img"
    context.log.info(f"Loading images from: {image_dir} (Op)")
    return [f"{image_dir}/image_{i}.jpg" for i in range(5)]

@dg.op(name="art_analysis_op")
def art_analysis_op(context: dg.OpExecutionContext, image_paths: List[str]) -> Dict[str, str]:
    context.log.info(f"Performing art analysis on {len(image_paths)} images (Op)")
    results = {}
    for image_path in image_paths:
        results[image_path] = f"Art analysis result from Op for {image_path}"
    return results

@dg.op(name="export_dataset_op")
def export_dataset_op(context: dg.OpExecutionContext, analysis_results: Dict[str, str]) -> str:
    context.log.info("Exporting dataset from Op...")
    dataset_path = "/workspace/.local/output/dags/smoke/dataset_op.json"
    with open(dataset_path, 'w') as f:
        import json
        json.dump(analysis_results, f, indent=4)
    return dataset_path

# --- Jobs ---
asset_job = dg.define_asset_job("image_pipeline_asset_job", selection="*")
dataset_export_job = dg.define_asset_job("dataset_export_job", selection=[final_dataset_asset])

@dg.job(name="image_pipeline_op_job")
def image_pipeline_op_job():
    image_paths = load_images_op()
    analysis_results = art_analysis_op(image_paths)
    export_dataset_op(analysis_results)

# --- Schedules ---
daily_image_pipeline_schedule = dg.ScheduleDefinition(
    job=asset_job,
    cron_schedule="0 0 * * *"
)

# --- Sensors ---
@dg.sensor(job=asset_job, minimum_interval_seconds=30)
def new_image_sensor(context: dg.SensorEvaluationContext):
    image_dir = "/workspace/datasets/os_img"
    last_run_timestamp = float(context.cursor) if context.cursor else 0
    current_timestamp = time.time()
    new_images_found = False

    for filename in os.listdir(image_dir):
        filepath = os.path.join(image_dir, filename)
        if os.path.isfile(filepath) and os.path.getmtime(filepath) > last_run_timestamp:
            new_images_found = True
            break

    if new_images_found:
        context.update_cursor(str(current_timestamp))
        yield dg.RunRequest()
    else:
        yield dg.SkipReason("No new images found since last run.")

# --- Asset Sensors ---
@dg.asset_sensor(asset_key=dg.AssetKey("art_analysis_results_asset"), job=dataset_export_job)
def art_analysis_asset_sensor(context: dg.SensorEvaluationContext, asset_event):
    context.log.info(f"Art analysis asset materialized, triggering dataset export.")
    return dg.RunRequest()


# --- Definitions ---
defs = dg.Definitions(
    assets=[
        raw_images_asset,
        art_analysis_results_asset,
        final_dataset_asset,
        raw_images_resource_asset,
        raw_images_io_asset,
        art_analysis_io_asset,
        art_analysis_eager_asset
    ],
    jobs=[
        asset_job,
        image_pipeline_op_job,
        dataset_export_job
    ],
    schedules=[daily_image_pipeline_schedule],
    sensors=[new_image_sensor, art_analysis_asset_sensor],
    resources={
        "image_config": image_loading_resource,
        "fs_io_manager": SimpleFileSystemIOManager()
    }
)