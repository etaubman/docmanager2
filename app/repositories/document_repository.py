"""
Path: app/repositories/document_repository.py
Description: Repository layer for document database operations
Purpose: Handles all database interactions for document entities
"""

from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.logging_config import get_logger
from app.models.document_version import DocumentVersion
from typing import Optional
from sqlalchemy import cast, String, JSON  # updated import

logger = get_logger(__name__)

class DocumentRepository:
    """Repository class for document-related database operations"""

    def __init__(self, db: Session):
        """Initialize the repository with a database session"""
        self.db = db

    @staticmethod
    def create(db: Session, document: DocumentCreate) -> Document:
        """Create a new document in the database"""
        logger.debug(f"Creating document in database: {document.title}")
        try:
            db_document = Document(
                title=document.title,
                content=document.content,
                file_path=getattr(document, 'file_path', None),
                file_name=getattr(document, 'file_name', None),
                file_size=getattr(document, 'file_size', None),
                metadata_values=getattr(document, 'metadata_values', None)
            )
            db.add(db_document)
            db.commit()
            db.refresh(db_document)
            logger.info(f"Successfully created document in database with ID: {db_document.id}")
            return db_document
        except Exception as e:
            logger.error(f"Database error while creating document: {str(e)}")
            db.rollback()
            raise

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[Document]:
        """Retrieve all documents with pagination"""
        logger.debug(f"Retrieving documents from database with skip={skip}, limit={limit}")
        try:
            documents = db.query(Document).offset(skip).limit(limit).all()
            logger.info(f"Retrieved {len(documents)} documents from database")
            return documents
        except Exception as e:
            logger.error(f"Database error while retrieving documents: {str(e)}")
            raise

    @staticmethod
    def get_by_id(db: Session, document_id: int) -> Document | None:
        """Retrieve a document by its ID"""
        logger.debug(f"Retrieving document from database with ID: {document_id}")
        try:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document:
                logger.info(f"Successfully retrieved document with ID: {document_id}")
            else:
                logger.info(f"No document found with ID: {document_id}")
            return document
        except Exception as e:
            logger.error(f"Database error while retrieving document {document_id}: {str(e)}")
            raise

    @staticmethod
    def update(db: Session, document_id: int, document: DocumentUpdate) -> Document | None:
        """Update a document by its ID"""
        logger.debug(f"Updating document in database with ID: {document_id}")
        try:
            db_document = DocumentRepository.get_by_id(db, document_id)
            if db_document:
                # Archive current version
                version_number = len(db_document.versions) + 1 if db_document.versions else 1
                version = DocumentVersion(
                    document_id=db_document.id,
                    version_number=version_number,
                    title=db_document.title,
                    content=db_document.content,
                    file_name=db_document.file_name,
                    file_path=db_document.file_path,
                    file_size=db_document.file_size
                )
                db.add(version)
                # Update document
                for key, value in document.model_dump().items():
                    setattr(db_document, key, value)
                db.commit()
                db.refresh(db_document)
                logger.info(f"Successfully updated document with ID: {document_id}")
            return db_document
        except Exception as e:
            logger.error(f"Database error while updating document {document_id}: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def delete(db: Session, document_id: int) -> bool:
        """Delete a document by its ID"""
        logger.debug(f"Deleting document from database with ID: {document_id}")
        try:
            db_document = DocumentRepository.get_by_id(db, document_id)
            if db_document:
                db.delete(db_document)
                db.commit()
                logger.info(f"Successfully deleted document with ID: {document_id}")
                return True
            logger.info(f"No document found to delete with ID: {document_id}")
            return False
        except Exception as e:
            logger.error(f"Database error while deleting document {document_id}: {str(e)}")
            db.rollback()
            raise

    @staticmethod
    def get_versions(db: Session, document_id: int) -> list:
        """Retrieve all versions of a document by its ID"""
        return db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.asc()).all()

    @staticmethod
    def get_latest_version(db: Session, document_id: int):
        """Retrieve the latest version of a document by its ID"""
        return db.query(DocumentVersion).filter(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc()).first()

    @staticmethod
    def search_documents(
        db: Session,
        filename: Optional[str] = None,
        title: Optional[str] = None,
        metadata_filter: Optional[dict] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        query = db.query(Document)
        if filename:
            query = query.filter(Document.file_name.ilike(f"%{filename}%"))
        if title:
            query = query.filter(Document.title.ilike(f"%{title}%"))
        if metadata_filter:
            for key, value in metadata_filter.items():
                # Updated metadata_values filter to use PostgreSQL JSON extraction "->>"
                query = query.filter(Document.metadata_values.op("->>")(key) == value)
        return query.offset(skip).limit(limit).all()