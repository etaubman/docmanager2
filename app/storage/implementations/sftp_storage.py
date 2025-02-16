"""
SFTP Storage Implementation
-------------------------

This module implements the StorageInterface for SFTP storage.
It provides functionality to save, retrieve, and delete files from an SFTP server
in an asynchronous manner.

Classes:
    SFTPStorage: Implementation of StorageInterface for SFTP servers
"""

import os
import io
from typing import BinaryIO, AsyncGenerator
import asyncssh
from ..storage_interface import StorageInterface
from app.logging_config import get_logger

logger = get_logger(__name__)

class SFTPStorage(StorageInterface):
    """
    Implementation of StorageInterface for SFTP storage.

    Attributes:
        host (str): SFTP server hostname
        port (int): SFTP server port
        username (str): SFTP username
        password (str): SFTP password
        private_key_path (str): Path to private key file
        remote_path (str): Base path on remote server
    """

    def __init__(
        self,
        host: str,
        username: str,
        remote_path: str = "/upload",
        port: int = 22,
        password: str = None,
        private_key_path: str = None
    ):
        """
        Initialize SFTP storage with connection details.

        Args:
            host (str): SFTP server hostname
            username (str): SFTP username
            remote_path (str): Base path on remote server
            port (int): SFTP server port (default: 22)
            password (str, optional): SFTP password
            private_key_path (str, optional): Path to private key file
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.remote_path = remote_path.rstrip('/')
        logger.info(f"Initialized SFTPStorage for host: {host}:{port}")

    async def _get_connection(self) -> asyncssh.SSHClientConnection:
        """Create an SFTP connection."""
        connect_kwargs = {
            'username': self.username,
            'port': self.port
        }

        if self.password:
            connect_kwargs['password'] = self.password
        elif self.private_key_path:
            connect_kwargs['client_keys'] = [self.private_key_path]

        try:
            conn = await asyncssh.connect(self.host, **connect_kwargs)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to SFTP server: {str(e)}")
            raise

    async def save_file(self, file: BinaryIO, filename: str) -> str:
        """
        Save a file to the SFTP server.

        Args:
            file (BinaryIO): The file object to be saved
            filename (str): Name of the file to be saved

        Returns:
            str: The path to the saved file on SFTP server
        """
        remote_path = f"{self.remote_path}/{filename}"
        logger.info(f"Saving file to SFTP: {remote_path}")
        
        try:
            content = await file.read()
            async with await self._get_connection() as conn:
                async with conn.start_sftp_client() as sftp:
                    # Ensure remote directory exists
                    try:
                        await sftp.mkdir(self.remote_path, parents=True)
                    except asyncssh.SFTPError:
                        pass  # Directory might already exist

                    # Write file
                    file_obj = io.BytesIO(content)
                    await sftp.putfo(file_obj, remote_path)
            
            logger.info(f"Successfully saved file to SFTP: {remote_path}")
            return remote_path
        except Exception as e:
            logger.error(f"Failed to save file to SFTP: {str(e)}")
            raise

    async def get_file(self, file_path: str) -> AsyncGenerator[bytes, None]:
        """
        Retrieve a file from the SFTP server.

        Args:
            file_path (str): Path to the file on SFTP server

        Yields:
            bytes: File content in chunks
        """
        logger.info(f"Retrieving file from SFTP: {file_path}")
        
        try:
            async with await self._get_connection() as conn:
                async with conn.start_sftp_client() as sftp:
                    async with await sftp.open(file_path, 'rb') as remote_file:
                        while chunk := await remote_file.read(8192):
                            yield chunk
            
            logger.info(f"Successfully retrieved file from SFTP: {file_path}")
        except Exception as e:
            logger.error(f"Failed to retrieve file from SFTP: {str(e)}")
            raise

    async def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the SFTP server.

        Args:
            file_path (str): Path to the file on SFTP server

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        logger.info(f"Attempting to delete file from SFTP: {file_path}")
        
        try:
            async with await self._get_connection() as conn:
                async with conn.start_sftp_client() as sftp:
                    await sftp.remove(file_path)
            
            logger.info(f"Successfully deleted file from SFTP: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file from SFTP: {str(e)}")
            return False