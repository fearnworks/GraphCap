# SPDX-License-Identifier: Apache-2.0
import time

from PIL import Image

from GraphCap.models.get_vision_model import VisionModel
from GraphCap.schemas.caption import ImageData
from GraphCap.utils.logger import logger

instruction = """<Task>You are a structured image analysis agent. Generate comprehensive tag list, caption, and dense caption for an image classification system.</Task>
<TagCategories requirement="You should generate a minimum of 1 tag for each category." confidence="Confidence score for the tag, between 0 (exclusive) and 1 (inclusive).">
- Entity : The content of the image, including the objects, people, and other elements.
- Relationship : The relationships between the entities in the image.
- Style : The style of the image, including the color, lighting, and other stylistic elements.
- Attribute : The most important attributes of the entities and relationships in the image.
- Composition : The composition of the image, including the arrangement of elements.
- Contextual : The contextual elements of the image, including the background, foreground, and other elements.
- Technical : The technical elements of the image, including the camera angle, lighting, and other technical details.
- Semantic : The semantic elements of the image, including the meaning of the image, the symbols, and other semantic details.
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
<ShortCaption note="The short caption is a concise single sentence caption of the image content with a maximum length of 100 characters.">
<Verification note="The verification identifies issues with the extracted tags and simple caption where the tags do not match the visual content you can actually see. Be a critic.">
<DenseCaption note="The dense caption is a descriptive but grounded narrative paragraph of the image content. Only reference items you are confident you can see in the image.It uses straightforward confident and clear language without overt flowery prose. It incorporates elements from each of the tag categories to provide a broad dense caption">"""

class DenseGraphCaption:
    def __init__(self, model: VisionModel, generator):
        """Initialize DenseGraphCaption with required model and generator.
        
        Args:
            model (VisionModel): The vision model to use for processing
            generator: The compiled generator to use for caption generation
        """
        start_total = time.time()
        logger.info("Initializing DenseGraphCaption")


        # Time model loading
        start_model = time.time()
        self.model = model
        self.generator = generator
        model_time = time.time() - start_model
        logger.info(f"Model initialization completed in {model_time:.2f} seconds")

        total_time = time.time() - start_total
        logger.info(f"Total DenseGraphCaption initialization took {total_time:.2f} seconds")
        logger.debug("DenseGraphCaption initialized successfully")

    def __call__(
        self,
        image: Image.Image,
        instruction: str = instruction,
        **kwargs
    ) -> ImageData:
        logger.info("Generating caption for image")

        instruction = self.model.format_instruction(instruction, [image])
        logger.debug(f"Instruction: {instruction}")

        try:
            result = self.generator(
                instruction,
                [image],
            )
            logger.debug("Caption generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}", exc_info=True)
            raise



