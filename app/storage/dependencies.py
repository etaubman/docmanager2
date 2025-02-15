"""
Storage Dependencies Module
-------------------------

This module provides dependency injection functions for storage implementations.
"""

from fastapi import Depends
from .storage_interface import StorageInterface
from .implementations.local_storage import LocalFileStorage

async def get_storage() -> StorageInterface:
    """
    Dependency provider for storage implementation.
    Currently returns LocalFileStorage, but can be modified to return different implementations
    based on configuration or environment.
    """
    return LocalFileStorage()