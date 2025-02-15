"""
Path: app/services/document_service.py
Description: Service layer for document business logic
Purpose: Handles business logic and coordinates between controllers and repository
"""

from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentUpdate, Document, DocumentFile
from app.storage.storage_interface import StorageInterface
from app.logging_config import get_logger
import os

logger = get_logger(__name__)

class DocumentService:
    """Service class for document-related operations"""

    def __init__(self):
        self.repository = DocumentRepository()

    def create_document(self, db: Session, document: DocumentCreate) -> Document:
        """Create a new document"""
        logger.info(f"Creating new document with title: {document.title}")
        try:
            doc = self.repository.create(db, document)
            logger.info(f"Successfully created document with ID: {doc.id}")
            return doc
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise

    async def create_document_with_file(
        self, 
        db: Session, 
        document: DocumentFile, 
        file: UploadFile,
        storage: StorageInterface
    ) -> Document:
        """Create a new document with an associated file"""
        logger.info(f"Creating new document with file: {file.filename}")
        try:
            filename = f"{os.urandom(8).hex()}_{file.filename}"
            file_path = await storage.save_file(file.file, filename)
            logger.info(f"File saved successfully at: {file_path}")
            
            doc_data = document.model_dump()
            doc_data.update({
                "file_path": file_path,
                "file_name": file.filename,
                "file_size": file.size
            })
            doc = self.repository.create(db, DocumentCreate(**doc_data))
            logger.info(f"Successfully created document with ID: {doc.id}")
            return doc
        except Exception as e:
            logger.error(f"Failed to create document with file: {str(e)}")
            raise

    def get_documents(self, db: Session, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get all documents with pagination"""
        logger.info(f"Retrieving documents with skip={skip}, limit={limit}")
        return self.repository.get_all(db, skip, limit)

    def get_document(self, db: Session, document_id: int) -> Document:
        """Get a specific document by ID"""
        logger.info(f"Retrieving document with ID: {document_id}")
        document = self.repository.get_by_id(db, document_id)
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
        updated_document = self.repository.update(db, document_id, document)
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
        if not self.repository.delete(db, document_id):
            logger.warning(f"Document with ID {document_id} not found for deletion")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        logger.info(f"Successfully deleted document with ID: {document_id}")