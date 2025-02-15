"""
Path: app/schemas/document.py
Description: Pydantic models for document data validation and serialization
Purpose: Defines the data structure for API request/response handling
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict
from fastapi import UploadFile

class DocumentBase(BaseModel):
    """Base schema with common document attributes"""
    title: str
    content: str

class DocumentCreate(DocumentBase):
    """Schema for document creation requests"""
    pass

class DocumentUpdate(DocumentBase):
    """Schema for document update requests"""
    pass

class DocumentFile(BaseModel):
    """Schema for file upload"""
    title: str
    content: str = ""

class Document(DocumentBase):
    """Schema for document responses, includes all document fields"""
    id: int
    file_path: str | None = None
    file_name: str | None = None
    file_size: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)

class DocumentResponse(Document):
    pass

# New schema for document version
class DocumentVersionResponse(BaseModel):
    id: int
    document_id: int
    version_number: int
    title: str
    content: str
    file_name: str | None = None
    file_path: str | None = None
    file_size: int | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)