# SPDX-License-Identifier: Apache-2.0
"""Assets and ops for exporting datasets to Hugging Face Hub."""

from pathlib import Path
from typing import List

import dagster as dg
from huggingface_hub import upload_file

from ..perspectives.types import PerspectiveCaptionOutput
from .dataset_manifest import (
    create_dataset_manifest,
    load_perspective_results_from_manifest,
)
from .dataset_prep import create_huggingface_dataset
from .dataset_readme import generate_readme_content
from .perspective_export import upload_perspective_dataset_to_huggingface
from .types import DatasetMetadata


class HfUploadManifestConfig(dg.Config):
    """Configuration schema for the huggingface_upload_manifest asset."""

    dataset_name: str
    namespace: str
    dataset_description: str
    dataset_tags: List[str]
    include_images: bool = True
    use_hf_urls: bool = False
    private_dataset: bool = False


@dg.asset(group_name="dataset_export", compute_kind="python")
def dataset_metadata(context: dg.AssetExecutionContext) -> DatasetMetadata:
    """Generate dataset metadata."""
    context.log.info("Generating dataset metadata")
    # Implementation here
    return {}


@dg.asset(
    group_name="dataset_export",
    compute_kind="python",
    deps=[dataset_metadata, "perspective_caption"],
)
def dataset_export_manifest(
    context: dg.AssetExecutionContext,
    dataset_metadata: DatasetMetadata,
    perspective_caption: PerspectiveCaptionOutput,
) -> dg.MaterializeResult:
    """Generate export manifest for dataset."""
    context.log.info("Generating export manifest")
    # Placeholder for manifest generation logic
    export_dir = Path(str(context.instance.root_directory)) / "dataset_export"
    export_dir.mkdir(parents=True, exist_ok=True)

    # Create perspective results and manifest
    manifest_path = create_dataset_manifest(export_dir, perspective_caption)

    return dg.MaterializeResult(
        metadata={
            "export_dir": str(export_dir),
            "manifest_path": str(manifest_path),
        }
    )


@dg.asset(
    group_name="dataset_export",
    compute_kind="huggingface",
    description="""
    Uploads a manifest dataset to Hugging Face Hub.
    """,
)
def huggingface_upload_manifest(
    context: dg.AssetExecutionContext,
    dataset_metadata: DatasetMetadata,
    dataset_export_manifest: dg.MaterializeResult,
) -> dg.MaterializeResult:
    """
    Uploads the exported manifest dataset to Hugging Face Hub.

    Args:
        context (dg.AssetExecutionContext): Dagster asset execution context.
        dataset_metadata (dict[str, object]): Result from dataset metadata creation (dependency).
        dataset_export_manifest (dg.MaterializeResult): Result from manifest dataset export (provides export_dir and manifest_path).

    Returns:
        dg.MaterializeResult: Dagster materialization result with dataset information.
    """
    context.log.info("Starting Hugging Face dataset upload")

    metadata = dataset_export_manifest.metadata or {}
    export_dir_str = metadata.get("export_dir")
    manifest_path_str = metadata.get("manifest_path")

    if not export_dir_str:
        raise ValueError("Export directory not found in dataset_export_manifest metadata.")
    if not manifest_path_str:
        raise ValueError("Manifest path not found in dataset_export_manifest metadata.")

    export_dir = Path(str(export_dir_str))
    manifest_path = Path(str(manifest_path_str))

    # Load perspective results from manifest
    perspective_results = load_perspective_results_from_manifest(manifest_path)

    # Create Hugging Face Dataset
    hf_dataset = create_huggingface_dataset(perspective_results)

    # Push dataset to Hugging Face Hub
    dataset_url = upload_perspective_dataset_to_huggingface(
        hf_dataset=hf_dataset,
        dataset_name=dataset_name,
        namespace=namespace,
        huggingface_client=huggingface_client,
        private_dataset=private_dataset,
    )

    # Create dataset card content
    readme_content = generate_readme_content(
        dataset_name=dataset_name,
        dataset_description=dataset_description,
        dataset_tags=dataset_tags,
        perspective_results_len=len(perspective_results),
    )

    # Upload README.md
    repo_id = f"{namespace}/{dataset_name}"
    try:
        context.log.info(f"Uploading README.md to Hugging Face Hub: {repo_id}")
        upload_file(
            repo_id=repo_id,
            path_or_fileobj=readme_content.encode("utf-8"),
            path_in_repo="README.md",
            repo_type="dataset",
            token=huggingface_client.token,
        )
        context.log.info(f"README.md uploaded successfully to {repo_id}")
    except Exception as e:
        context.log.error(f"Error uploading README.md to Hugging Face Hub: {e}")
        raise

    return dg.MaterializeResult(
        metadata={
            "dataset_name": dataset_name,
            "namespace": namespace,
            "dataset_url": dataset_url,
        }
    )
