#!/usr/bin/env python3
"""
Use JoyCaption to caption images.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import torch
import torch.amp
import torchvision.transforms.functional as TVF
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import (
    AutoTokenizer,
    LlavaForConditionalGeneration,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

from GraphCap.agents.joycap.ImageDataset import ImageDataset
from GraphCap.agents.joycap.prompt_builder import Prompt


def none_or_type(value, desired_type):
    if value == "None":
        return None
    return desired_type(value)


def caption_images(config: Dict[str, Any]):
    """
    Main function to caption images using the provided configuration.
    """
    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base = Path(config["output_dir"])
    output_dir = output_base / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save prompt configurations
    save_prompt_configs(config["prompts"], output_dir)

    # Find the images
    image_paths = find_images(config.get("glob"), config.get("filelist"), Path(config.get("directory")))
    if len(image_paths) == 0:
        logging.warning("No images found")
        return
    logging.info(f"Found {len(image_paths)} images")

    # Load JoyCaption
    tokenizer = AutoTokenizer.from_pretrained(config["model"], use_fast=True)
    assert isinstance(tokenizer, PreTrainedTokenizer) or isinstance(tokenizer, PreTrainedTokenizerFast)
    llava_model = LlavaForConditionalGeneration.from_pretrained(config["model"], torch_dtype="bfloat16", device_map=0)
    assert isinstance(llava_model, LlavaForConditionalGeneration)

    prompts = config["prompts"]
    dataset = ImageDataset(
        prompts, image_paths, tokenizer, llava_model.config.image_token_index, llava_model.config.image_seq_length
    )
    dataloader = DataLoader(
        dataset,
        collate_fn=dataset.collate_fn,
        num_workers=config["num_workers"],
        shuffle=False,
        drop_last=False,
        batch_size=config["batch_size"],
    )
    end_of_header_id = tokenizer.convert_tokens_to_ids("<|end_header_id|>")
    end_of_turn_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")
    assert isinstance(end_of_header_id, int) and isinstance(end_of_turn_id, int)

    # Create a dictionary to store captions by image path
    image_captions = {}

    pbar = tqdm(total=len(image_paths) * len(prompts), desc="Captioning images...", dynamic_ncols=True)
    for batch in dataloader:
        vision_dtype = llava_model.vision_tower.vision_model.embeddings.patch_embedding.weight.dtype
        vision_device = llava_model.vision_tower.vision_model.embeddings.patch_embedding.weight.device
        language_device = llava_model.language_model.get_input_embeddings().weight.device

        # Move to GPU
        pixel_values = batch["pixel_values"].to(vision_device, non_blocking=True)
        input_ids = batch["input_ids"].to(language_device, non_blocking=True)
        attention_mask = batch["attention_mask"].to(language_device, non_blocking=True)

        # Normalize the image
        pixel_values = pixel_values / 255.0
        pixel_values = TVF.normalize(pixel_values, [0.5], [0.5])
        pixel_values = pixel_values.to(vision_dtype)

        # Generate the captions
        generate_ids = llava_model.generate(
            input_ids=input_ids,
            pixel_values=pixel_values,
            attention_mask=attention_mask,
            max_new_tokens=config["max_new_tokens"],
            do_sample=not config["greedy"],
            suppress_tokens=None,
            use_cache=True,
            temperature=config["temperature"],
            top_k=config["top_k"],
            top_p=config["top_p"],
        )

        # Trim off the prompts
        assert isinstance(generate_ids, torch.Tensor)
        generate_ids = generate_ids.tolist()
        generate_ids = [trim_off_prompt(ids, end_of_header_id, end_of_turn_id) for ids in generate_ids]

        # Decode the captions
        captions = tokenizer.batch_decode(generate_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        captions = [c.strip() for c in captions]

        # Store captions by image path and config name
        for path, caption, prompt in zip(batch["paths"], captions, batch["prompts"]):
            path_str = str(path)  # Convert Path to string
            if path_str not in image_captions:
                image_captions[path_str] = {"image_path": path_str, "timestamp": datetime.now().isoformat()}
            image_captions[path_str][prompt.config_name] = caption

        pbar.update(len(captions))

    # Write results
    write_results(image_captions, output_dir)


def trim_off_prompt(input_ids: list[int], eoh_id: int, eot_id: int) -> list[int]:
    # Trim off the prompt
    while True:
        try:
            i = input_ids.index(eoh_id)
        except ValueError:
            break

        input_ids = input_ids[i + 1 :]

    # Trim off the end
    try:
        i = input_ids.index(eot_id)
    except ValueError:
        return input_ids

    return input_ids[:i]


def write_results(captions: Dict[str, Dict[str, str]], output_dir: Path):
    """Write results to Excel and JSON files"""
    try:
        # Write Excel file
        excel_path = output_dir / "captions.xlsx"
        write_captions_excel(captions, excel_path)

        # Write JSON file with full data
        json_path = output_dir / "captions.json"
        write_captions_json(captions, json_path)

    except Exception as e:
        logging.error(f"Failed to write results: {e}")
        raise


def write_captions_excel(captions: Dict[str, Dict[str, str]], excel_path: Path):
    """Write captions to Excel file"""
    try:
        # Convert dictionary to DataFrame
        df = pd.DataFrame.from_dict(captions, orient="index")

        # Reorder columns to ensure image_path and timestamp are first
        columns = ["image_path", "timestamp"] + [col for col in df.columns if col not in ["image_path", "timestamp"]]
        df = df[columns]

        # Write to Excel
        df.to_excel(excel_path, index=False, engine="openpyxl")
        logging.info(f"Wrote captions to Excel file: {excel_path}")
    except Exception as e:
        logging.error(f"Failed to write Excel file: {e}")
        raise


def write_captions_json(captions: Dict[str, Dict[str, str]], json_path: Path):
    """Write captions to JSON file"""
    try:
        # Ensure all paths are strings
        json_data = {str(path): data for path, data in captions.items()}

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        logging.info(f"Wrote captions to JSON file: {json_path}")
    except Exception as e:
        logging.error(f"Failed to write JSON file: {e}")
        raise


def save_prompt_configs(prompts: List[Prompt], output_dir: Path):
    """Save prompt configurations to JSON file"""
    try:
        configs = []
        for prompt in prompts:
            config_dict = {
                "config_name": prompt.config_name,
                "mode": prompt.prompt_config.mode.value,
                "tone": prompt.prompt_config.tone.value if prompt.prompt_config.tone else None,
                "word_count": prompt.prompt_config.word_count,
                "length": prompt.prompt_config.length,
                "use_case": prompt.prompt_config.use_case,
                "description": prompt.prompt_config.description,
                "options": {
                    "exclude_unchangeable_attributes": prompt.prompt_config.exclude_unchangeable_attributes,
                    "include_lighting": prompt.prompt_config.include_lighting,
                    "include_camera_angle": prompt.prompt_config.include_camera_angle,
                    "include_watermark_info": prompt.prompt_config.include_watermark_info,
                    "include_artifact_info": prompt.prompt_config.include_artifact_info,
                    "include_camera_details": prompt.prompt_config.include_camera_details,
                    "keep_pg": prompt.prompt_config.keep_pg,
                    "exclude_resolution": prompt.prompt_config.exclude_resolution,
                    "include_quality_assessment": prompt.prompt_config.include_quality_assessment,
                    "include_composition": prompt.prompt_config.include_composition,
                    "exclude_text": prompt.prompt_config.exclude_text,
                    "include_depth_of_field": prompt.prompt_config.include_depth_of_field,
                    "include_lighting_source": prompt.prompt_config.include_lighting_source,
                    "avoid_ambiguity": prompt.prompt_config.avoid_ambiguity,
                    "include_sfw_rating": prompt.prompt_config.include_sfw_rating,
                    "only_important_elements": prompt.prompt_config.only_important_elements,
                },
                "generated_prompt": prompt.prompt,
            }
            configs.append(config_dict)

        config_path = output_dir / "prompt_configs.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)
        logging.info(f"Saved prompt configurations to: {config_path}")
    except Exception as e:
        logging.error(f"Failed to save prompt configurations: {e}")
        raise


def parse_prompts(prompt_str: str | None, prompt_file: str | None) -> list[Prompt]:
    if prompt_str is not None and prompt_file is not None:
        raise ValueError("Cannot specify both --prompt and --prompt-file")

    if prompt_str is not None:
        return [Prompt(prompt=prompt_str, weight=1.0)]

    if prompt_file is None:
        raise ValueError("Must specify either --prompt or --prompt-file")

    data = json.loads(Path(prompt_file).read_text())

    if not isinstance(data, list):
        raise ValueError("Expected JSON file to contain a list of prompts")

    prompts = []

    for item in data:
        if isinstance(item, str):
            prompts.append(Prompt(prompt=item, weight=1.0))
        elif (
            isinstance(item, dict)
            and "prompt" in item
            and "weight" in item
            and isinstance(item["prompt"], str)
            and isinstance(item["weight"], (int, float))
        ):
            prompts.append(Prompt(prompt=item["prompt"], weight=item["weight"]))
        else:
            raise ValueError(
                f"Invalid prompt in JSON file. Should be either a string or an object with 'prompt' and 'weight' fields: {item}"
            )

    if len(prompts) == 0:
        raise ValueError("No prompts found in JSON file")

    if sum(p.weight for p in prompts) <= 0.0:
        raise ValueError("Prompt weights must sum to a positive number")

    return prompts


def find_images(glob: str | None, filelist: str | Path | None, directory: Path) -> list[Path]:
    if glob is None and filelist is None:
        raise ValueError("Must specify either --glob or --filelist")

    paths = []
    logging.info("All files in directory:")
    logging.info(list(directory.glob("*")))

    if glob is not None:
        # Split the glob pattern and search for each pattern
        patterns = glob.split(",")
        for pattern in patterns:
            pattern = pattern.strip()
            logging.info(f"Searching for images with pattern: {pattern}")
            found = list(directory.glob(pattern))
            paths.extend(found)
            logging.info(f"Found {len(found)} images with pattern: {pattern}")

    if filelist is not None:
        logging.info(f"Searching for images with filelist: {filelist}")
        paths.extend(
            (Path(line.strip()) for line in Path(filelist).read_text().strip().splitlines() if line.strip() != "")
        )

    # Remove duplicates while preserving order
    seen = set()
    unique_paths = []
    for path in paths:
        if path not in seen:
            seen.add(path)
            unique_paths.append(path)

    return unique_paths
