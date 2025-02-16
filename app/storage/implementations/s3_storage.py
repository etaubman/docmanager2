"""
S3 Storage Implementation
-----------------------

This module implements the StorageInterface for AWS S3 storage.
It provides functionality to save, retrieve, and delete files from S3
in an asynchronous manner.

Classes:
    S3Storage: Implementation of StorageInterface for AWS S3
"""

import os
from typing import BinaryIO, AsyncGenerator
import aioboto3
from botocore.exceptions import ClientError
from ..storage_interface import StorageInterface
from app.logging_config import get_logger

logger = get_logger(__name__)

class S3Storage(StorageInterface):
    """
    Implementation of StorageInterface for AWS S3 storage.

    Attributes:
        bucket_name (str): The name of the S3 bucket.
        aws_region (str): AWS region where the bucket is located.
    """

    def __init__(self, bucket_name: str, aws_region: str = "us-east-1"):
        """
        Initializes the S3Storage with bucket and region.

        Args:
            bucket_name (str): The name of the S3 bucket to use
            aws_region (str): AWS region where the bucket is located
        """
        self.bucket_name = bucket_name
        self.aws_region = aws_region
        self.session = aioboto3.Session(region_name=aws_region)
        logger.info(f"Initialized S3Storage with bucket: {bucket_name} in region: {aws_region}")

    async def save_file(self, file: BinaryIO, filename: str) -> str:
        """
        Saves a file to S3.

        Args:
            file (BinaryIO): The file object to be saved
            filename (str): The name of the file to be saved

        Returns:
            str: The S3 key of the saved file
        """
        logger.info(f"Saving file: {filename} to S3 bucket: {self.bucket_name}")
        try:
            content = await file.read()
            async with self.session.client('s3') as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=content
                )
            logger.info(f"Successfully saved file: {filename} to S3")
            return filename
        except Exception as e:
            logger.error(f"Failed to save file {filename} to S3: {str(e)}")
            raise

    async def get_file(self, file_path: str) -> AsyncGenerator[bytes, None]:
        """
        Retrieves a file from S3.

        Args:
            file_path (str): The S3 key of the file to be retrieved

        Yields:
            bytes: The content of the file in chunks
        """
        logger.info(f"Retrieving file from S3: {file_path}")
        try:
            async with self.session.client('s3') as s3:
                response = await s3.get_object(Bucket=self.bucket_name, Key=file_path)
                async with response['Body'] as stream:
                    while chunk := await stream.read(8192):
                        yield chunk
            logger.info(f"Successfully retrieved file from S3: {file_path}")
        except ClientError as e:
            logger.error(f"Failed to retrieve file {file_path} from S3: {str(e)}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file from S3.

        Args:
            file_path (str): The S3 key of the file to be deleted

        Returns:
            bool: True if the file was successfully deleted, False otherwise
        """
        logger.info(f"Attempting to delete file from S3: {file_path}")
        try:
            async with self.session.client('s3') as s3:
                await s3.delete_object(Bucket=self.bucket_name, Key=file_path)
            logger.info(f"Successfully deleted file from S3: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file {file_path} from S3: {str(e)}")
            return False