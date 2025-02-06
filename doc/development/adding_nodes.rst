Adding New Nodes to the graphcap DAG System
============================================

Overview
--------
graphcap utilizes a directed acyclic graph (DAG) to manage data processing and analysis workflows.
Nodes are the building blocks of the DAG. Each node encapsulates a single responsibility—processing, transformation, visualization, etc.
This guide outlines the steps to add a new node, register it within the system, and implement integration tests to ensure proper functionality.

Prerequisites
-------------
Before creating a new node, ensure that you are familiar with:

- The overall DAG architecture and workflow management in GraphCap.
- The node interface as defined in ``lib/graphcap/dag/node.py`` (the ``BaseNode`` class).
- Existing node implementations in the ``lib/graphcap/dag/nodes/`` directory.
- Python 3.11+ standards, strong typing, and project coding style.

Step 1: Create Your Node Implementation
-----------------------------------------
1. Create a new node class by inheriting from ``BaseNode``. Implement the required methods:

   - Override the ``schema()`` to define input configurations.
   - Override the ``outputs()`` to specify output types.
   - Implement the asynchronous ``execute()`` method containing your node logic.

For example:

.. code-block:: python

    from graphcap.dag.node import BaseNode
    from typing import Any, Dict, List, Optional

    class MyCustomNode(BaseNode):
        """
        MyCustomNode

        This node performs a custom data transformation.
        """

        @classmethod
        def schema(cls) -> Dict[str, Dict[str, Any]]:
            return {
                "required": {
                    "input_param": {
                        "type": "STRING",
                        "description": "A required input parameter.",
                    },
                },
                "optional": {
                    "multiplier": {
                        "type": "INT",
                        "description": "Multiplier for data processing.",
                        "default": 1,
                    },
                },
            }

        @classmethod
        def outputs(cls) -> Dict[str, Any]:
            return {
                "result": {
                    "type": "DICT",
                    "description": "Output data after processing.",
                },
            }

        async def execute(self, **kwargs) -> Dict[str, Any]:
            # Validate inputs based on schema
            self.validate_inputs(**kwargs)
            input_value = kwargs["input_param"]
            multiplier = kwargs.get("multiplier", 1)

            # Implement your node logic here
            processed = {"result": f"Processed {input_value} with multiplier {multiplier}"}
            return processed

Step 2: Register the New Node
------------------------------
To make your new node available to the DAG system, register it in the node index.

1. Open ``lib/graphcap/node_index.py``.
2. Add an entry mapping your node's type name to the class.

For example, update the mapping as shown below:

.. code-block:: python

    NODE_CLASS_MAPPINGS = {
        "ImageSamplingNode": ImageSamplingNode,
        "PerspectiveNode": PerspectiveNode,
        "PerspectiveOutputNode": PerspectiveOutputNode,
        "DAGVisualizerNode": DAGVisualizerNode,
        "DatasetExportNode": DatasetExportNode,
        "CopyImagesNode": CopyImagesNode,
        # Register your new node type below
        "MyCustomNode": MyCustomNode,
    }

Step 3: Add Integration Tests
-----------------------------
Integration tests help ensure that your node behaves correctly within the DAG.

1. Create a test file in the ``tests/library_tests/node_tests/`` directory (for example, ``test_my_custom_node.py``).
2. Write tests that:

   * Validate the node's schema enforcement.
   * Check correct node execution under expected input conditions.
   * Verify error handling in case of missing or invalid inputs.

Example test snippet:

.. code-block:: python

    import pytest
    from graphcap.dag.dag import DAG
    from my_project.custom_nodes.my_custom_node import MyCustomNode

    @pytest.mark.asyncio
    async def test_my_custom_node_execution():
        # Create an instance of your node with required properties
        node = MyCustomNode(id="custom1")
        # Validate that providing the required parameter returns expected result
        result = await node.execute(input_param="test", multiplier=2)
        expected = "Processed test with multiplier 2"
        assert result["result"] == expected

    def test_schema_validation():
        node = MyCustomNode(id="custom1")
        # Omitting the required 'input_param' should raise a ValueError
        with pytest.raises(ValueError, match="Missing required parameter: input_param"):
            node.validate_inputs(multiplier=2)

Step 4: Update Batch Configurations (if applicable)
----------------------------------------------------
If your new node is part of a batch process or integrates with existing batch workflows, add or update sample configuration files in ``config/batch_configs/``.

For example, add a section in a sample TOML configuration (e.g., :file:`config/batch_configs/example_config.toml`) to include your node:
   
.. code-block:: toml

    [nodes.my_custom_node]
    type = "MyCustomNode"
    input_param = "sample input"
    multiplier = 3

Additional Considerations
-------------------------
- **Documentation:** Update related documentation (in :file:`lib/graphcap/dag/README.md` or in your node file's docstring) to describe the new node's functionality.
- **Error Handling:** Ensure that your node handles invalid input gracefully and provides clear error messages.
- **Consistency:** Follow the established coding style and testing practices used throughout the graphcap project.

Conclusion
----------
By following this guide, you can add a new node to the graphcap DAG system while ensuring consistency with existing project standards. Be sure to run your integration tests and update any related batch configurations to reflect your changes.

Happy coding!
