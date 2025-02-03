# DAG Node Development Guide


This guide explains how to create and add new nodes to the GraphCap DAG system.

## Creating a New Node

1. Create a new node class that inherits from `BaseNode`:

```python
from graphcap.dag.node import BaseNode

class MyCustomNode(BaseNode):
    """
    Brief description of what your node does.

    Detailed description of the node's behavior and purpose.
    """

    @classmethod
    def schema(cls) -> Dict[str, Dict[str, Any]]:
        """Define node input schema."""
        return {
            "required": {
                "input_field": {
                    "type": "STRING",
                    "description": "Description of required input",
                },
            },
            "optional": {
                "optional_field": {
                    "type": "INT",
                    "description": "Description of optional input",
                    "default": 42,
                },
            },
        }

    @classmethod
    def outputs(cls) -> Dict[str, Any]:
        """Define node output schema."""
        return {
            "output_field": {
                "type": "DICT",
                "description": "Description of node output",
            },
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute node functionality."""
        # Validate inputs
        self.validate_inputs(**kwargs)

        # Your node logic here
        result = {"output_field": "some result"}

        return result
```

2. Register your node in the appropriate package's `__init__.py`:

```python
from .my_custom_node import MyCustomNode

# Register available node types
NODE_TYPES = {
    "MyCustomNode": MyCustomNode,
}

__all__ = ["MyCustomNode", "NODE_TYPES"]
```

## Using Your Node in a DAG

Add your node to a DAG configuration:

```json
{
  "nodes": [
    {
      "id": "my_node",
      "type": "MyCustomNode",
      "config": {
        "input_field": "required value",
        "optional_field": 100
      },
      "dependencies": ["other_node_id"]
    }
  ]
}
```

## Node Development Guidelines

1. **Input Validation**
   - Define clear schema for inputs
   - Use type hints
   - Validate all inputs before processing

2. **Error Handling**
   - Raise descriptive exceptions
   - Handle expected failure cases
   - Log important events

3. **Documentation**
   - Clear docstrings
   - Input/output descriptions
   - Usage examples

4. **Testing**
   - Unit tests for node logic
   - Integration tests with DAG
   - Test error cases

## Available Node Types

Common node types include:

- `ImageSamplingNode`: Image loading and sampling
- `PerspectiveNode`: Caption generation with different perspectives
- `DAGVisualizerNode`: DAG visualization

## Example Node Categories

1. **Input/Output Nodes**
   - File reading/writing
   - Data loading/saving
   - API connections

2. **Processing Nodes**
   - Data transformation
   - Analysis
   - Filtering

3. **Visualization Nodes**
   - Graph generation
   - Report creation
   - Export formatting

4. **Meta Nodes**
   - DAG visualization
   - Performance monitoring
   - Logging

## Best Practices

1. Keep nodes focused on a single responsibility
2. Use clear, descriptive node and parameter names
3. Provide sensible defaults for optional parameters
4. Include proper error messages and logging
5. Document node behavior and requirements
6. Test with different input combinations
7. Consider node reusability 