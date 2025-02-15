"""
Local File Storage Implementation
-------------------------------

This module implements the StorageInterface for local file system storage.
It provides functionality to save, retrieve, and delete files from the local
file system in an asynchronous manner.

Classes:
    LocalFileStorage: Implementation of StorageInterface for local file system
"""

import os
import aiofiles
from typing import BinaryIO, AsyncGenerator
from ..storage_interface import StorageInterface
from app.logging_config import get_logger

logger = get_logger(__name__)

class LocalFileStorage(StorageInterface):
    """
    Implementation of StorageInterface for local file system storage.

    Attributes:
        base_path (str): The base directory where files will be stored.
    """

    def __init__(self, base_path: str = "uploads"):
        """
        Initializes the LocalFileStorage with a base directory.

        Args:
            base_path (str): The base directory where files will be stored. Defaults to "uploads".
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        logger.info(f"Initialized LocalFileStorage with base path: {base_path}")

    async def save_file(self, file: BinaryIO, filename: str) -> str:
        """
        Saves a file to the local file system.

        Args:
            file (BinaryIO): The file object to be saved.
            filename (str): The name of the file to be saved.

        Returns:
            str: The path to the saved file.
        """
        file_path = os.path.join(self.base_path, filename)
        logger.info(f"Saving file: {filename} to path: {file_path}")
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                content = file.read()
                await f.write(content)
            logger.info(f"Successfully saved file: {filename}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save file {filename}: {str(e)}")
            raise

    async def get_file(self, file_path: str) -> AsyncGenerator[bytes, None]:
        """
        Retrieves a file from the local file system.

        Args:
            file_path (str): The path to the file to be retrieved.

        Yields:
            bytes: The content of the file in chunks.
        """
        logger.info(f"Retrieving file from path: {file_path}")
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    yield chunk
            logger.info(f"Successfully retrieved file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to retrieve file {file_path}: {str(e)}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file from the local file system.

        Args:
            file_path (str): The path to the file to be deleted.

        Returns:
            bool: True if the file was successfully deleted, False otherwise.
        """
        logger.info(f"Attempting to delete file: {file_path}")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Successfully deleted file: {file_path}")
                return True
            logger.warning(f"File not found for deletion: {file_path}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {str(e)}")
            return False