from pathlib import Path
from typing import List, Dict, Optional
import json
from loguru import logger
from pydantic import BaseModel
from huggingface_hub import HfApi, create_repo, CommitScheduler
import os
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class DatasetConfig(BaseModel):
    name: str
    description: str
    tags: List[str]
    include_images: bool = True

class DatasetManager:
    def __init__(self, export_dir: Path):
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        self.api = HfApi()
        
    async def export_to_jsonl(
        self,
        captions: List[Dict],
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export captions to JSONL format"""
        if output_path is None:
            output_path = self.export_dir / "captions.jsonl"
            
        with output_path.open("w") as f:
            for caption in captions:
                f.write(json.dumps(caption) + "\n")
                
        logger.info(f"Exported {len(captions)} captions to {output_path}")
        return output_path

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _verify_repo_exists(self, repo_id: str, token: Optional[str] = None):
        """Verify repository exists with retries"""
        return self.api.repo_info(repo_id=repo_id, repo_type="dataset")

    async def create_hf_dataset(
        self,
        jsonl_path: Path,
        config: DatasetConfig,
        push_to_hub: bool = False,
        token: Optional[str] = None,
        private: bool = False
    ) -> str:
        """Create and optionally upload a dataset to the Hugging Face Hub"""
        if not push_to_hub or not token:
            return str(jsonl_path)

        # Get user info from token to create full repo_id
        try:
            user_info = self.api.whoami(token=token)
            username = user_info["name"]
            repo_id = f"{username}/{config.name}"
            logger.info(f"Creating dataset repository for user: {username}")
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            raise

        # Create the repository first and ensure it exists
        try:
            create_repo(
                repo_id=repo_id,
                token=token,
                private=private,
                repo_type="dataset",
                exist_ok=True
            )
            logger.info(f"Repository {repo_id} created or already exists")
            
            # Add a small delay after creation
            time.sleep(2)
            
            # Verify with retries
            self._verify_repo_exists(repo_id, token)
            logger.info(f"Repository {repo_id} verified")
            
        except Exception as e:
            logger.error(f"Failed to create or verify repository: {e}")
            raise

        try:
            # Upload the JSONL file
            logger.info(f"Uploading JSONL file to {repo_id}")
            self.api.upload_file(
                path_or_fileobj=str(jsonl_path),
                path_in_repo="data/captions.jsonl",
                repo_id=repo_id,
                repo_type="dataset",
                token=token
            )
            logger.info(f"Successfully uploaded JSONL file to {repo_id}")

            # If include_images is True, upload associated images
            if config.include_images:
                logger.info("Starting image uploads...")
                input_dir = Path(jsonl_path).parent
                logger.info(f"Looking for images in: {input_dir}")
                
                metadata_entries = []
                
                with jsonl_path.open() as f:
                    for line in f:
                        entry = json.loads(line)
                        logger.debug(f"Processing entry: {entry}")
                        
                        if "filename" in entry:
                            image_name = entry["filename"].lstrip("./")
                            image_path = input_dir / image_name
                            
                            metadata_entry = {
                                "file_name": f"data/images/{Path(image_name).name}",
                                "image": f"data/images/{Path(image_name).name}",
                                "config_name": entry.get("config_name", ""),
                                "version": entry.get("version", ""),
                                "model": entry.get("model", ""),
                                "provider": entry.get("provider", ""),
                                "split": "train",
                                "parsed": {
                                    "tags_list": entry.get("parsed", {}).get("tags_list", []),
                                    "short_caption": entry.get("parsed", {}).get("short_caption", ""),
                                    "verification": entry.get("parsed", {}).get("verification", ""),
                                    "dense_caption": entry.get("parsed", {}).get("dense_caption", "")
                                }
                            }
                            metadata_entries.append(metadata_entry)
                            
                            logger.info(f"Looking for image at: {image_path}")
                            if image_path.exists():
                                try:
                                    repo_image_path = f"data/images/{image_path.name}"
                                    logger.info(f"Uploading image {image_path} to {repo_image_path}")
                                    self.api.upload_file(
                                        path_or_fileobj=str(image_path),
                                        path_in_repo=repo_image_path,
                                        repo_id=repo_id,
                                        repo_type="dataset",
                                        token=token
                                    )
                                    logger.info(f"Successfully uploaded image: {image_path.name} to {repo_image_path}")
                                except Exception as e:
                                    logger.warning(f"Failed to upload image {image_path}: {e}", exc_info=True)
                                    continue
                            else:
                                logger.warning(f"Image not found at path: {image_path}")
                        else:
                            logger.warning("Entry missing filename field")
                            
                logger.info("Completed image uploads")

                metadata_content = "\n".join(json.dumps(entry) for entry in metadata_entries)
                try:
                    logger.info("Uploading metadata.jsonl...")
                    self.api.upload_file(
                        path_or_fileobj=metadata_content.encode(),
                        path_in_repo="data/metadata.jsonl",
                        repo_id=repo_id,
                        repo_type="dataset",
                        token=token
                    )
                    logger.info("Successfully uploaded metadata.jsonl")
                except Exception as e:
                    logger.error(f"Failed to upload metadata: {e}")
                    raise

            # Create dataset-metadata.json
            dataset_metadata = {
                "splits": ["train"],
                "column_names": [
                    "file_name",
                    "image",
                    "config_name",
                    "version",
                    "model",
                    "provider",
                    "parsed"
                ]
            }
            
            try:
                logger.info("Uploading dataset-metadata.json...")
                self.api.upload_file(
                    path_or_fileobj=json.dumps(dataset_metadata).encode(),
                    path_in_repo="dataset-metadata.json",
                    repo_id=repo_id,
                    repo_type="dataset",
                    token=token
                )
                logger.info("Successfully uploaded dataset-metadata.json")
            except Exception as e:
                logger.error(f"Failed to upload dataset metadata: {e}")
                raise

            try:
                logger.info("Updating repository settings...")
                self.api.update_repo_settings(
                    repo_id=repo_id,
                    private=private,
                    repo_type="dataset",
                    token=token
                )
                logger.info("Repository settings updated successfully")
            except Exception as e:
                logger.error(f"Failed to update repository settings: {e}")
                raise

            try:
                logger.info("Creating dataset card...")
                readme_content = f"""---
tags:
  - images
  - metadata
viewer: true
---

# Dataset Card for {config.name}

{config.description}

## Dataset Structure

The dataset is organized as follows:
- `data/images/`: Contains all the images
- `data/metadata.jsonl`: Contains metadata for each image, including:
  - Image path
  - Configuration name and version
  - Model and provider information
  - Parsed data including:
    - Tag list with categories and confidence scores
    - Short caption
    - Dense caption
    - Verification notes

## Usage
"""
                self.api.upload_file(
                    path_or_fileobj=readme_content.encode(),
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="dataset",
                    token=token
                )
                logger.info("Successfully updated README")
            except Exception as e:
                logger.warning(f"Failed to update README: {e}")

            logger.info(f"Dataset successfully uploaded to Hugging Face Hub: {repo_id}")
            return f"https://huggingface.co/datasets/{repo_id}"

        except Exception as e:
            logger.error(f"Error uploading dataset to Hub: {e}")
            raise

    async def save_work_session(
        self,
        session_data: Dict,
        session_id: str
    ) -> Path:
        """Save current work session"""
        session_path = self.export_dir / f"session_{session_id}.json"
        with session_path.open("w") as f:
            json.dump(session_data, f)
        return session_path

    async def load_work_session(
        self,
        session_id: str
    ) -> Optional[Dict]:
        """Load a previous work session"""
        session_path = self.export_dir / f"session_{session_id}.json"
        if session_path.exists():
            with session_path.open() as f:
                return json.load(f)
        return None