from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class StructuredVisionConfig:
    prompt: str
    schema: BaseModel
