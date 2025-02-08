# SPDX-License-Identifier: Apache-2.0
"""Assets and ops for basic text captioning."""

from typing import Dict, List

import dagster as dg


@dg.asset(group_name="perspectives", compute_kind="python")
def perspective_list(context: dg.AssetExecutionContext) -> List[str]:
    """List of perspectives."""
    context.log.info("Generating perspective list")
    return ["art_critic", "graph_analysis"]


@dg.asset(name="vision_provider")
def vision_provider(context: dg.AssetExecutionContext) -> Dict[str, str]:
    """Vision provider."""
    context.log.info("Generating vision provider")
    return {"graphcap_provider": "graphcap_provider"}


@dg.asset(group_name="perspectives", compute_kind="graphcap", deps=[perspective_list, vision_provider])
def perspective_caption(
    context: dg.AssetExecutionContext,
    image_list: List[str],
    vision_provider: Dict[str, str],
    perspective_list: List[str],
) -> Dict[str, str]:
    """Generate captions for selected images."""
    context.log.info("Generating captions")
    context.log.info(f"Image selection: {image_list}")
    context.log.info(f"Provider selection: {vision_provider}")
    context.log.info(f"Perspective: {perspective_list}")
    # Implementation here
    return {}
