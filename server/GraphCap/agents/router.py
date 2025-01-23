# src/embedding/retrieve_router.py
from fastapi import APIRouter, File, Form, UploadFile
from GraphCap.utils.logger import logger

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/generate_caption")
async def generate_caption_endpoint(
    file: UploadFile = File(...),
):
    logger.info("Received caption generation request.")
    # TODO: Implement updated caption generation
    return {"content": {"tags_list": [], "short_caption": "", "verification": "", "dense_caption": ""}}


@router.post("/generate_reasoning")
async def generate_reasoning_endpoint(
    file: UploadFile = File(...),
    question: str = Form(...),
):
    logger.info("Received reasoning generation request.")
    # TODO: Implement updated reasoning generation
    return {"content": {"response": ""}}
