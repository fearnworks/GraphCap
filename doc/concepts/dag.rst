DAG System Documentation
========================

The Directed Acyclic Graph (DAG) system in GraphCap provides a flexible framework for building and executing workflows for image processing and analysis. This system allows for the construction, validation, and execution of DAGs with support for asynchronous operations and built-in visualization capabilities.

Key Features
------------
- **DAG Construction and Validation**: Easily create and validate DAGs with node dependency management.
- **Asynchronous Execution**: Execute workflows asynchronously to improve performance and scalability.
- **Built-in Visualization**: Visualize DAG structures and dependencies using built-in nodes.
- **Extensible Node System**: Create custom nodes to extend the functionality of the DAG system.

Components
----------
- **DAG**: The main class for managing the workflow, including node addition, validation, and execution.
- **BaseNode**: The base class for all nodes, providing a framework for defining node behavior and execution.
- **DAGVisualizerNode**: A node for generating visualizations of the DAG structure.

Usage Example
-------------
Here's a basic example of how to create and execute a DAG:

```python
from graphcap.dag import DAG, BaseNode

# Define custom nodes
class MyProcessingNode(BaseNode):
    async def execute(self, **kwargs):
        # Node logic here
        return {"result": "processed"}

class MyOutputNode(BaseNode):
    async def execute(self, **kwargs):
        # Output logic here
        return {"output": "completed"}

# Create nodes
nodes = [
    MyProcessingNode(id="process1"),
    MyOutputNode(id="output1", dependencies=["process1"])
]

# Create and validate DAG
dag = DAG(nodes=nodes)
dag.validate()

# Execute workflow
results = await dag.execute()
```

Node Development Guidelines
---------------------------
1. **Input Validation**: Define clear schemas for inputs and validate them before processing.
2. **Error Handling**: Raise descriptive exceptions and handle expected failure cases.
3. **Documentation**: Provide clear docstrings and input/output descriptions.
4. **Testing**: Implement unit tests for node logic and integration tests with the DAG.

Available Node Types
--------------------
- **ImageSamplingNode**: For image loading and sampling.
- **PerspectiveNode**: For caption generation with different perspectives.
- **DAGVisualizerNode**: For visualizing the DAG structure.

Example Node Categories
-----------------------
1. **Input/Output Nodes**: Handle file reading/writing and data loading/saving.
2. **Processing Nodes**: Perform data transformation, analysis, and filtering.
3. **Visualization Nodes**: Generate graphs, create reports, and format exports.
4. **Meta Nodes**: Visualize DAGs, monitor performance, and log activities.

Best Practices
--------------
1. Keep nodes focused on a single responsibility.
2. Use clear, descriptive names for nodes and parameters.
3. Provide sensible defaults for optional parameters.
4. Include proper error messages and logging.
5. Document node behavior and requirements.
6. Test with different input combinations.
7. Consider node reusability.
