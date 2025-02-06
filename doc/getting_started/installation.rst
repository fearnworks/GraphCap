===========================
Installation Instructions
===========================

This document provides a step-by-step guide to setting up the GraphCap project for development and usage.

Prerequisites
=============

- **Python**: Ensure you have Python 3.8 or later installed.
- **Docker**: Required for running the server and other components.
- **Git**: For cloning the repository.

Setup Instructions
==================

1. **Clone the Repository**

   Clone the GraphCap repository from GitHub:

   .. code-block:: bash

      git clone https://github.com/fearnworks/graphcap.git
      cd graphcap

2. **Set Up the Dev Environment**

   Use the task runner to install all necessary dependencies. You can skip this step if you are not developing the project:

   .. code-block:: bash

      task install

3. **Configure Environment Variables**

   Copy the environment template and configure your environment variables:

   .. code-block:: bash

      cp .env.caption.template .env
      cp ./config/provider.config.toml.example ./config/provider.config.toml
      # Edit .env and provider config to set your API keys and other configurations

4. **Run the Server**

   Start the server using Docker Compose:

   .. code-block:: bash

      task dev:server

Configuration
=============

- **Docker Compose**: The project uses Docker Compose for managing services. You can customize the services by editing `config/docker-compose.override.example.yml` and renaming it to `docker-compose.override.yml`.

- **Provider Configuration**: Configure AI providers in `config/provider.config.toml`. Uncomment and set up the providers you wish to use.

- **Batch Configurations**: Customize batch processing settings in `config/batch_configs/`.

