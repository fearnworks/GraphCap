# SPDX-License-Identifier: Apache-2.0

from ..schemas.caption import ImageData
from ..schemas.structured_vision import StructuredVisionConfig
from ..providers.clients.base_client import BaseClient
from typing import Optional, List, Dict, Any
from pathlib import Path
import asyncio
from pydantic import BaseModel

instruction = """<Task>You are a structured image analysis agent. Generate comprehensive tag list, caption,
and dense caption for an image classification system.</Task>
<TagCategories requirement="You should generate a minimum of 1 tag for each category." confidence="Confidence score
for the tag, between 0 (exclusive) and 1 (inclusive).">
- Entity : The content of the image, including the objects, people, and other elements.
- Relationship : The relationships between the entities in the image.
- Style : The style of the image, including the color, lighting, and other stylistic elements.
- Attribute : The most important attributes of the entities and relationships in the image.
- Composition : The composition of the image, including the arrangement of elements.
- Contextual : The contextual elements of the image, including the background, foreground, and other elements.
- Technical : The technical elements of the image, including the camera angle, lighting, and other technical details.
- Semantic : The semantic elements of the image, including the meaning of the image, the symbols,
and other semantic details.
<Examples note="These show the expected format as an abstraction.">
{
  "tags_list": [
    {
      "tag": "subject 1",
      "category": "Entity",
      "confidence": 0.98
    },
    {
      "tag": "subject 2",
      "category": "Entity",
      "confidence": 0.95
    },
    {
      "tag": "subject 1 runs from subject 2",
      "category": "Relationship",
      "confidence": 0.90
    },
  ]
}
</Examples>
</TagCategories>
<ShortCaption note="The short caption is a concise single sentence caption of the image content
with a maximum length of 100 characters.">
<Verification note="The verification identifies issues with the extracted tags and simple caption where the tags
do not match the visual content you can actually see. Be a critic.">
<DenseCaption note="The dense caption is a descriptive but grounded narrative paragraph of the image content.
Only reference items you are confident you can see in the image.It uses straightforward confident and clear language
without overt flowery prose. It incorporates elements from each of the tag categories to provide a broad dense caption">
"""


graphcap_vision_config = StructuredVisionConfig(config_name="graphcap", version="1", prompt=instruction, schema=ImageData)

async def process_graph_caption(
    provider,
    image_path: Path,
    max_tokens: Optional[int] = 1024,
    temperature: Optional[float] = 0.8,
    top_p: Optional[float] = 0.9,
) -> dict:
    """Process a single image and return structured caption data"""
    try:
        completion = await provider.vision(
            prompt=graphcap_vision_config.prompt,
            image=image_path,
            schema=graphcap_vision_config.schema,
            model=provider.default_model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )

        # Handle both Pydantic model and raw completion responses
        if isinstance(completion, BaseModel):
            result = completion.choices[0].message.parsed
            if isinstance(result, BaseModel):
                result = result.model_dump()
        else:
            result = completion.choices[0].message.parsed
            if "choices" in result:
                result = result["choices"][0]["message"]["parsed"]["parsed"]
            elif "message" in result:
                result = result["message"]["parsed"]

        return result
    except Exception as e:
        raise Exception(f"Error processing {image_path}: {str(e)}")

async def process_batch_captions(
    provider: BaseClient,
    image_paths: List[Path],
    max_tokens: Optional[int] = 1024,
    temperature: Optional[float] = 0.8,
    top_p: Optional[float] = 0.9,
) -> List[Dict[str, Any]]:
    """Process multiple images and return their captions"""
    tasks = [
        process_graph_caption(
            provider=provider,
            image_path=path,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
        )
        for path in image_paths
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return [
        {
            "filename": str(path),
            "config_name": graphcap_vision_config.config_name,
            "version": graphcap_vision_config.version,
            "model": provider.default_model,
            "provider": provider.name,
            "parsed": result if not isinstance(result, Exception) else {"error": str(result)}
        }
        for path, result in zip(image_paths, results)
    ]
