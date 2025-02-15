"""
Path: app/schemas/metadata.py
Description: Pydantic schemas for metadata and document types
Purpose: Request/response validation for metadata and document type operations
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from datetime import datetime

class MetadataType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    DATE = "date"
    ENUM = "enum"
    BOOLEAN = "boolean"

class MetadataFieldBase(BaseModel):
    name: str
    description: Optional[str] = None
    field_type: MetadataType
    is_multi_valued: bool = False
    enum_values: Optional[str] = None
    validation_rules: Optional[str] = None
    default_value: Optional[str] = None

class MetadataFieldCreate(MetadataFieldBase):
    pass

class MetadataField(MetadataFieldBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class DocumentTypeMetadataAssociation(BaseModel):
    metadata_field_id: int
    is_required: bool = False

class DocumentTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class DocumentTypeCreate(DocumentTypeBase):
    metadata_fields: List[DocumentTypeMetadataAssociation]

class DocumentType(DocumentTypeBase):
    id: int
    metadata_fields: List[MetadataField]
    model_config = ConfigDict(from_attributes=True)

# Update document schemas to include metadata
class DocumentMetadata(BaseModel):
    document_type_id: Optional[int] = None
    metadata_values: Dict[str, Any] = Field(default_factory=dict)

class MetadataAssociationUpdate(BaseModel):
    """Schema for updating metadata field associations"""
    field_associations: List[DocumentTypeMetadataAssociation]
    model_config = ConfigDict(from_attributes=True)