# SPDX-License-Identifier: Apache-2.0
from enum import StrEnum
from typing import List

from pydantic import BaseModel, Field


class TagType(StrEnum):
    ENTITY = "Entity"
    RELATIONSHIP = "Relationship"
    STYLE = "Style"
    ATTRIBUTE = "Attribute"
    COMPOSITION = "Composition"
    CONTEXTUAL = "Contextual"
    TECHNICAL = "Technical"
    SEMANTIC = "Semantic"


class ImageTag(BaseModel):
    category: TagType
    tag: str = Field(description=("Descriptive keyword or phrase representing the tag."))
    confidence: float = Field(
        description=("Confidence score for the tag, between 0 (exclusive) and 1 (inclusive)."),
    )


class ImageData(BaseModel):
    tags_list: List[ImageTag] = Field()
    short_caption: str
    verification: str
    dense_caption: str

    class Config:
        populate_by_name = True
