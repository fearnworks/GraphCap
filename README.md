# graphcap
> **SPDX-License-Identifier: Apache-2.0**

![Image](./docs/static/flow.png)

**graphcap** is a work-in-progress repository dedicated to experimenting with **structured outputs** and **scene-based captions** to support open-source dataset generation. By leveraging models capable of producing detailed annotations (including bounding boxes, attributes, relationships, and textual captions), graphcap aims to streamline the creation of rich, shareable metadata for images.

## Key Ideas

- **Structured Image Captions**  
  Generates scene graphs (or detailed JSON-based annotations) to provide a more holistic description of image content.

- **Local or Remote Inference**  
  Designed for flexibility in how models are run (local GPU, cloud-based APIs, or hybrid approaches).

- **Open-Source Collaboration**  
  Focused on community-driven development and data generation, following open standards and licenses.

## Current Status

- **Experimental Code**: The repository is under active development, and many features or interfaces may change frequently.
- **Licensing**: The project is made available under the [Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0), ensuring open collaboration and usage.

## Background

Original RFC : [link](https://github.com/Open-Model-Initiative/OMI-Data-Pipeline/issues/134)

## Architecture

GraphCap is organized into three main components that work together to provide a complete dataset generation and management solution:

1. **GraphCap Library (`graphcap`)**
   - Core Library: Fundamental utilities and shared functionality
   - CLI: Command-line interface for direct interactions
   - DAG: Directed Acyclic Graph implementation for pipeline workflows
   - Nodes: Processing components for the pipeline
   - Stateless: Pure functional components for data transformation

2. **Server Component (`server`)**
   - REST API: HTTP interface for remote interactions
   - Orchestration: Manages workflow execution and resource allocation
   - Stateful Services: Maintains system state and session management
   - Tool Servers: Specialized services for specific processing tasks

3. **Core UI Component (`core ui`)**
   - Dataset Management: Interface for organizing and viewing datasets
   - Pipeline Management: Tools for creating and monitoring workflows
   - Configuration: System settings and pipeline configuration tools

### Development Flow

- Developers can contribute to both PyPI packages and Docker images
- Components are published to PyPI Registry for Python package distribution
- Docker images are stored in a central Docker image repository
- The system integrates with Agentic Systems for AI-powered processing

### Integration

- The server component uses the GraphCap library for core functionality
- The UI communicates with the server through a client/server relationship
- Users interact primarily through the UI, while developers can access all components directly
