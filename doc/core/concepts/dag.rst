DAG System Documentation
========================

Overview
--------

The Directed Acyclic Graph (DAG) system in GraphCap provides a flexible framework for building and executing workflows for image processing and analysis. It allows for the definition of nodes and their dependencies, ensuring that tasks are executed in the correct order.

Key Features:
- DAG construction and validation
- Node dependency management
- Asynchronous execution
- Built-in visualization
- Extensible node system

Components
----------

- **DAG**: The main class for managing the graph structure, validating dependencies, and executing nodes.
- **BaseNode**: The base class for all nodes in the DAG, providing a framework for defining node behavior, inputs, and outputs.
- **DAGVisualizerNode**: A node specifically for visualizing the DAG structure and dependencies.

Usage
-----

###Creating a DAG

To create a DAG, instantiate the `DAG` class with a list of nodes. Each node should inherit from `BaseNode` and define its own execution logic.

.. code-block:: python

    from graphcap.dag import DAG, BaseNode

    class MyProcessingNode(BaseNode):
        async def execute(self, **kwargs):
            # Node logic here
            return {"result": "processed"}

    nodes = [
        MyProcessingNode(id="process1"),
        MyProcessingNode(id="process2", dependencies=["process1"])
    ]

    dag = DAG(nodes=nodes)
    dag.validate()

###Executing a DAG

Once the DAG is validated, you can execute it asynchronously. The execution will follow the topological order of the nodes.

.. code-block:: python

    results = await dag.execute()

###Visualizing a DAG

Use the `DAGVisualizerNode` to generate a visualization of the DAG structure.

.. code-block:: python

    visualizer_node = DAGVisualizerNode(id="visualize", dependencies=["process2"])
    dag.add_node(visualizer_node)
    await visualizer_node.execute(dag=dag, output_dir="./visualizations")

Node Development
----------------

To create a new node, inherit from `BaseNode` and implement the `execute` method. Define the input schema and outputs using the `schema` and `outputs` class methods.

.. code-block:: python

    class MyCustomNode(BaseNode):
        @classmethod
        def schema(cls):
            return {
                "required": {"input_data": {"type": "STRING", "description": "Input data"}},
                "optional": {"threshold": {"type": "FLOAT", "default": 0.5}}
            }

        @classmethod
        def outputs(cls):
            return {"output_data": {"type": "STRING", "description": "Processed output"}}

        async def execute(self, **kwargs):
            # Node logic here
            return {"output_data": "result"}

Best Practices
--------------

- **Focus on Single Responsibility**: Each node should perform a single task.
- **Clear Naming**: Use descriptive names for nodes and parameters.
- **Error Handling**: Implement robust error handling and logging.
- **Documentation**: Provide clear docstrings and usage examples for each node.
- **Testing**: Ensure nodes are thoroughly tested with various input scenarios.
