"""
Path: app/services/document_service.py
Description: Document service with metadata validation
"""

from typing import Optional, Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status, Depends
import os
import uuid

from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentFile
from app.repositories.document_repository import DocumentRepository
from app.services.metadata_service import MetadataService
from app.storage.storage_interface import StorageInterface
from app.storage.dependencies import get_storage
from app.database import get_db
from app.logging_config import get_logger

logger = get_logger(__name__)



class DocumentService:
    def __init__(self, db: Session = Depends(get_db), storage: StorageInterface = Depends(get_storage)):
        self.db = db
        self.document_repo = DocumentRepository(db)
        self.metadata_service = MetadataService(db)
        self.storage = storage

    async def create_document(
        self,
        file: UploadFile,
        title: str,
        document_type_id: Optional[int] = None,
        metadata_values: Optional[Dict[str, Any]] = None
    ) -> Document:
        if document_type_id:
            # Validate metadata if document type is provided
            self.metadata_service.validate_document_metadata(
                document_type_id,
                metadata_values or {}
            )

        # Generate unique filename
        file_id = str(uuid.uuid4()).replace("-", "")
        file_extension = os.path.splitext(file.filename)[1]
        storage_filename = f"{file_id}{file_extension}"

        # Save file using storage interface
        file_path = await self.storage.save_file(file, storage_filename)
        
        # Create document using schema
        doc_create = DocumentCreate(
            title=title,
            content="",  # Content can be updated later with file processing
        )
        document = self.document_repo.create(self.db, doc_create)
        
        # Update additional fields
        document.file_path = file_path
        document.file_name = file.filename
        document.file_size = file.size
        document.document_type_id = document_type_id
        document.metadata_values = metadata_values or {}
        
        self.db.commit()
        self.db.refresh(document)
        return document

    async def create_document_with_file(self, db: Session, document: DocumentFile, file: UploadFile, storage: StorageInterface) -> Document:
        """Create a new document with an attached file"""
        # Generate unique filename
        file_id = str(uuid.uuid4()).replace("-", "")
        file_extension = os.path.splitext(file.filename)[1]
        storage_filename = f"{file_id}{file_extension}"
        
        # Save file
        file_path = await storage.save_file(file, storage_filename)
        
        # Create document
        doc_create = DocumentCreate(
            title=document.title,
            content=document.content
        )
        doc = self.document_repo.create(db, doc_create)
        
        # Update file information
        doc.file_path = file_path
        doc.file_name = file.filename
        doc.file_size = file.size
        db.commit()
        db.refresh(doc)
        
        return doc

    def update_document_metadata(
        self,
        document_id: int,
        document_type_id: Optional[int],
        metadata_values: Dict[str, Any]
    ) -> Document:
        document = self.document_repo.get_by_id(self.db, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        if document_type_id:
            # Validate metadata for new document type
            self.metadata_service.validate_document_metadata(
                document_type_id,
                metadata_values
            )
            document.document_type_id = document_type_id
            
        document.metadata_values = metadata_values
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_documents(self, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get all documents with pagination"""
        logger.info(f"Retrieving documents with skip={skip}, limit={limit}")
        return self.document_repo.get_all(self.db, skip, limit)

    def get_document(self, document_id: int) -> Document:
        """Get a specific document by ID"""
        logger.info(f"Retrieving document with ID: {document_id}")
        document = self.document_repo.get_by_id(self.db, document_id)
        if not document:
            logger.warning(f"Document with ID {document_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        return document

    def update_document(self, db: Session, document_id: int, document: DocumentUpdate) -> Document:
        """Update a specific document"""
        logger.info(f"Updating document with ID: {document_id}")
        updated_document = self.document_repo.update(db, document_id, document)
        if not updated_document:
            logger.warning(f"Document with ID {document_id} not found for update")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        logger.info(f"Successfully updated document with ID: {document_id}")
        return updated_document

    def delete_document(self, db: Session, document_id: int) -> None:
        """Delete a specific document"""
        logger.info(f"Attempting to delete document with ID: {document_id}")
        if not self.document_repo.delete(db, document_id):
            logger.warning(f"Document with ID {document_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        logger.info(f"Successfully deleted document with ID: {document_id}")

    async def get_file(self, file_path: str) -> AsyncGenerator[bytes, None]:
        """Get a file from storage by its path"""
        logger.info(f"Retrieving file from storage: {file_path}")
        async for chunk in self.storage.get_file(file_path):
            yield chunk