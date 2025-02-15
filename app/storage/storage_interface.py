"""
Storage Interface Module
-----------------------

This module defines the abstract base class for storage implementations in the document management system.
The StorageInterface provides a common contract that all storage implementations must follow,
ensuring consistent file handling across different storage backends.

Classes:
    StorageInterface: Abstract base class defining the storage contract
"""

from abc import ABC, abstractmethod
from typing import BinaryIO, AsyncGenerator

class StorageInterface(ABC):
    @abstractmethod
    async def save_file(self, file: BinaryIO, filename: str) -> str:
        """Save a file and return its storage path/identifier"""
        pass

    @abstractmethod
    async def get_file(self, file_path: str) -> AsyncGenerator[bytes, None]:
        """Retrieve a file by its path/identifier"""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file by its path/identifier"""
        pass