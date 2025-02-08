# SPDX-License-Identifier: Apache-2.0
"""Type definitions for perspectives assets."""

from typing import Any, Dict, List, TypedDict


class PerspectiveCaptionResult(TypedDict):
    """Type definition for a single perspective caption result."""

    filename: str
    config_name: str
    version: str
    model: str
    provider: str
    parsed: Dict[str, Any]


PerspectiveCaptionOutput = List[PerspectiveCaptionResult]
