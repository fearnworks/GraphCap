=================================
Ops
=================================

**Ops** are the fundamental computational units within graphcap pipelines. They represent individual steps in your image processing workflows, responsible for performing specific tasks like data transformation, analysis, or calling external services.

This section introduces the concept of Ops in graphcap, explaining their purpose, key features, and how to define and use them within your DAGs.

Key Concepts
============

- **Computational Units:** Ops are the building blocks of graphcap pipelines. Each Op encapsulates a distinct piece of computation, designed to perform a specific task.

- **Node Type: `OpNode`:** In graphcap, Ops are implemented as subclasses of the :class:`OpNode` class (or a similarly named class you choose), which inherits from the base :class:`BaseNode`.  This class provides the structure and interface for defining Ops within your DAGs.

- **`execute` Method:** The core logic of an Op is implemented in its `execute` method. This method contains the Python code that performs the actual computation, data transformation, or analysis that the Op is designed for.

- **Inputs and Outputs (Simplified):**  Ops in graphcap receive inputs implicitly through the :class:`NodeExecutionContext` object passed to their `execute` method.  Outputs are dictionaries returned by the `execute` method. (In this MVP, input/output definitions are simplified compared to Dagster, focusing on kwargs and structured return dictionaries).

- **Configuration (Optional):** Ops can be configured using Pydantic models defined via the ``@config_class`` decorator. This allows you to parameterize Op behavior and adjust settings at runtime.

- **Decorators for Definition:**  Ops are typically defined using the ``@op_node`` decorator (or a similar decorator name you choose), which simplifies the process of creating OpNode classes and registering them with the graphcap system.


Typical Op Tasks
=================

Ops in graphcap are designed to perform relatively simple, focused tasks within an image processing pipeline. Examples of typical Op tasks include:

- **Data Transformation:**  Resizing images, converting image formats, applying filters, or augmenting image datasets.
- **Image Analysis:** Running image recognition models, feature extraction, or generating image embeddings.
- **Caption Generation (Perspective Execution):** Executing specific captioning perspectives (like "ArtCritic" or "GraphCaption") on a batch of images.
- **Data Aggregation and Summarization:**  Aggregating caption results, generating dataset statistics, or creating summary reports.
- **Visualization:** Generating visualizations of DAG structures or analysis results.
- **Calling External Services:** Interacting with APIs for model inference, data storage, or external data sources.


Defining Ops
============

Ops are defined as Python classes that inherit from :class:`OpNode` and are decorated with the ``@op_node`` decorator. The core logic is implemented in the ``execute`` method.

.. code-block:: python

    from graphcap.dag.node import BaseNode
    from graphcap.dag.decorators import op_node
    from graphcap.dag.node import NodeExecutionContext
    from typing import Dict, Any

    @op_node
    class ImageResizeOp(BaseNode): # Define an Op by inheriting from OpNode and using @op_node decorator
        \"\"\"
        Resizes images to a specified size.
        \"\"\"

        async def execute(self, context: NodeExecutionContext) -> Dict[str, Any]:
            \"\"\"
            Executes the image resizing operation.

            Args:
                context (NodeExecutionContext): The execution context for the node.

            Returns:
                Dict[str, Any]: A dictionary containing information about the resized images (e.g., paths to resized images).
            \"\"\"
            context.log_info(f"Executing image resize operation for node: {self.id}")
            # ... (Image resizing logic here, using context to access inputs if needed) ...
            resized_image_paths = [...] # (example output)
            return {"resized_images": resized_image_paths}


Using Ops in DAGs
==================

Once defined, Ops are instantiated and added to a graphcap DAG as nodes.  Dependencies between Ops are defined when constructing the DAG, ensuring that Ops are executed in the correct order.

.. code-block:: python

    from graphcap.dag.dag import DAG
    # ... (Import ImageResizeOp and other nodes) ...

    resize_node = ImageResizeOp(id="resize_images") # Instantiate the Op
    # ... (Other node instantiations) ...


    nodes = [
        resize_node,
        # ... (Other nodes) ...
    ]

    dag = DAG(nodes=nodes) # Create DAG with Op nodes
    dag.validate()
    results = await dag.execute() # Execute the DAG

