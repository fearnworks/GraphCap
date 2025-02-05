"""
# SPDX-License-Identifier: Apache-2.0
Caption Module

This module provides functionality for generating different types of structured captions
for images using vision AI models. It supports multiple caption formats and versions
through a decoupled architecture.

Key features:
- Multiple caption type support (graph, art critic, etc.)
- Shared vision model integration
- Structured data validation
- Configurable prompting system

Caption Types:
    GraphCaption: Structured analysis with tags and descriptions
    ArtCritic: Artistic analysis focusing on composition and technique

Perspectives:
    Perspectives in GraphCap are specialized modules that provide unique analyses.
    Each perspective focuses on different aspects of the image, allowing for comprehensive
    and diverse image analysis.
"""
