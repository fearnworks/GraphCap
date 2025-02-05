===================================
Orchestration Server Overview
===================================

Overview
--------
The GraphCap orchestration server is a FastAPI-based service that manages the execution and coordination of image processing and captioning pipelines. It provides the API endpoints for task orchestration, dataset management, and workflow execution. Designed with modern Python standards (>3.11), the server leverages asynchronous operations to ensure high performance and scalability.

Key Features
------------
- **FastAPI Framework:**  
  Built on FastAPI, the server supports asynchronous request handling, automatic API documentation, and efficient routing.
  
- **Docker Containerization:**  
  The server is fully containerized and deployed using Docker. This ensures consistency between development and production environments.
  
- **Volume Mounting and Hot Reloading:**  
  Key directories such as `lib/graphcap`, `server`, and `config` are mounted into the container for seamless code updates and rapid development iterations.
  
- **Database Integration:**  
  The server connects to a PostgreSQL database (defined as `gcap_postgres` in Docker Compose) for persistent storage of configurations, metadata, and workflow states.
  
- **Configurable Environment:**  
  Environment variables are specified via external `.env` files (with a template available as `server/.env.local.template`), making it easy to adjust settings such as database URLs, paths, and debug options.

Docker Compose Deployment
-------------------------
The orchestration server is orchestrated together with its dependencies (e.g., PostgreSQL) using Docker Compose. The main configuration is defined in `config/docker-compose.yml`. For example, the service configuration for the server is as follows:

.. code-block:: yaml

    services:
      gcap_server:
        container_name: gcap_server
        build:
          context: ../
          dockerfile: server/Dockerfile.server
        ports:
          - "32100:32100"
        volumes:
          - ./provider.config.toml:/app/server/provider.config.toml
          - ../lib/graphcap:/app/lib/graphcap
          - ../lib/pyproject.toml:/app/lib/pyproject.toml
          - ../server:/app/server
          - ../pyproject.toml:/app/pyproject.toml
          - ../config:/workspace/config
          - ../.local:/workspace/.local
          - ../datasets:/workspace/datasets
        environment:
          - HOST_PLATFORM=${HOST_PLATFORM:-linux}
          - PYTHONPATH=/app/server
          - DATABASE_URL=postgresql+asyncpg://graphcap:graphcap@gcap_postgres:5432/graphcap
        env_file:
          - ../.env
        networks:
          - graphcap
        depends_on:
          gcap_postgres:
            condition: service_healthy

Deployment and Usage
--------------------
To launch the orchestration server and all of its required services, run the following command from the project's root directory:

.. code-block:: bash

    docker-compose -f config/docker-compose.yml up --build
    # or 
    task dev:server

This command builds the server image (using `server/Dockerfile.server`), starts the PostgreSQL database, and mounts necessary volumes for code, configuration, and datasets. The server is then accessible on port 32100.
