"""
# SPDX-License-Identifier: Apache-2.0
graphcap.tests.lib.node_tests.test_image_sampling

Tests for image sampling node functionality.

Key features:
- Image loading and validation
- Sampling method verification
- Sample size handling
- Path validation
- Sampling information accuracy

Classes:
    None (contains test functions only)
"""

import json
from pathlib import Path

import pytest
from graphcap.dag.dag import DAG
from graphcap.io import ImageSamplingNode


@pytest.fixture
def test_configs(test_data_dir):
    """Fixture providing test configurations for image sampling."""
    return [
        {
            "nodes": [
                {
                    "id": "basic_loader",
                    "type": "ImageSamplingNode",
                    "config": {"path": str(test_data_dir), "sample_size": 0, "sample_method": "random"},
                    "dependencies": [],
                }
            ]
        },
        {
            "nodes": [
                {
                    "id": "sample_latest",
                    "type": "ImageSamplingNode",
                    "config": {"path": str(test_data_dir), "sample_size": 2, "sample_method": "latest"},
                    "dependencies": [],
                }
            ]
        },
        {
            "nodes": [
                {
                    "id": "sample_incremental",
                    "type": "ImageSamplingNode",
                    "config": {"path": str(test_data_dir), "sample_size": 1, "sample_method": "incremental"},
                    "dependencies": [],
                }
            ]
        },
    ]


@pytest.mark.asyncio
async def test_basic_image_loading(test_data_dir):
    """
    GIVEN a directory with test images
    WHEN creating an ImageSamplingNode with basic configuration
    THEN should load all images without sampling
    """
    node = ImageSamplingNode(id="test_loader")
    result = await node.execute(path=str(test_data_dir), sample_size=0, sample_method="random")

    assert "image_paths" in result
    assert "sampling_info" in result
    assert len(result["image_paths"]) > 0
    assert result["sampling_info"]["sample_method"] == "all"


@pytest.mark.asyncio
async def test_image_sampling_methods(test_configs, test_data_dir):
    """
    GIVEN different sampling configurations
    WHEN executing nodes with different sampling methods
    THEN should correctly sample images according to each method
    """
    node_classes = {"ImageSamplingNode": ImageSamplingNode}

    for config in test_configs:
        # Create and validate DAG
        dag = DAG.from_json(json.dumps(config), node_classes)
        assert dag.validate()

        # Execute DAG
        results = await dag.execute()

        # Verify results for each node
        for node_id, result in results.items():
            assert "image_paths" in result
            assert "sampling_info" in result

            info = result["sampling_info"]
            paths = result["image_paths"]

            # Verify sampling size
            if info["sample_method"] != "all":
                sample_size = config["nodes"][0]["config"]["sample_size"]
                assert len(paths) == sample_size

            # Verify paths exist
            for path in paths:
                assert Path(path).exists()


@pytest.mark.asyncio
async def test_invalid_path():
    """
    GIVEN an invalid path
    WHEN executing the node
    THEN should raise appropriate error
    """
    node = ImageSamplingNode(id="test_invalid")

    with pytest.raises(ValueError):
        await node.execute(path="./nonexistent/path", sample_size=0, sample_method="random")


@pytest.mark.asyncio
async def test_sampling_consistency(test_data_dir):
    """
    GIVEN same configuration
    WHEN sampling with 'incremental' or 'latest' method
    THEN should return consistent results
    """
    node = ImageSamplingNode(id="test_consistent")

    # Test incremental sampling
    result1 = await node.execute(path=str(test_data_dir), sample_size=2, sample_method="incremental")
    result2 = await node.execute(path=str(test_data_dir), sample_size=2, sample_method="incremental")

    # Same configuration should yield same results for deterministic methods
    assert result1["image_paths"] == result2["image_paths"]


@pytest.mark.asyncio
async def test_sampling_info_accuracy(test_data_dir):
    """
    GIVEN a directory with known number of images
    WHEN sampling with different sizes
    THEN should report accurate sampling information
    """
    node = ImageSamplingNode(id="test_info")

    # Get total number of images
    full_result = await node.execute(path=str(test_data_dir), sample_size=0, sample_method="random")
    total_images = len(full_result["image_paths"])

    # Test with specific sample size
    sample_size = 2
    result = await node.execute(path=str(test_data_dir), sample_size=sample_size, sample_method="random")

    assert result["sampling_info"]["original_count"] == total_images
    assert result["sampling_info"]["sample_size"] == sample_size
    assert result["sampling_info"]["sample_method"] == "random"


@pytest.mark.asyncio
async def test_schema_validation():
    """
    GIVEN node schema
    WHEN validating inputs
    THEN should enforce required parameters
    """
    node = ImageSamplingNode(id="test_schema")

    # Test missing required parameter
    with pytest.raises(ValueError, match="Missing required parameter: path"):
        node.validate_inputs(sample_size=0, sample_method="random")

    # Test valid parameters
    assert node.validate_inputs(path="./test", sample_size=0, sample_method="random")
