import os
from typing import List

import dagster as dg
from dagster import asset, op
from PIL import Image


def is_image_file(filename: str) -> bool:
    """Check if a file is an image based on its extension."""
    image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".ico"]
    return any(filename.lower().endswith(ext) for ext in image_extensions)


@asset(group_name="image", compute_kind="python")
def image_list(context: dg.AssetExecutionContext) -> list[str]:
    """Load raw images from directory."""
    image_dir = "/workspace/datasets/os_img"
    image_files = [
        os.path.join(image_dir, f)
        for f in os.listdir(image_dir)
        if os.path.isfile(os.path.join(image_dir, f)) and is_image_file(f)
    ]
    context.log.info(f"Found {len(image_files)} images in {image_dir}")
    context.add_output_metadata(
        {
            "num_images": len(image_files),
            "image_dir": image_dir,
            "image_files": str(image_files),
        }
    )
    return image_files


@op
def load_pil_images_op(context: dg.OpExecutionContext, image_paths: List[str]) -> List[Image.Image]:
    """Load images using PIL."""
    pil_images = []
    for path in image_paths:
        try:
            img = Image.open(path)
            pil_images.append(img)
            context.log.info(f"Image loaded successfully: {path}")
        except FileNotFoundError:
            context.log.error(f"File not found: {path}")
        except Exception as e:
            context.log.error(f"Error loading image {path}: {e}")

    return pil_images
