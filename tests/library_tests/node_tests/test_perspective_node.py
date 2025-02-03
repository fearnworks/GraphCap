"""
# SPDX-License-Identifier: Apache-2.0
graphcap.tests.lib.node_tests.test_perspective_node

Integration tests for perspective node functionality.

Key features:
- Art analysis perspective testing
- Provider integration verification
- Output format validation
- Node configuration handling
- Error handling and validation

Classes:
    None (contains test functions only)
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
    assert "perspective_results" in perspective_result

    # Check perspective results structure
    results_data = perspective_result["perspective_results"]
    assert "formal" in results_data
    assert "html" in results_data
    assert "image_path" in results_data

    # Check formal analysis content
    assert "content" in results_data["formal"]
    assert "filename" in results_data["formal"]
    assert results_data["formal"]["filename"] == "formal_analysis.txt"

    # Check HTML report
    assert "content" in results_data["html"]
    assert "filename" in results_data["html"]
    assert results_data["html"]["filename"] == "art_report.html"


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

    # Execute DAG and wait for completion
    try:
        results = await dag.execute()
    except Exception as e:
        pytest.fail(f"DAG execution failed: {str(e)}")

    # Verify art analysis results
    assert "art_analysis" in results, "Art analysis results should be present"
    art_results = results["art_analysis"]["perspective_results"]

    # Check formal analysis
    assert "formal" in art_results, "Formal analysis should be present"
    formal = art_results["formal"]
    assert "filename" in formal, "Formal analysis should have filename"
    assert "content" in formal, "Formal analysis should have content"
    assert formal["content"], "Formal analysis content should not be empty"
    assert formal["filename"] == "formal_analysis.txt"

    # Check HTML report
    assert "html" in art_results, "HTML report should be present"
    html = art_results["html"]
    assert "filename" in html, "HTML report should have filename"
    assert "content" in html, "HTML report should have content"
    assert html["filename"] == "art_report.html"

    # Check image path
    assert "image_path" in art_results, "Image path should be present"
    assert art_results["image_path"], "Image path should not be empty"

    # Print results for verification
    print("\nFormal Analysis Content:")
    print(formal["content"][:200] + "...")
    print(f"\nHTML Report Size: {len(html['content'])} bytes")
