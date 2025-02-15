"""
Path: app/routes/document_routes.py
Description: API routes for document management
Purpose: Defines all HTTP endpoints for document operations with OpenAPI documentation
"""

from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentFile
from app.services.document_service import DocumentService
from app.storage.implementations.local_storage import LocalFileStorage

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Document not found"}}
)

document_service = DocumentService()
storage = LocalFileStorage()

@router.post("/", 
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    description="Creates a new document with the provided title and content"
)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new document with the following information:
    
    - **title**: Required title of the document
    - **content**: Required content of the document
    """
    return document_service.create_document(db, document)

@router.post("/upload",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document with file",
    description="Creates a new document with an attached file"
)
async def upload_document(
    file: UploadFile = File(...),
    document: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document with a file:
    
    - **file**: Required file to upload
    - **document**: JSON string containing title and content
    """
    doc_data = json.loads(document)
    return await document_service.create_document_with_file(db, DocumentFile(**doc_data), file, storage)

@router.get("/download/{document_id}",
    summary="Download document file",
    description="Downloads the file associated with a document"
)
async def download_document_file(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Download a document's file:
    
    - **document_id**: Required ID of the document
    """
    doc = document_service.get_document(db, document_id)
    if not doc.file_path:
        raise HTTPException(status_code=404, detail="No file associated with this document")
    
    return StreamingResponse(
        storage.get_file(doc.file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'}
    )

@router.get("/", 
    response_model=List[Document],
    summary="Get all documents",
    description="Retrieves all documents with pagination support"
)
def get_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all documents with pagination:
    
    - **skip**: Number of documents to skip (default: 0)
    - **limit**: Maximum number of documents to return (default: 100)
    """
    return document_service.get_documents(db, skip, limit)

@router.get("/{document_id}",
    response_model=Document,
    summary="Get a specific document",
    description="Retrieves a document by its ID"
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific document by its ID:
    
    - **document_id**: Required ID of the document to retrieve
    """
    return document_service.get_document(db, document_id)

@router.put("/{document_id}",
    response_model=Document,
    summary="Update a document",
    description="Updates an existing document's title and/or content"
)
def update_document(
    document_id: int,
    document: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a document with the following information:
    
    - **document_id**: Required ID of the document to update
    - **title**: New title of the document
    - **content**: New content of the document
    """
    return document_service.update_document(db, document_id, document)

@router.delete("/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
    description="Deletes a document by its ID"
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document by its ID:
    
    - **document_id**: Required ID of the document to delete
    """
    document_service.delete_document(db, document_id)