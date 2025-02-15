"""
Path: app/services/metadata_service.py
Description: Service layer for metadata and document type operations
Purpose: Business logic and validation for metadata fields and document types
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from app.repositories.metadata_repository import MetadataRepository, DocumentTypeRepository
from app.models.metadata import MetadataField, DocumentType, MetadataType
from app.schemas.metadata import (
    MetadataFieldCreate, 
    DocumentTypeCreate,
    MetadataAssociationUpdate
)
from app.database import get_db
import json

class MetadataValidationError(Exception):
    pass

class MetadataService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.metadata_repo = MetadataRepository(db)
        self.document_type_repo = DocumentTypeRepository(db)

    def validate_metadata_value(self, field: MetadataField, value: Any) -> bool:
        if value is None:
            return True

        try:
            if field.field_type == MetadataType.TEXT:
                if not isinstance(value, str):
                    raise MetadataValidationError(f"Field {field.name} must be a string")
            
            elif field.field_type == MetadataType.INTEGER:
                if not isinstance(value, int):
                    raise MetadataValidationError(f"Field {field.name} must be an integer")
            
            elif field.field_type == MetadataType.DATE:
                try:
                    datetime.fromisoformat(value)
                except (ValueError, TypeError):
                    raise MetadataValidationError(f"Field {field.name} must be a valid ISO date string")
            
            elif field.field_type == MetadataType.ENUM:
                if not field.enum_values:
                    raise MetadataValidationError(f"No enum values defined for field {field.name}")
                valid_values = [v.strip() for v in field.enum_values.split(',')]
                if value not in valid_values:
                    raise MetadataValidationError(f"Value for {field.name} must be one of: {', '.join(valid_values)}")
            
            elif field.field_type == MetadataType.BOOLEAN:
                if not isinstance(value, bool):
                    raise MetadataValidationError(f"Field {field.name} must be a boolean")

            if field.validation_rules:
                rules = json.loads(field.validation_rules)
                # Apply custom validation rules here
                # This can be extended based on specific needs

            return True
        except MetadataValidationError:
            raise
        except Exception as e:
            raise MetadataValidationError(f"Validation error for field {field.name}: {str(e)}")

    def validate_document_metadata(self, document_type_id: int, metadata_values: Dict[str, Any]) -> bool:
        doc_type = self.document_type_repo.get_document_type(document_type_id)
        if not doc_type:
            raise MetadataValidationError("Document type not found")

        # Check required fields
        for field in doc_type.metadata_fields:
            is_required = any(assoc.is_required 
                            for assoc in doc_type.metadata_fields_association 
                            if assoc.metadata_field_id == field.id)
            
            if is_required and field.name not in metadata_values:
                raise MetadataValidationError(f"Required field {field.name} is missing")

        # Validate provided values
        for field_name, value in metadata_values.items():
            field = next((f for f in doc_type.metadata_fields if f.name == field_name), None)
            if not field:
                raise MetadataValidationError(f"Unknown metadata field: {field_name}")

            if field.is_multi_valued:
                if not isinstance(value, list):
                    raise MetadataValidationError(f"Field {field_name} expects multiple values")
                for single_value in value:
                    self.validate_metadata_value(field, single_value)
            else:
                self.validate_metadata_value(field, value)

        return True

    # Metadata field operations
    def create_metadata_field(self, field_data: MetadataFieldCreate) -> MetadataField:
        if self.metadata_repo.get_metadata_field_by_name(field_data.name):
            raise ValueError(f"Metadata field with name {field_data.name} already exists")
        
        field = MetadataField(**field_data.dict())
        return self.metadata_repo.create_metadata_field(field)

    def get_metadata_field(self, field_id: int) -> Optional[MetadataField]:
        return self.metadata_repo.get_metadata_field(field_id)

    def get_all_metadata_fields(self) -> List[MetadataField]:
        return self.metadata_repo.get_all_metadata_fields()

    # Document type operations
    def create_document_type(self, type_data: DocumentTypeCreate) -> DocumentType:
        if self.document_type_repo.get_document_type_by_name(type_data.name):
            raise ValueError(f"Document type with name {type_data.name} already exists")

        doc_type = DocumentType(
            name=type_data.name,
            description=type_data.description
        )
        doc_type = self.document_type_repo.create_document_type(doc_type)

        # Associate metadata fields
        for assoc in type_data.metadata_fields:
            self.document_type_repo.associate_metadata_field(
                doc_type.id,
                assoc.metadata_field_id,
                assoc.is_required
            )

        return doc_type

    def get_document_type(self, type_id: int) -> Optional[DocumentType]:
        return self.document_type_repo.get_document_type(type_id)

    def get_all_document_types(self) -> List[DocumentType]:
        return self.document_type_repo.get_all_document_types()

    def update_document_type_fields(self, type_id: int, fields_update: MetadataAssociationUpdate) -> DocumentType:
        """Update the metadata fields associated with a document type"""
        doc_type = self.document_type_repo.get_document_type(type_id)
        if not doc_type:
            raise ValueError(f"Document type with id {type_id} not found")

        # Clear existing associations
        self.document_type_repo.clear_metadata_fields(type_id)

        # Add new associations
        for assoc in fields_update.field_associations:
            self.document_type_repo.associate_metadata_field(
                type_id,
                assoc.metadata_field_id,
                assoc.is_required
            )

        return self.get_document_type(type_id)