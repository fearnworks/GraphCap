# SPDX-License-Identifier: Apache-2.0
"""
Assets and ops for importing datasets from Hugging Face Hub.

This module provides assets and functions to download datasets from the Hugging Face Hub.
It supports three methods of downloading:
1. Using Git LFS to clone the entire repository (recommended for full datasets)
2. Using the datasets library (recommended for standardized dataset access)
3. Using huggingface_hub for direct file access (recommended for specific files)

Assets:
    dataset_download: Downloads a dataset using the configured method.
    dataset_parse: Parses the downloaded dataset and saves it to the specified output directory.
"""

import json
import subprocess
from pathlib import Path

import dagster as dg
from datasets import load_dataset
from huggingface_hub import hf_hub_download

from .types import DatasetImportConfig, DatasetParseConfig


def _clone_with_git_lfs(
    repo_id: str, local_dir: Path, context: dg.AssetExecutionContext, fresh_clone: bool = True
) -> None:
    """
    Clones a dataset repository using Git LFS.

    This is the recommended method for downloading complete datasets as it properly
    handles large files and maintains the exact repository structure.
    """
    # Ensure git-lfs is installed
    try:
        subprocess.run(["git", "lfs", "install"], check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to initialize Git LFS. Is it installed?") from e

    # Clean up existing directory if it exists
    if local_dir.exists() and fresh_clone:
        context.log.info(f"Cleaning up existing directory: {local_dir}")
        try:
            subprocess.run(["rm", "-rf", str(local_dir)], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clean up directory {local_dir}: {e.stderr.decode()}") from e

    # Clone the repository
    repo_url = f"https://huggingface.co/datasets/{repo_id}"
    try:
        subprocess.run(["git", "clone", repo_url, str(local_dir)], check=True, capture_output=True)
        context.log.info(f"Successfully cloned repository {repo_id} to {local_dir}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to clone repository {repo_id}: {e.stderr.decode()}") from e


def _download_with_datasets(repo_id: str, local_dir: Path, context: dg.AssetExecutionContext) -> None:
    """
    Downloads a dataset using the datasets library.

    This method is recommended for datasets that follow the Hugging Face datasets format
    and when you want to work with the dataset using the datasets library features.
    """
    try:
        dataset = load_dataset(repo_id, cache_dir=str(local_dir))
        context.log.info(f"Successfully loaded dataset {repo_id} using datasets library")
        # Print dataset info for verification
        context.log.info(f"Dataset structure: {dataset}")
    except Exception as e:
        raise ValueError(f"Failed to load dataset {repo_id} with datasets library: {e}")


def _download_file(repo_id: str, filename: str, local_dir: Path, context: dg.AssetExecutionContext) -> Path:
    """
    Downloads a specific file from the dataset repository.

    This method is recommended when you only need specific files from the dataset.
    """
    try:
        file_path = hf_hub_download(
            repo_id=repo_id, filename=filename, repo_type="dataset", local_dir=str(local_dir), force_download=True
        )
        context.log.info(f"Successfully downloaded file {filename} from {repo_id}")
        return Path(file_path)
    except Exception as e:
        raise ValueError(f"Failed to download file {filename} from {repo_id}: {e}")


@dg.asset(group_name="dataset_import", compute_kind="python")
def dataset_download(context: dg.AssetExecutionContext, config: DatasetImportConfig) -> str:
    """
    Downloads a dataset from the Hugging Face Hub using the specified method.

    Args:
        context: Dagster execution context
        config: Configuration specifying how to download the dataset

    Returns:
        str: Path to the downloaded dataset
    """
    local_dir = Path(config.local_dir)
    local_dir.mkdir(parents=True, exist_ok=True)

    context.log.info(f"Downloading dataset {config.repo_id} to {local_dir}")

    if config.use_git_lfs:
        _clone_with_git_lfs(config.repo_id, local_dir, context, fresh_clone=config.fresh_clone)
    elif config.use_datasets_library:
        _download_with_datasets(config.repo_id, local_dir, context)
    elif config.filename:
        _download_file(config.repo_id, config.filename, local_dir, context)
    else:
        raise ValueError("Must specify one of: use_git_lfs=True, use_datasets_library=True, or filename")

    return str(local_dir)


@dg.asset(group_name="dataset_import", compute_kind="python", deps=[dataset_download])
def dataset_parse(context: dg.AssetExecutionContext, dataset_download: str, config: DatasetParseConfig) -> None:
    """
    Parses the downloaded dataset and saves it to the specified output directory.

    For Git LFS downloaded repositories, this will:
    1. Read the dataset structure
    2. Parse any metadata files
    3. Create a standardized format in the output directory

    Args:
        context: Dagster execution context
        dataset_download: Path to the downloaded dataset
        config: Configuration for parsing the dataset
    """
    input_dir = Path(dataset_download)
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    context.log.info(f"Parsing dataset from {input_dir} to {output_dir}")

    # Read dataset structure
    if not input_dir.is_dir():
        raise ValueError(f"Dataset path {input_dir} is not a directory")

    # List all files in the repository
    files = list(input_dir.rglob("*"))
    context.log.info(f"Found {len(files)} files in dataset")

    # Basic structure analysis
    data_files = [f for f in files if f.is_file()]
    for file in data_files:
        rel_path = file.relative_to(input_dir)
        context.log.debug(f"Found file: {rel_path}")

    # For now, just create a simple manifest
    manifest = {
        "dataset_path": str(input_dir),
        "file_count": len(data_files),
        "files": [str(f.relative_to(input_dir)) for f in data_files],
    }

    # Write manifest
    manifest_file = output_dir / "dataset_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)

    context.log.info(f"Created dataset manifest at {manifest_file}")
