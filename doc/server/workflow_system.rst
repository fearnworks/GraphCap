============================================
Workflow and Job Management System
============================================

Overview
--------
The GraphCap orchestration server includes a robust workflow and job management system to facilitate the execution of image processing pipelines. 
Workflows are defined as Directed Acyclic Graphs (DAGs) and are stored as JSON configuration files. 
These definitions are then loaded, validated, and persisted in a PostgreSQL database.
 In parallel, a job manager oversees the asynchronous execution of these workflows.

Workflow Definition and Loading
---------------------------------
- **JSON-Based Configurations:**  
  Workflows are defined in JSON files located in the `/workspace/config/workflows` directory. Each file contains a list of nodes and their dependencies.
  
- **Version Tracking:**  
  A hash is computed for each workflow file. This hash is stored along with the workflow information in the database, which helps in detecting updates and managing versions.
  
- **Schema Validation:**  
  Before execution, each workflow is validated to ensure it contains the required structure (e.g., a `nodes` key) and adheres to the expected format.

Workflow Execution and Job Management
---------------------------------------
- **Job Creation:**  
  When a workflow is triggered, it is executed as a job. The job encapsulates the entire workflow configuration and maintains its current state.
  
- **Asynchronous Execution:**  
  Workflows are executed asynchronously using the GraphCap DAG system. After validation, the DAG representing the workflow is executed, and the output is processed for job completion.
  
- **Status Tracking:**  
  The job manager tracks each job's lifecycle—including start, progress, and completion. API endpoints enable clients to query and update job status.

API Endpoints and Integration
-----------------------------
The server integrates workflow and job management through RESTful endpoints:
- **CRUD Operations for Workflows:**  
  Endpoints allow creation, listing, retrieval, and updates of workflow configurations.
  
- **Triggering Workflows:**  
  A dedicated endpoint initiates workflow execution, which in turn creates a job managed asynchronously.
  
- **Job Status Feedback:**  
  Clients can fetch the current state of a job, making it easy to monitor workflow execution in real time.

