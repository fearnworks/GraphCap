# SPDX-License-Identifier: Apache-2.0
"""Assets and ops for basic text captioning."""

from pathlib import Path
from typing import Dict, List

import dagster as dg

from ..common.logging import write_caption_results
from ..common.resources import ProviderConfigFile
from ..perspectives.perspectives import ArtCriticProcessor, GraphCaptionProcessor
from ..providers.clients import (
    BaseClient,
    GeminiClient,
    OllamaClient,
    OpenAIClient,
    OpenRouterClient,
    VLLMClient,
)


@dg.asset(group_name="perspectives", compute_kind="python")
def perspective_list(context: dg.AssetExecutionContext) -> List[str]:
    """List of perspectives."""
    context.log.info("Generating perspective list")
    return ["art_critic", "graph_analysis"]


@dg.asset(group_name="perspectives", compute_kind="graphcap", deps=[perspective_list])
async def perspective_caption(
    context: dg.AssetExecutionContext,
    image_list: List[str],
    perspective_list: List[str],
    provider_config_file: ProviderConfigFile,
    default_provider: str,
) -> Dict[str, str]:
    """Generate captions for selected images."""
    context.log.info("Generating captions")
    context.log.info(f"Image selection: {image_list}")
    context.log.info(f"Perspective: {perspective_list}")

    config_path = provider_config_file.provider_config
    from ..providers.provider_config import get_providers_config

    providers = get_providers_config(config_path)
    selected_provider_config = providers[default_provider]

    # Instantiate the client
    client_args = {
        "name": default_provider,
        "kind": selected_provider_config.kind,
        "environment": selected_provider_config.environment,
        "env_var": selected_provider_config.env_var,
        "base_url": selected_provider_config.base_url,
        "default_model": selected_provider_config.default_model,
    }

    client: BaseClient
    if selected_provider_config.kind == "openai":
        client = OpenAIClient(**client_args)
    elif selected_provider_config.kind == "gemini":
        client = GeminiClient(**client_args)
    elif selected_provider_config.kind == "vllm":
        client = VLLMClient(**client_args)
    elif selected_provider_config.kind == "ollama":
        client = OllamaClient(**client_args)
    elif selected_provider_config.kind == "openrouter":
        client = OpenRouterClient(**client_args)
    else:
        raise ValueError(f"Unknown provider kind: {selected_provider_config.kind}")

    results: Dict[str, str] = {}
    all_results = []
    for perspective in perspective_list:
        if perspective == "art_critic":
            processor = ArtCriticProcessor()
        elif perspective == "graph_analysis":
            processor = GraphCaptionProcessor()
        else:
            context.log.warning(f"Unknown perspective: {perspective}")
            continue

        for image in image_list:
            try:
                # Use the default_provider client to generate the caption
                caption_data = await processor.process_single(client, Path(image))
                results[f"{perspective}_{image}"] = str(caption_data)
                all_results.append({"perspective": perspective, "image": image, "caption_data": caption_data})
            except Exception as e:
                context.log.error(f"Error generating caption for {image} with {perspective}: {e}")
    write_caption_results(all_results)
    metadata = {
        "num_images": len(image_list),
        "perspectives": str(perspective_list),
        "default_provider": default_provider,
        "caption_results_location": "/workspace/logs/gcap_pipelines",
    }
    context.add_output_metadata(metadata)
    return results
