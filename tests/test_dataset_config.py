import json
import os
from pathlib import Path

import pytest
from graphcap.dataset.dataset_manager import DatasetManager
from graphcap.dataset.metadata import DatasetConfig


@pytest.fixture(scope="session")
def test_dataset_manager(test_export_dir):
    """Create a dataset manager instance for testing"""
    return DatasetManager(export_dir=test_export_dir)


@pytest.mark.asyncio
async def test_export_to_jsonl(test_dataset_manager, test_captions, test_export_dir):
    """
    GIVEN a list of valid captions
    WHEN exporting to JSONL format
    THEN should create a JSONL file with correct content
    """
    output_path = await test_dataset_manager.export_to_jsonl(test_captions)

    assert output_path.exists()
    assert output_path.parent == test_export_dir

    # Verify contents
    exported_captions = []
    with output_path.open() as f:
        for line in f:
            exported_captions.append(json.loads(line))

    assert len(exported_captions) == len(test_captions)


@pytest.mark.asyncio
async def test_export_to_jsonl_empty_captions(test_dataset_manager):
    """
    GIVEN an empty list of captions
    WHEN exporting to JSONL
    THEN should create an empty JSONL file
    """
    output_path = await test_dataset_manager.export_to_jsonl([])
    assert output_path.exists()
    assert output_path.stat().st_size == 0


@pytest.mark.asyncio
async def test_create_hf_dataset_no_push(test_dataset_manager, test_dataset_config):
    """
    GIVEN a dataset configuration without push to hub
    WHEN creating dataset
    THEN should return local file path
    """
    config = DatasetConfig(**test_dataset_config)
    result = await test_dataset_manager.create_hf_dataset(
        Path("test.jsonl"),
        config,
        push_to_hub=False,
    )
    assert result == "test.jsonl"


@pytest.mark.asyncio
async def test_work_session_operations(test_dataset_manager):
    """
    GIVEN session data
    WHEN performing work session operations
    THEN should correctly save and load data
    """
    # Test data
    session_data = {"key": "value", "test_data": [1, 2, 3], "nested": {"a": 1, "b": 2}}
    session_id = "test_session"

    # Save session
    saved_path = await test_dataset_manager.save_work_session(session_data, session_id)
    assert saved_path.exists()

    # Load session
    loaded_data = await test_dataset_manager.load_work_session(session_id)
    assert loaded_data == session_data

    # Test loading non-existent session
    missing_data = await test_dataset_manager.load_work_session("missing_session")
    assert missing_data is None


@pytest.mark.asyncio
async def test_work_session_invalid_data(test_dataset_manager):
    """
    GIVEN invalid session data
    WHEN saving work session
    THEN should raise TypeError
    """
    invalid_data = {"key": lambda x: x}  # Functions are not JSON serializable

    with pytest.raises(TypeError):
        await test_dataset_manager.save_work_session(invalid_data, "test_session")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_hf_dataset_with_push(test_dataset_manager, test_dataset_config, test_captions):
    """
    GIVEN valid dataset configuration and HF token
    WHEN pushing to Hugging Face hub
    THEN should successfully create and upload dataset
    """
    hf_token = os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not hf_token:
        pytest.skip("No Hugging Face token available")

    config = DatasetConfig(**test_dataset_config)

    # First export the test captions
    jsonl_path = await test_dataset_manager.export_to_jsonl(test_captions)

    # Create and push dataset
    result = await test_dataset_manager.create_hf_dataset(
        jsonl_path,
        config,
        push_to_hub=True,
        token=hf_token,
        private=True,
    )

    assert "huggingface.co/datasets/" in result
    assert config.name in result


@pytest.mark.asyncio
async def test_export_with_custom_path(test_dataset_manager, test_captions, test_export_dir):
    """
    GIVEN custom output path
    WHEN exporting captions
    THEN should use specified path
    """
    custom_path = test_export_dir / "custom_output.jsonl"
    output_path = await test_dataset_manager.export_to_jsonl(test_captions, output_path=custom_path)

    assert output_path == custom_path
    assert output_path.exists()


@pytest.mark.asyncio
async def test_export_jsonl_relative_paths(test_dataset_manager, test_captions, test_export_dir):
    """
    GIVEN a list of captions with image paths
    WHEN exporting to JSONL format
    THEN should convert image paths to be relative to the output JSONL file location

    Note:
        If input caption has filename "../datasets/os_img/new-york-7781184_640.jpg"
        and JSONL is in same directory as images, output should be "./images/new-york-7781184_640.jpg"
    """
    # Create test captions with absolute/different-relative paths
    test_data = [
        {**test_captions[0], "filename": "../datasets/os_img/new-york-7781184_640.jpg"},
        {**test_captions[1], "filename": "/absolute/path/image.jpg"},
    ]

    output_path = test_export_dir / "images" / "captions.jsonl"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export captions
    result_path = await test_dataset_manager.export_to_jsonl(test_data, output_path=output_path)

    # Read exported file
    with result_path.open() as f:
        exported_captions = [json.loads(line) for line in f]

    # Verify paths are relative to JSONL file location
    assert exported_captions[0]["filename"] == "./images/new-york-7781184_640.jpg"
    assert exported_captions[1]["filename"] == "./images/image.jpg"
