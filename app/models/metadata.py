"""
Path: app/models/metadata.py
Description: Metadata and DocumentType model definitions using SQLAlchemy ORM
Purpose: Defines the database schema for metadata fields and document types
"""

from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base

class MetadataType(str, Enum):
    TEXT = "text"
    INTEGER = "integer"
    DATE = "date"
    ENUM = "enum"
    BOOLEAN = "boolean"

# Association table for document types and metadata fields
document_type_metadata = Table(
    'document_type_metadata',
    Base.metadata,
    Column('document_type_id', Integer, ForeignKey('document_types.id'), primary_key=True),
    Column('metadata_field_id', Integer, ForeignKey('metadata_fields.id'), primary_key=True),
    Column('is_required', Boolean, default=False)
)

class MetadataField(Base):
    """
    MetadataField model representing a metadata field definition
    """
    __tablename__ = "metadata_fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(512))
    field_type = Column(SQLEnum(MetadataType), nullable=False)
    is_multi_valued = Column(Boolean, default=False)
    enum_values = Column(String(1024))  # Comma-separated values for enum type
    validation_rules = Column(String(512))  # JSON string for validation rules
    default_value = Column(String(255))
    
    # Relationships
    document_types = relationship("DocumentType", secondary=document_type_metadata, back_populates="metadata_fields")

class DocumentType(Base):
    """
    DocumentType model representing a document type with associated metadata fields
    """
    __tablename__ = "document_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(String(512))
    
    # Relationships
    metadata_fields = relationship("MetadataField", secondary=document_type_metadata, back_populates="document_types")
    documents = relationship("Document", back_populates="document_type")