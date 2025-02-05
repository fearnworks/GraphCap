Release and Packaging Architecture
==================================

Overview
--------

GraphCap uses modern Python packaging tools and practices to manage dependencies, testing, and distribution. The project is structured as a workspace with multiple components:

- `graphcap` - Core library package
- `server` - FastAPI server package
- Additional workspace components (UI, etc.)

1. Build System
---------------

1.1 Build Backend
~~~~~~~~~~~~~~~~~

We use Hatchling as our build backend for its modern features and extensibility:

.. code-block:: toml

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

1.2 Project Structure
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text
    .cursor/rules/               # Context store for software agents
    .github/workflows/           # GitHub Actions workflows
    .venv/                      # Root local environment spawned by uv
    .env.caption.template       # Template for environment variables used in testing
    config/                     # Configuration directory
    ├── docker-compose.yml              # Base docker compose config
    ├── docker-compose.override.example.yml  # Override file example (copied w/ remove of .example)
    ├── provider.example.config.toml    # Provider configuration example for inference providers
    ├── Taskfile.models.yml            # Commands for example cookbook models
    └── batch_configs/                 # Default configurations and workflows
        
    datasets/                   # Working area for datasets, includes examples
    docs/                      # Project Documentation
    lib/graphcap/              # Main graphcap library
    pyproject.toml             # Project dependencies and build configuration


    server/                    # Server submodule
    ├── Dockerfile.server      # Build image for server
    └── pyproject.toml         # Server-specific dependencies

    tests/                     # Test suite
    ├── README.md              # Test documentation and guidelines
    ├── .gitignore            # Test-specific ignore rules
    ├── artifacts/            # Test artifacts and fixtures
    │   ├── dag_configs/      # DAG configuration test files
    │   ├── provider/         # Provider test configurations
    │   └── test_dataset/     # Test dataset files
    ├── conftest.py           # pytest configuration and fixtures
    ├── library_tests/        # Library component tests
    │   ├── node_tests/       # Node functionality tests
    │   └── provider_tests/   # Provider integration tests
    └── server_tests/         # Server integration tests

    Taskfile.yml              # Task runner configuration
    README.md                 # Project overview and documentation

2. CI/CD Workflows
------------------

The project uses GitHub Actions for continuous integration and deployment with three current workflows:

2.1 Library CI (`library-ci.yml`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This workflow handles the core library package quality checks:

- **Trigger**: Runs on pushes/PRs to `main` and `ci` branches that modify library code, tests, or package configs
- **Jobs**:
  - `lint`: Runs Ruff for code style and quality checks
  - `test`: Executes library unit tests using pytest (excluding integration and server tests)

2.2 PyPI Release (`pypi-publish.yml`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manages the publication of library releases to PyPI:

- **Trigger**: Runs when a new GitHub release is published or manually
- **Jobs**:
  - `verify`: Runs test suite to validate release
  - `publish`: Builds and publishes package to PyPI using build and twine

2.3 Server CI/CD (`server-build.yml`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handles the FastAPI server component testing and deployment:

- **Trigger**: Runs on pushes to `main`, `dev`, `feature/*`, and `ci` branches that modify server code or on version tags
- **Jobs**:
  - `lint`: Runs Ruff checks on server code
  - `test`: Executes server-specific tests
  - `deploy`: Builds and pushes Docker image to GitHub Container Registry (ghcr.io)

2.4 Documentation (`documentation.yml`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Builds and deploys the documentation to GitHub Pages:

- **Trigger**: Runs on pushes, pull requests, and manual dispatch
- **Jobs**:
  - `docs`: Builds the documentation using Sphinx and deploys it to GitHub Pages
