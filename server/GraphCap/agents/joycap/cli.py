#!/usr/bin/env python3
"""
CLI interface for JoyCaption image captioning.
"""

import logging
from typing import Optional

import click
from GraphCap.agents.joycap.cap import caption_images, none_or_type
from GraphCap.agents.joycap.prompt_builder import build_prompts
from GraphCap.agents.joycap.prompt_config_library import PromptConfigLibrary

TESTING_INPUTS = {
    "glob": "*.jpg,*.jpeg,*.png,*.webp",
    "directory": "/./datasets/cc_selected",
    "num_workers": 5,
    "batch_size": 5,
    "max_new_tokens": 256,
    "temperature": 0.6,
    "top_p": 0.9,
    "top_k": None,
    "greedy": False,
    "prompts": build_prompts(PromptConfigLibrary.get_artistic_configs()),
    "model": "fancyfeast/llama-joycaption-alpha-two-hf-llava",
    "output_dir": "./.local/joycap",
}


@click.group()
def cli():
    """JoyCaption CLI tool for image captioning"""
    pass


@cli.command()
@click.option("-t", "--test", is_flag=True, help="Use test configuration")
@click.option("--glob", type=str, help="Glob pattern to find images")
@click.option("--filelist", type=str, help="File containing list of images")
@click.option("--batch-size", type=int, default=1, help="Batch size")
@click.option("--greedy/--no-greedy", default=False, help="Use greedy decoding instead of sampling")
@click.option("--temperature", type=float, default=0.6, help="Sampling temperature")
@click.option("--top-p", type=lambda x: none_or_type(x, float), default=0.9, help="Top-p sampling")
@click.option("--top-k", type=lambda x: none_or_type(x, int), default=None, help="Top-k sampling")
@click.option("--max-new-tokens", type=int, default=256, help="Maximum length of the generated caption (in tokens)")
@click.option("--num-workers", type=int, default=4, help="Number of workers loading images in parallel")
@click.option("--model", type=str, default="fancyfeast/llama-joycaption-alpha-two-hf-llava", help="Model to use")
@click.option("--prompt", type=str, help="Caption prompt to use")
@click.option("--prompt-file", type=str, help="JSON file containing prompts")
@click.option("--directory", type=str, help="Directory to search for images")
@click.option("--output", type=str, default="./.local/joycap", help="Output directory for captions")
def caption(
    test: bool,
    glob: Optional[str],
    filelist: Optional[str],
    batch_size: int,
    greedy: bool,
    temperature: float,
    top_p: Optional[float],
    top_k: Optional[int],
    max_new_tokens: int,
    num_workers: int,
    model: str,
    prompt: Optional[str],
    prompt_file: Optional[str],
    directory: Optional[str],
    output: str,
):
    """Caption images using JoyCaption"""
    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

    if test:
        logging.info("Using test configuration")
        config = TESTING_INPUTS.copy()
    else:
        # Create config dictionary from CLI arguments
        config = {
            "glob": glob,
            "filelist": filelist,
            "batch_size": batch_size,
            "greedy": greedy,
            "temperature": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_new_tokens": max_new_tokens,
            "num_workers": num_workers,
            "model": model,
            "prompts": [{"prompt": prompt, "weight": 1.0}] if prompt else None,
            "prompt_file": prompt_file,
            "directory": directory or ".",
            "output_dir": output,
        }

    try:
        caption_images(config)
    except Exception as e:
        logging.error(f"Error during captioning: {e}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    cli()
