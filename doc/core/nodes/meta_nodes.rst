====================
DAG Meta Nodes
====================

Overview
========
Meta nodes in the GraphCap DAG package extend the basic node functionality with enhancements that help visualize and analyze the workflow structure. They are designed to support tasks such as:

- Visualizing the overall DAG structure.
- Analyzing node dependencies and execution order.
- Monitoring and logging workflow performance.

These capabilities offer developers and administrators better insights into the execution and design of complex pipelines.

DAGVisualizerNode
=================
The primary meta node is the ``DAGVisualizerNode``. This node generates visual representations of the DAG, helping to quickly comprehend node dependencies and workflow hierarchies.

**Purpose:**
- Render the DAG as an image in various formats (e.g., PNG, PDF, SVG).
- Illustrate node interdependencies and depict execution order using standard graph layouts.
- Allow custom styling via configuration parameters such as node size, color, and positional layout.

**Usage Example:**
Below is an example of how to integrate the ``DAGVisualizerNode`` into a workflow for visualizing a simple DAG.

.. code-block:: python

    from graphcap.dag import DAG, NODE_TYPES
    from graphcap.dag.nodes.meta import DAGVisualizerNode
    from graphcap.dag.node import BaseNode
    import asyncio

    # Define a dummy node for demonstration purposes
    class DummyNode(BaseNode):
        @classmethod
        def schema(cls) -> dict:
            return {"required": {}, "optional": {}}

        @property
        def outputs(self) -> dict:
            return {}

        async def execute(self, **kwargs) -> dict:
            return {}

    # Create dummy nodes
    node1 = DummyNode(id="node1")
    node2 = DummyNode(id="node2", dependencies=["node1"])

    # Instantiate the meta node for visualization
    visualizer = DAGVisualizerNode(id="viz", dependencies=["node1", "node2"])

    # Build the DAG and add nodes
    nodes = [node1, node2, visualizer]
    dag = DAG(nodes=nodes)
    dag.validate()

    # Execute the visualization node asynchronously
    async def main():
        output = await visualizer.execute(
            dag=dag,
            output_dir="./dag_visualizations",
            format="png",
            style={
                "width": 12,
                "height": 8,
                "node_color": "#E6F3FF",
                "node_size": 3000,
                "edge_color": "#666666",
                "font_size": 10,
                "arrows": True,
                "arrowsize": 20
            },
            timestamp="20231101_latest"
        )
        print("Visualization output:", output)

    asyncio.run(main())

