.. SPDX-License-Identifier: Apache-2.0
.. graphcap.module.doc.overview

=================================
Overview
=================================

graphcap is a platform that leverages advanced vision and language models to generate graph structures from multimodal data.
 It is designed to support structured outputs that provide detailed image annotations, scene graphs, and rich metadata for open-source datasets.

Overview
--------
graphcap is composed of several core components:

- **graphcap Library**  
  The core Python library provides utilities for constructing Directed Acyclic Graphs (DAGs) to orchestrate image processing workflows, manage nodes, and generate structured captions.

- **Server Component**  
  A FastAPI-based orchestration server that manages workflow execution, job management, and resource allocation. It enables both local and remote inference and integrates with the graphcap library for core functionalities.

- **UI Component**  
  A web-based interface for managing datasets, configuring pipelines, and visually monitoring workflow progress and outputs.

Key Features
------------
- **Structured Image Captions**:  
  Generate detailed scene graphs and JSON-based annotations for comprehensive image analysis.

- **Flexible Inference Options**:  
  Support for both local GPU and cloud-based inference, providing adaptability to various deployment environments.

- **Workflow Orchestration**:  
  Utilize a robust DAG system to define, validate, and execute complex image processing pipelines.

- **Modular Architecture**:  
  Seamlessly integrate the library, server, and UI components to ensure scalability and ease of maintenance.

Getting Started
---------------
To get up and running with GraphCap, review the respective sections of the documentation:

- Installation and project setup using modern Python packaging with Hatchling.
- Running the server component via Docker Compose or task runner commands.
- Building and executing workflows for image captioning and dataset generation.

