# Config Notes 

This folder contains the configuration files for the project.

## VLLM Configs & Key Docs

[VLLM Docker Docs](https://docs.vllm.ai/en/latest/deployment/docker.html)
[VLLM Multimodal Inputs](https://docs.vllm.ai/en/latest/serving/multimodal_inputs.html)
[VLLM Supported Models](https://docs.vllm.ai/en/latest/models/supported_models.html)

It is highly recommended to use multimodal modals with support for the v1 architecture (can be found in the table)

Taskfile.models.yml contains command blueprints for serving models.
./provider_helpers contains helper scripts for certain models.

## Docker Compose

docker compose contains the based docker compose file for running the project.
docker compose overrides contains overrides for the base docker compose file.
