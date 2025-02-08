import os
from typing import List

import dagster as dg
from dagster import asset, op
from PIL import Image


def is_image_file(filename: str) -> bool:
    """Check if a file is an image based on its extension."""
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".ico"}
    return any(filename.lower().endswith(ext) for ext in image_extensions)


@asset(group_name="image", compute_kind="python")
def image_list(context: dg.AssetExecutionContext) -> list[str]:
    """Load raw images from directory."""
    image_dir = "/workspace/datasets/os_img"
    image_files = []

    if not os.path.isdir(image_dir):
        context.log.error(f"Image directory not found: {image_dir}")
        return []

    for filename in os.listdir(image_dir):
        filepath = os.path.join(image_dir, filename)
        if os.path.isfile(filepath) and is_image_file(filename):
            image_files.append(filepath)
    return image_files


@op
def load_pil_images_op(context: dg.OpExecutionContext, image_paths: List[str]) -> List[Image.Image]:
    """Load images using PIL from a list of file paths."""
    pil_images = []

    for path in image_paths:
        try:
            img = Image.open(path)
            img.load()  # Force loading image data from file
            pil_images.append(img)
            context.log.info(f"Image loaded successfully: {path}")
        except FileNotFoundError:
            context.log.error(f"File not found: {path}")
        except Exception as e:
            context.log.error(f"Error loading image {path}: {e}")

    return pil_images
