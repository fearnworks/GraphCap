# src/embedding/retrieve_router.py
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from GraphCap.config.server_controller import controller
from GraphCap.utils.logger import logger
from PIL import Image

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/generate_caption")
async def generate_caption_endpoint(
    file: UploadFile = File(...),
):
    logger.info("Received caption generation request.")
    try:
        image = Image.open(file.file)
        logger.debug("Image opened successfully")
    except Exception as e:
        logger.error(f"Invalid image file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    try:
        logger.info("Generating caption")
        caption = controller["DenseGraphCaption"](image)
        logger.info("Caption generated successfully")
        if caption is None:
            logger.error("Failed to generate caption")
            raise HTTPException(status_code=500, detail="Failed to generate caption")

        return {"content": caption.model_dump()}
    except Exception as e:
        logger.error(f"Error during caption generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/generate_reasoning")
async def generate_reasoning_endpoint(
    file: UploadFile = File(...),
    question: str = Form(...),
):
    logger.info("Received reasoning generation request.")
    try:
        image = Image.open(file.file)
        logger.debug("Image opened successfully")
    except Exception as e:
        logger.error(f"Invalid image file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    try:
        logger.info("Generating reasoning")
        reasoning = controller["BasicReasoner"](image, question)
        logger.info("Reasoning generated successfully")
        if reasoning is None:
            logger.error("Failed to generate reasoning")
            raise HTTPException(status_code=500, detail="Failed to generate reasoning")

        return {"content": reasoning.model_dump()}
    except Exception as e:
        logger.error(f"Error during reasoning generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
