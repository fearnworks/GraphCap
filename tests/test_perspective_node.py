"""
# SPDX-License-Identifier: Apache-2.0
graphcap.tests.test_perspective_node

Integration tests for perspective node functionality.
"""

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from graphcap.caption.nodes import PerspectiveNode
from graphcap.dag.dag import DAG

# Load environment variables from root .env file
load_dotenv(Path(__file__).parents[2] / ".env")


@pytest.fixture(autouse=True)
def check_api_keys():
    """Skip tests if required API keys are not available."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("No GOOGLE_API_KEY or GEMINI_API_KEY found. Skipping perspective tests.")
    # Log key presence for debugging
    print(f"Using API key from {'GOOGLE_API_KEY' if os.getenv('GOOGLE_API_KEY') else 'GEMINI_API_KEY'}")


@pytest.fixture
def test_dag_config(test_data_dir):
    """Fixture providing test DAG configuration."""
    return {
        "nodes": [
            {
                "id": "image_loader",
                "type": "ImageSamplingNode",
                "config": {"path": str(test_data_dir), "sample_size": 1, "sample_method": "random"},
                "dependencies": [],
            },
            {
                "id": "art_analysis",
                "type": "PerspectiveNode",
                "config": {
                    "perspective_type": "art",
                    "provider_name": "gemini",
                    "model_params": {"max_tokens": 4096, "temperature": 0.8, "top_p": 0.9, "max_concurrent": 1},
                    "output": {
                        "directory": "./test_outputs",
                        "formats": ["dense"],
                        "store_logs": True,
                        "copy_images": False,
                    },
                },
                "dependencies": ["image_loader"],
            },
        ]
    }


@pytest.mark.asyncio
async def test_perspective_node_execution(test_dag_config, tmp_path):
    """
    Test perspective node execution in DAG.

    GIVEN a DAG with image sampling and perspective nodes
    WHEN executing the DAG
    THEN should process images and generate outputs correctly
    """
    # Update output directory to tmp_path
    test_dag_config["nodes"][1]["config"]["output"]["directory"] = str(tmp_path)

    # Create and validate DAG
    node_classes = {
        "ImageSamplingNode": "graphcap.io.nodes.image_sampling.ImageSamplingNode",
        "PerspectiveNode": "graphcap.caption.nodes.perspective.PerspectiveNode",
    }
    dag = DAG.from_dict(test_dag_config, node_classes)

    # Add node configurations after creation
    for node_config in test_dag_config["nodes"]:
        if "config" in node_config:
            dag.nodes[node_config["id"]].config = node_config["config"]

    assert dag.validate()

    # Execute DAG
    results = await dag.execute()

    # Verify image loader results
    assert "image_loader" in results
    image_loader_result = results["image_loader"]
    assert "image_paths" in image_loader_result
    assert len(image_loader_result["image_paths"]) == 1

    # Verify perspective node results
    assert "art_analysis" in results
    perspective_result = results["art_analysis"]
    assert "captions" in perspective_result
    assert "perspective_info" in perspective_result

    # Check perspective info
    info = perspective_result["perspective_info"]
    assert info["type"] == "art"
    assert info["total_images"] == 1
    assert info["successful"] == 1
    assert info["formats"] == ["dense"]
    assert Path(info["output_dir"]).exists()

    # Check captions
    captions = perspective_result["captions"]
    assert len(captions) == 1
    assert "parsed" in captions[0]
    assert "error" not in captions[0]["parsed"]


@pytest.mark.asyncio
async def test_perspective_node_validation():
    """Test perspective node validation."""
    node = PerspectiveNode(id="test_validation")

    # Test missing required parameters
    with pytest.raises(ValueError, match="Missing required parameter: image_paths"):
        node.validate_inputs(perspective_type="art")

    # Test invalid perspective type
    with pytest.raises(ValueError, match=r"Invalid value for perspective_type\. Must be one of:.*"):
        node.validate_inputs(image_paths=["test.jpg"], perspective_type="invalid")

    # Test valid configuration
    assert node.validate_inputs(
        image_paths=["test.jpg"],
        perspective_type="art",
        provider_name="gemini",
        model_params={"max_tokens": 4096, "temperature": 0.8},
        output={"formats": ["dense"], "store_logs": True},
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_perspective_node_outputs(test_dag_config, tmp_path):
    """Test perspective node output generation."""
    # Configure multiple output formats
    test_dag_config["nodes"][1]["config"]["output"].update(
        {
            "directory": str(tmp_path),
            "formats": ["formal", "html"],  # Art critic uses formal and html formats
            "copy_images": True,
        }
    )

    # Create and validate DAG
    node_classes = {
        "ImageSamplingNode": "graphcap.io.nodes.image_sampling.ImageSamplingNode",
        "PerspectiveNode": "graphcap.caption.nodes.perspective.PerspectiveNode",
    }
    dag = DAG.from_dict(test_dag_config, node_classes)

    # Add node configurations after creation
    for node_config in test_dag_config["nodes"]:
        if "config" in node_config:
            dag.nodes[node_config["id"]].config = node_config["config"]

    results = await dag.execute()

    # Check output files
    output_dir = Path(results["art_analysis"]["perspective_info"]["output_dir"])
    assert output_dir.exists()

    # Check for art critic specific files
    batch_dir = next(output_dir.glob("batch_*"))  # Get the timestamped batch directory
    assert batch_dir.exists()

    # Check for expected files
    assert (batch_dir / "formal_analysis.txt").exists(), "Should have formal analysis file"
    assert (batch_dir / "art_report.html").exists(), "Should have HTML report"
    assert (batch_dir / "process.log").exists(), "Should have process log"

    # Check image copying
    assert (batch_dir / "images").exists(), "Should have images directory"
    assert any((batch_dir / "images").glob("*.jpg")), "Should have copied images"

    # Verify content
    formal_analysis = (batch_dir / "formal_analysis.txt").read_text()
    assert formal_analysis, "Formal analysis should not be empty"

    html_report = (batch_dir / "art_report.html").read_text()
    assert html_report, "HTML report should not be empty"
