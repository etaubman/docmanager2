"""
Path: app/repositories/metadata_repository.py
Description: Repository for metadata and document type operations
Purpose: Database operations for metadata fields and document types
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, delete
from app.models.metadata import MetadataField, DocumentType, document_type_metadata

class MetadataRepository:
    def __init__(self, db: Session):
        """Initialize the repository with a database session"""
        self.db = db

    def create_metadata_field(self, metadata_field: MetadataField) -> MetadataField:
        """Create a new metadata field in the database"""
        self.db.add(metadata_field)
        self.db.commit()
        self.db.refresh(metadata_field)
        return metadata_field

    def get_metadata_field(self, field_id: int) -> Optional[MetadataField]:
        """Retrieve a metadata field by its ID"""
        return self.db.query(MetadataField).filter(MetadataField.id == field_id).first()

    def get_metadata_field_by_name(self, name: str) -> Optional[MetadataField]:
        """Retrieve a metadata field by its name"""
        return self.db.query(MetadataField).filter(MetadataField.name == name).first()

    def get_all_metadata_fields(self) -> List[MetadataField]:
        """Retrieve all metadata fields"""
        return self.db.query(MetadataField).all()

    def update_metadata_field(self, field_id: int, updates: dict) -> Optional[MetadataField]:
        """Update a metadata field by its ID with the provided updates"""
        field = self.get_metadata_field(field_id)
        if field:
            for key, value in updates.items():
                setattr(field, key, value)
            self.db.commit()
            self.db.refresh(field)
        return field

    def delete_metadata_field(self, field_id: int) -> bool:
        """Delete a metadata field by its ID"""
        field = self.get_metadata_field(field_id)
        if field:
            self.db.delete(field)
            self.db.commit()
            return True
        return False

class DocumentTypeRepository:
    def __init__(self, db: Session):
        """Initialize the repository with a database session"""
        self.db = db

    def create_document_type(self, document_type: DocumentType) -> DocumentType:
        """Create a new document type in the database"""
        self.db.add(document_type)
        self.db.commit()
        self.db.refresh(document_type)
        return document_type

    def get_document_type(self, type_id: int) -> Optional[DocumentType]:
        """Retrieve a document type by its ID"""
        return self.db.query(DocumentType).filter(DocumentType.id == type_id).first()

    def get_document_type_by_name(self, name: str) -> Optional[DocumentType]:
        """Retrieve a document type by its name"""
        return self.db.query(DocumentType).filter(DocumentType.name == name).first()

    def get_all_document_types(self) -> List[DocumentType]:
        """Retrieve all document types"""
        return self.db.query(DocumentType).all()

    def update_document_type(self, type_id: int, updates: dict) -> Optional[DocumentType]:
        """Update a document type by its ID with the provided updates"""
        doc_type = self.get_document_type(type_id)
        if doc_type:
            for key, value in updates.items():
                setattr(doc_type, key, value)
            self.db.commit()
            self.db.refresh(doc_type)
        return doc_type

    def delete_document_type(self, type_id: int) -> bool:
        """Delete a document type by its ID"""
        doc_type = self.get_document_type(type_id)
        if doc_type:
            self.db.delete(doc_type)
            self.db.commit()
            return True
        return False

    def associate_metadata_field(self, type_id: int, field_id: int, is_required: bool = False):
        """Associate a metadata field with a document type"""
        stmt = document_type_metadata.insert().values(
            document_type_id=type_id,
            metadata_field_id=field_id,
            is_required=is_required
        )
        self.db.execute(stmt)
        self.db.commit()

    def dissociate_metadata_field(self, type_id: int, field_id: int):
        """Dissociate a metadata field from a document type"""
        stmt = document_type_metadata.delete().where(
            and_(
                document_type_metadata.c.document_type_id == type_id,
                document_type_metadata.c.metadata_field_id == field_id
            )
        )
        self.db.execute(stmt)
        self.db.commit()

    def clear_metadata_fields(self, type_id: int):
        """Remove all metadata field associations for a document type"""
        stmt = delete(document_type_metadata).where(
            document_type_metadata.c.document_type_id == type_id
        )
        self.db.execute(stmt)
        self.db.commit()