======================================
Workspace Concept Overview
======================================

Overview
--------
The graphcap system uses the concept of a "workspace" to organize and manage various runtime assets and configuration files in a centralized manner. 
The workspace is implemented as a mounted volume that brings essential directories from the host system into the running container. 
This design allows for persistent storage, hot reloading of changes, and easy management of configuration data and datasets.

Directory Structure
---------------------
Within the workspace, several key directories are mounted:

- **config:**  

- **.local:**  
  Stores local state, logs, and cache data to persist runtime information across container restarts.

- **datasets:**  
  Serves as the working area for datasets, including both example data and user-provided files used in processing pipelines.

These directories are brought into the container as defined in the Docker Compose configuration. For example, the volume mounts in ``config/docker-compose.yml`` include:

.. code-block:: yaml

    volumes:
      - ../config:/workspace/config
      - ../.local:/workspace/.local
      - ../datasets:/workspace/datasets

Benefits and Usage
------------------
- **Hot Reloading:**  
  Any changes made to files or configurations on the host are instantly reflected inside the container, streamlining the development and debugging process.

- **Data Persistence:**  
  By separating configuration and dataset storage from the container's ephemeral filesystem, your data remains intact even if the container is restarted or updated.

- **Simplified Management:**  
  With a dedicated workspace, managing configuration files, local state, and datasets becomes more intuitive, helping to keep deployment and maintenance processes organized.

