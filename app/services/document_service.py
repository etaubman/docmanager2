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
import os

class DocumentService:
    """Service class for document-related operations"""

    def __init__(self):
        self.repository = DocumentRepository()

    def create_document(self, db: Session, document: DocumentCreate) -> Document:
        """Create a new document"""
        return self.repository.create(db, document)

    async def create_document_with_file(
        self, 
        db: Session, 
        document: DocumentFile, 
        file: UploadFile,
        storage: StorageInterface
    ) -> Document:
        """Create a new document with an associated file"""
        # Save the file first
        filename = f"{os.urandom(8).hex()}_{file.filename}"
        file_path = await storage.save_file(file.file, filename)
        
        # Create document with file information
        doc_data = document.model_dump()
        doc_data.update({
            "file_path": file_path,
            "file_name": file.filename,
            "file_size": file.size
        })
        return self.repository.create(db, DocumentCreate(**doc_data))

    def get_documents(self, db: Session, skip: int = 0, limit: int = 100) -> list[Document]:
        """Get all documents with pagination"""
        return self.repository.get_all(db, skip, limit)

    def get_document(self, db: Session, document_id: int) -> Document:
        """Get a specific document by ID"""
        document = self.repository.get_by_id(db, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        return document

    def update_document(self, db: Session, document_id: int, document: DocumentUpdate) -> Document:
        """Update a specific document"""
        updated_document = self.repository.update(db, document_id, document)
        if not updated_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )
        return updated_document

    def delete_document(self, db: Session, document_id: int) -> None:
        """Delete a specific document"""
        if not self.repository.delete(db, document_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )