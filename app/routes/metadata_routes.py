"""
Path: app/routes/metadata_routes.py
Description: API routes for metadata and document type operations
Purpose: Handle HTTP requests for metadata and document type management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.metadata import (
    MetadataField, MetadataFieldCreate,
    DocumentType, DocumentTypeCreate,
    MetadataAssociationUpdate
)
from app.services.metadata_service import MetadataService, MetadataValidationError

router = APIRouter()

# Metadata Field Routes
@router.post("/metadata-fields/", response_model=MetadataField)
def create_metadata_field(
    field: MetadataFieldCreate,
    db: Session = Depends(get_db)
):
    service = MetadataService(db)
    try:
        return service.create_metadata_field(field)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metadata-fields/", response_model=List[MetadataField])
def get_metadata_fields(db: Session = Depends(get_db)):
    service = MetadataService(db)
    return service.get_all_metadata_fields()

@router.get("/metadata-fields/{field_id}", response_model=MetadataField)
def get_metadata_field(field_id: int, db: Session = Depends(get_db)):
    service = MetadataService(db)
    field = service.get_metadata_field(field_id)
    if not field:
        raise HTTPException(status_code=404, detail="Metadata field not found")
    return field

# Document Type Routes
@router.post("/document-types/", response_model=DocumentType)
def create_document_type(
    doc_type: DocumentTypeCreate,
    db: Session = Depends(get_db)
):
    service = MetadataService(db)
    try:
        return service.create_document_type(doc_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/document-types/", response_model=List[DocumentType])
def get_document_types(db: Session = Depends(get_db)):
    service = MetadataService(db)
    return service.get_all_document_types()

@router.get("/document-types/{type_id}", response_model=DocumentType)
def get_document_type(type_id: int, db: Session = Depends(get_db)):
    service = MetadataService(db)
    doc_type = service.get_document_type(type_id)
    if not doc_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    return doc_type

@router.put("/document-types/{type_id}/fields", response_model=DocumentType)
def update_document_type_fields(
    type_id: int,
    fields_update: MetadataAssociationUpdate,
    db: Session = Depends(get_db)
):
    """Update metadata fields associated with a document type"""
    service = MetadataService(db)
    try:
        return service.update_document_type_fields(type_id, fields_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))