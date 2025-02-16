"""
Storage Dependencies Module
-------------------------

This module provides dependency injection functions for storage implementations.
"""

import os
from fastapi import Depends
from dotenv import load_dotenv
from .storage_interface import StorageInterface
from .implementations.local_storage import LocalFileStorage
from .implementations.s3_storage import S3Storage
from .implementations.sftp_storage import SFTPStorage

load_dotenv()

async def get_storage() -> StorageInterface:
    """
    Dependency provider for storage implementation.
    Returns appropriate storage implementation based on environment configuration.
    """
    storage_type = os.getenv("STORAGE_TYPE", "local").lower()
    
    if storage_type == "s3":
        bucket_name = os.getenv("AWS_BUCKET_NAME")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        if not bucket_name:
            raise ValueError("AWS_BUCKET_NAME environment variable is required for S3 storage")
        return S3Storage(bucket_name=bucket_name, aws_region=aws_region)
    
    elif storage_type == "sftp":
        host = os.getenv("SFTP_HOST")
        username = os.getenv("SFTP_USERNAME")
        if not (host and username):
            raise ValueError("SFTP_HOST and SFTP_USERNAME are required for SFTP storage")
        
        return SFTPStorage(
            host=host,
            username=username,
            password=os.getenv("SFTP_PASSWORD"),
            private_key_path=os.getenv("SFTP_PRIVATE_KEY_PATH"),
            port=int(os.getenv("SFTP_PORT", "22")),
            remote_path=os.getenv("SFTP_REMOTE_PATH", "/upload")
        )
    
    return LocalFileStorage()