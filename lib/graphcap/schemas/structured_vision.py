from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class StructuredVisionConfig:
    config_name: str
    version: str
    prompt: str
    schema: BaseModel
