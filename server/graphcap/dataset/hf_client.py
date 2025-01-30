"""
# SPDX-License-Identifier: Apache-2.0
HuggingFace Client Module

This module provides a client interface for interacting with the HuggingFace Hub,
handling dataset repository operations and file uploads.

Classes:
    HuggingFaceClient: Client for HuggingFace Hub operations
"""

from pathlib import Path
from typing import Optional, Union

from huggingface_hub import HfApi, create_repo
from tenacity import retry, stop_after_attempt, wait_exponential


class HuggingFaceClient:
    """
    Client for interacting with the HuggingFace Hub API.

    Provides methods for repository management, file uploads, and user authentication.
    Includes retry logic for handling transient API failures.

    Attributes:
        api (HfApi): HuggingFace API client instance
    """

    def __init__(self):
        """Initialize the HuggingFace client with API instance."""
        self.api = HfApi()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def verify_repo_exists(self, repo_id: str, token: Optional[str] = None):
        """
        Verify that a repository exists on HuggingFace Hub.

        Args:
            repo_id (str): Repository identifier (username/repo-name)
            token (Optional[str]): HuggingFace API token

        Returns:
            RepoInfo: Repository information if it exists
        """
        return self.api.repo_info(repo_id=repo_id, repo_type="dataset")

    def get_user_info(self, token: str) -> dict:
        """
        Get information about the authenticated user.

        Args:
            token (str): HuggingFace API token

        Returns:
            dict: User information including username and organizations
        """
        return self.api.whoami(token=token)

    def create_dataset_repo(self, repo_id: str, token: str, private: bool = False):
        """
        Create a new dataset repository on HuggingFace Hub.

        Args:
            repo_id (str): Repository identifier (username/repo-name)
            token (str): HuggingFace API token
            private (bool): Whether to create a private repository. Defaults to False

        """
        create_repo(repo_id=repo_id, token=token, private=private, repo_type="dataset", exist_ok=True)

    def upload_file(self, content: Union[str, bytes, Path], path_in_repo: str, repo_id: str, token: str):
        """
        Upload a file to a HuggingFace repository.

        Args:
            content (Union[str, bytes, Path]): File content or path to upload
            path_in_repo (str): Destination path in the repository
            repo_id (str): Repository identifier (username/repo-name)
            token (str): HuggingFace API token

        """
        self.api.upload_file(
            path_or_fileobj=content if isinstance(content, (str, Path)) else content,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
        )
