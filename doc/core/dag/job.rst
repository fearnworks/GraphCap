=================================
Jobs
=================================

**Jobs** are the primary unit of execution and monitoring in graphcap. They represent runnable workflows composed of a :doc:`DAG <core/concepts/dag>` of interconnected :doc:`Ops <core/concepts/ops>`.  Jobs allow you to launch and manage the execution of your image processing pipelines within the graphcap system.

This section introduces the concept of Jobs in graphcap, explaining their purpose, benefits, and how to define and execute them.

Key Concepts
============

- **Runnable Workflows:** Jobs are the top-level entities that you *run* in graphcap.  Each Job encapsulates a complete image processing workflow defined by a DAG.

- **DAG Encapsulation:** A Job *contains* a :doc:`DAG <core/concepts/dag>`. The DAG defines the structure and logic of the workflow, while the Job provides the runnable container for that DAG.

- **Unit of Execution and Monitoring:**  Jobs are the units of execution that graphcap tracks and monitors. When you launch a Job, graphcap creates a *run* to execute the underlying DAG.  You can monitor the progress and results of these runs.

- **Launching Runs:** Jobs can be launched programmatically (via Python code) or, in future versions of graphcap, potentially through a UI or other interfaces.

Benefits of Using Jobs
========================

- **Clear Execution Boundary:** Jobs provide a clear boundary for executing and managing workflows. They define a distinct unit of work within graphcap.

- **Runnable and Executable DAGs:** Jobs make DAGs executable and runnable. They provide the entry point for triggering the execution of a defined workflow.

- **Centralized Monitoring (Future Enhancement):** In future versions of graphcap, Jobs will be the central point for monitoring workflow execution, tracking progress, and viewing results.

- **Workflow Automation (Future Enhancement):** Jobs can be integrated with scheduling and triggering mechanisms (future enhancements) to automate pipeline execution based on time or external events.

Defining Jobs
=============

Jobs are defined using the :class:`JobDefinition` class in graphcap. You create a `JobDefinition` by providing:

1.  **A Name:** A unique name for the Job.
2.  **A DAG Instance:**  The :class:`DAG <core/concepts/dag>` instance that the Job will execute.
3.  **A Description (Optional):** Human-readable documentation for the Job.
4.  **Tags and Metadata (Optional):**  Tags and metadata for organization and information.

.. code-block:: python

    from graphcap.dag.job_definition import JobDefinition
    from graphcap.dag.dag import DAG
    # ... (Import your DAG and nodes) ...

    # Assume you have a DAG instance named 'my_image_pipeline_dag'
    # ...

    # Define the Job
    my_image_processing_job = JobDefinition(
        name="image_processing_job_batch_1",
        description="Job to run the main image processing pipeline for batch 1.",
        dag=my_image_pipeline_dag, # Associate the DAG with the Job
        tags={"release": "v1.0", "data_batch": "batch_1"},
        metadata={"author": "data_team", "priority": "high"}
    )


Executing Jobs
==============

Jobs are executed by calling their `execute` method.  For the MVP, execution is primarily programmatic.

.. code-block:: python

    # ... (Assume you have a JobDefinition instance named 'my_image_processing_job') ...

    results = await my_image_processing_job.execute() # Execute the Job
    # Process the results (dictionary of node results)
    print(results)
