#!/usr/bin/env python3
"""
Use JoyCaption to caption images.
"""

import logging
from pathlib import Path

import torch
import torch.amp
import torchvision.transforms.functional as TVF
from PIL import Image
from torch.utils.data import Dataset
from transformers import (
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

from GraphCap.agents.joycap.prompt_builder import Prompt


class ImageDataset(Dataset):
    def __init__(
        self,
        prompts: list[Prompt],
        paths: list[Path],
        tokenizer: PreTrainedTokenizer | PreTrainedTokenizerFast,
        image_token_id: int,
        image_seq_length: int,
    ):
        self.prompts = prompts
        self.paths = paths
        self.tokenizer = tokenizer
        self.image_token_id = image_token_id
        self.image_seq_length = image_seq_length
        self.pad_token_id = tokenizer.pad_token_id

        # Create all image-prompt combinations
        self.combinations = [(path, prompt) for path in paths for prompt in prompts]

    def __len__(self):
        return len(self.combinations)

    def __getitem__(self, idx: int) -> dict:
        path, prompt = self.combinations[idx]

        # Preprocess image
        try:
            image = Image.open(path)
            if image.size != (384, 384):
                image = image.resize((384, 384), Image.LANCZOS)
            image = image.convert("RGB")
            pixel_values = TVF.pil_to_tensor(image)
        except Exception as e:
            logging.error(f"Failed to load image '{path}': {e}")
            pixel_values = None  # Will be filtered out later

        # Build the conversation
        convo = [
            {
                "role": "system",
                "content": "You are a helpful image captioner.",
            },
            {
                "role": "user",
                "content": prompt.prompt,
            },
        ]

        # Format the conversation
        convo_string = self.tokenizer.apply_chat_template(convo, tokenize=False, add_generation_prompt=True)
        assert isinstance(convo_string, str)

        # Tokenize the conversation
        convo_tokens = self.tokenizer.encode(convo_string, add_special_tokens=False, truncation=False)

        # Repeat the image tokens
        input_tokens = []
        for token in convo_tokens:
            if token == self.image_token_id:
                input_tokens.extend([self.image_token_id] * self.image_seq_length)
            else:
                input_tokens.append(token)

        input_ids = torch.tensor(input_tokens, dtype=torch.long)
        attention_mask = torch.ones_like(input_ids)

        return {
            "path": path,
            "prompt": prompt,  # Include the full prompt object
            "pixel_values": pixel_values,
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }

    def collate_fn(self, batch: list[dict]) -> dict:
        # Filter out images that failed to load
        batch = [item for item in batch if item["pixel_values"] is not None]

        # Pad input_ids and attention_mask
        # Have to use left padding because HF's generate can't handle right padding it seems
        max_length = max(item["input_ids"].shape[0] for item in batch)
        n_pad = [max_length - item["input_ids"].shape[0] for item in batch]
        input_ids = torch.stack(
            [
                torch.nn.functional.pad(item["input_ids"], (n, 0), value=self.pad_token_id)
                for item, n in zip(batch, n_pad)
            ]
        )
        attention_mask = torch.stack(
            [torch.nn.functional.pad(item["attention_mask"], (n, 0), value=0) for item, n in zip(batch, n_pad)]
        )

        # Stack pixel values
        pixel_values = torch.stack([item["pixel_values"] for item in batch])

        # Collect paths and prompts
        paths = [item["path"] for item in batch]
        prompts = [item["prompt"] for item in batch]

        return {
            "paths": paths,
            "prompts": prompts,
            "pixel_values": pixel_values,
            "input_ids": input_ids,
            "attention_mask": attention_mask,
        }
