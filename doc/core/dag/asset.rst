.. SPDX-License-Identifier: Apache-2.0
.. graphcap.module.doc.core.concepts.assets

=================================
Assets
=================================

**Assets** are the fundamental data objects managed within graphcap. They represent the tangible outputs of your image processing pipelines, such as datasets, structured captions, and analysis reports.  
Think of them as the valuable pieces of data that your graphcap system is designed to create, refine, and manage.
This section introduces the concept of assets in graphcap, explaining their definition, key characteristics, and benefits within the system.

Key Concepts
============

- **Asset Definition:** An asset in graphcap is defined through code, specifying its name, how it is produced, and its relationships to other assets. This definition serves as the blueprint for the data object within the graphcap system.

- **Asset Key (Name):**  Each asset in graphcap is uniquely identified by a name, often referred to as its *asset key*. This name is used to reference the asset throughout the graphcap system, especially when defining dependencies and tracking lineage.

- **Data Production by Nodes:** Assets are *produced* or *materialized* by nodes within a graphcap DAG.  A node responsible for creating an asset contains the code and logic required to compute and generate the asset's data.

- **Persistent Data Representation:**  While the details of persistence are handled by specific nodes (like output nodes), assets conceptually represent data that is stored persistently. This could be in the form of files on disk, entries in a dataset, or structured data in a database (future enhancement).

- **Dependencies on Other Assets:**  Assets in graphcap can depend on other assets. These dependencies are defined within the DAG structure, creating a clear lineage of data transformations. When an asset depends on another, it means that the upstream asset must be successfully processed before the downstream asset can be computed.

Benefits of Using Assets
========================

- **Data-Centric Workflow Orchestration:**  Assets shift the focus of graphcap workflows from just executing tasks to managing and understanding the flow of data.  The DAG becomes a representation of how data assets are transformed and related.

- **Organized and Discoverable Outputs:** By defining assets, graphcap provides a structured way to organize and manage the various outputs of your image processing pipelines. Assets become discoverable and manageable entities within the system.

- **Clear Data Lineage and Dependency Tracking:**  Asset dependencies within the DAG provide a clear and auditable lineage of how data is derived. You can easily trace back the source of any asset and understand its upstream data dependencies.

- **Declarative Pipeline Design:** Defining assets promotes a more declarative approach to pipeline design. Instead of focusing solely on the sequence of operations, you define *what* data assets you want to produce and *how* they relate to each other.

Conceptual Example
====================

Imagine a graphcap pipeline designed to generate scene graphs from images.  A conceptual asset in this pipeline could be:

**"Processed Images Dataset"**:

- **Definition:**  Defined by a node (`DatasetExportNode` for example) that takes structured caption outputs and formats them into a shareable dataset.
- **Key:**  `processed_images_dataset`
- **Production:**  Produced by the `DatasetExportNode`, which aggregates outputs from `PerspectiveOutputNode` instances.
- **Dependencies:** Depends on assets produced by `PerspectiveOutputNode` nodes (e.g., "Graph Captions", "Art Critic Reports").

This "Processed Images Dataset" asset would represent the final, shareable dataset output of the graphcap pipeline. Users could then interact with this asset, track its lineage, and understand its properties within the graphcap system.
