# SPDX-License-Identifier: Apache-2.0
import time

from PIL import Image

from GraphCap.agents.BasicReasoner.schemas import ChainOfThought
from GraphCap.models.get_vision_model import VisionModel
from GraphCap.utils.logger import logger

instruction = """<Task>You are a visual reasoning agent. Analyze the given image and answer the following question: {question}</Task>

<ScratchPad>
1. Problem Analysis: Analyze the question and break it down into key components.
2. Context Analysis: Examine the image carefully and identify relevant elements.
3. Solution Outline: Develop a high-level approach to answering the question based on the image content.
4. Solution Plan: Create a step-by-step plan to arrive at the answer.
</ScratchPad>

<Response>
Provide a clear and concise answer to the question based on your analysis.
</Response>
"""
class BasicReasoner:
    def __init__(self, model: VisionModel, generator):
        """Initialize BasicReasoner with required model and generator.
        
        Args:
            model (VisionModel): The vision model to use for processing
            generator: The compiled generator to use for reasoning
        """
        start_total = time.time()
        logger.info("Initializing BasicReasoner")


        # Time model loading
        start_model = time.time()
        self.model = model
        self.generator = generator
        model_time = time.time() - start_model
        logger.info(f"Model initialization completed in {model_time:.2f} seconds")

        total_time = time.time() - start_total
        logger.info(f"Total BasicReasoner initialization took {total_time:.2f} seconds")
        logger.debug("BasicReasoner initialized successfully")

    def __call__(
        self,
        image: Image.Image,
        question: str,
        instruction: str = instruction,
        **kwargs
    ) -> ChainOfThought:
        logger.info("Generating reasoning for image")

        instruction = self.model.format_instruction(instruction.format(question=question), [image])
        logger.debug(f"Instruction: {instruction}")

        try:
            result = self.generator(
                instruction,
                [image],
            )
            logger.debug("Reasoning generated successfully")
            return result
        except Exception as e:
            logger.error(f"Error generating reasoning: {str(e)}", exc_info=True)
            raise



