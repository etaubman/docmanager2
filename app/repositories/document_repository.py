"""
Path: app/repositories/document_repository.py
Description: Repository layer for document database operations
Purpose: Handles all database interactions for document entities
"""

from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

class DocumentRepository:
    """Repository class for document-related database operations"""

    @staticmethod
    def create(db: Session, document: DocumentCreate) -> Document:
        """Create a new document in the database"""
        db_document = Document(title=document.title, content=document.content)
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> list[Document]:
        """Retrieve all documents with pagination"""
        return db.query(Document).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, document_id: int) -> Document | None:
        """Retrieve a document by its ID"""
        return db.query(Document).filter(Document.id == document_id).first()

    @staticmethod
    def update(db: Session, document_id: int, document: DocumentUpdate) -> Document | None:
        """Update a document by its ID"""
        db_document = DocumentRepository.get_by_id(db, document_id)
        if db_document:
            for key, value in document.model_dump().items():
                setattr(db_document, key, value)
            db.commit()
            db.refresh(db_document)
        return db_document

    @staticmethod
    def delete(db: Session, document_id: int) -> bool:
        """Delete a document by its ID"""
        db_document = DocumentRepository.get_by_id(db, document_id)
        if db_document:
            db.delete(db_document)
            db.commit()
            return True
        return False