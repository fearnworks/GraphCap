=================================
Op Graphs
=================================

**Op Graphs** in graphcap allow you to compose complex workflows by assembling individual :doc:`Ops <core/concepts/ops>` (or other Op Graphs) into reusable, higher-level units.  Graphs represent interconnected sets of operations, enabling you to build sophisticated image processing pipelines from simpler components.

This section introduces the concept of Op Graphs in graphcap, explaining their purpose, benefits, and how to define and use them to structure your workflows.

Key Concepts
============

- **Composition of Ops:** Op Graphs are built by connecting multiple :doc:`Ops <core/concepts/ops>` (instances of :class:`OpNode`) together.  This composition allows you to create modular and reusable pipeline components.

- **Dependency Wiring:** Within a Graph, you explicitly define the data dependencies between the constituent Ops.  This wiring dictates the execution order and data flow within the Graph.

- **Graph Node: `GraphDefinition`:** Op Graphs are represented by the :class:`GraphDefinition` class in graphcap. This class defines the structure of the graph, including the set of Ops it contains and their interconnections.

- **Reusability and Modularity:** Op Graphs promote modularity and code reuse. You can create graphs for common workflow patterns and then reuse these graphs as components within larger pipelines or other graphs.

- **Abstraction and Organization:** Graphs provide a level of abstraction, allowing you to manage complexity by grouping related Ops into logical units. This makes complex pipelines easier to understand, maintain, and evolve.

Benefits of Using Op Graphs
========================

- **Building Complex Workflows:**  Op Graphs enable you to construct intricate image processing pipelines by composing simpler, focused Ops.

- **Code Reusability:**  Graphs can be reused as components in different pipelines or within other graphs, reducing code duplication and promoting consistency.

- **Improved Organization and Readability:**  Graphs help structure complex pipelines into logical units, making them easier to understand, navigate, and maintain.

- **Abstraction and Encapsulation:**  Graphs encapsulate a set of interconnected operations, hiding the internal complexity and presenting a higher-level interface to users of the graph.

- **Simplified Testing and Debugging:**  By breaking down pipelines into graphs of Ops, you can test and debug individual Ops and Graphs more effectively.

Defining Op Graphs
====================

Op Graphs are defined using the :class:`GraphDefinition` class in graphcap. You create a `GraphDefinition` by providing:

1.  **A Name:** A unique name for the Op Graph.
2.  **A Description (Optional):**  Human-readable documentation for the graph.
3.  **A List of Nodes (Ops):** The :class:`OpNode` instances that constitute the graph.
4.  **Dependencies:** A dictionary that explicitly defines the data dependencies between the Ops within the graph.

.. code-block:: python

    from graphcap.dag.graph_definition import GraphDefinition
    from graphcap.dag.nodes import MyOp1, MyOp2, MyOp3 # Example OpNode classes

    # Instantiate Op nodes
    node1 = MyOp1(id="node_one")
    node2 = MyOp2(id="node_two")
    node3 = MyOp3(id="node_three")

    # Define the Op Graph
    my_graph = GraphDefinition(
        name="my_complex_workflow",
        description="An example graph demonstrating composition of Ops.",
        nodes=[node1, node2, node3], # List of OpNodes
        dependencies={ # Define dependencies between nodes
            "node_two": ["node_one"], # node_two depends on node_one
            "node_three": ["node_two"] # node_three depends on node_two
        }
    )


Using Op Graphs
==================

Once defined, Op Graphs can be used in several ways within graphcap:

- **As Nodes in Larger DAGs:** Op Graphs can be treated as composite nodes and incorporated into larger, more complex DAGs, further promoting modularity.
- **Directly Executed Workflows (Future Enhancement):** In future versions of graphcap, Op Graphs could potentially be executed directly as standalone workflows (similar to Dagster Jobs, though this is not part of the MVP).

Example Use Cases for Op Graphs
==============================

- **Modular Image Analysis Pipelines:**  Create graphs for specific image analysis tasks (e.g., "Scene Graph Generation Graph", "Artistic Style Analysis Graph") and then combine these graphs into more comprehensive pipelines.
- **Reusable Data Transformation Modules:**  Define graphs for common data transformation sequences (e.g., "Preprocessing Graph", "Feature Extraction Graph") and reuse them across different projects.
- **Encapsulating Complex Logic:**  Group a series of related Ops within a Graph to manage complexity and improve the readability of your main DAG definition.

