"""
Path: app/routes/document_routes.py
Description: API routes for document management
Purpose: Defines all HTTP endpoints for document operations with OpenAPI documentation
"""

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentFile
from app.services.document_service import DocumentService
from app.storage.implementations.local_storage import LocalFileStorage
from app.logging_config import get_logger

logger = get_logger(__name__)

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
    logger.info(f"Received request to create document: {document.title}")
    try:
        result = document_service.create_document(db, document)
        logger.info(f"Successfully processed create document request for ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error processing create document request: {str(e)}")
        raise

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
    logger.info(f"Received document upload request with file: {file.filename}")
    try:
        doc_data = json.loads(document)
        result = await document_service.create_document_with_file(db, DocumentFile(**doc_data), file, storage)
        logger.info(f"Successfully processed document upload for ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error processing document upload: {str(e)}")
        raise

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
    logger.info(f"Received download request for document ID: {document_id}")
    try:
        doc = document_service.get_document(db, document_id)
        if not doc.file_path:
            logger.warning(f"No file associated with document ID: {document_id}")
            raise HTTPException(status_code=404, detail="No file associated with this document")
        
        logger.info(f"Streaming file for document ID: {document_id}")
        return StreamingResponse(
            storage.get_file(doc.file_path),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'}
        )
    except Exception as e:
        logger.error(f"Error processing download request for document {document_id}: {str(e)}")
        raise

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
    logger.info(f"Received request to list documents (skip={skip}, limit={limit})")
    try:
        result = document_service.get_documents(db, skip, limit)
        logger.info(f"Successfully retrieved {len(result)} documents")
        return result
    except Exception as e:
        logger.error(f"Error retrieving documents list: {str(e)}")
        raise

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
    logger.info(f"Received request to get document ID: {document_id}")
    try:
        result = document_service.get_document(db, document_id)
        logger.info(f"Successfully retrieved document ID: {document_id}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving document {document_id}: {str(e)}")
        raise

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
    logger.info(f"Received request to update document ID: {document_id}")
    try:
        result = document_service.update_document(db, document_id, document)
        logger.info(f"Successfully updated document ID: {document_id}")
        return result
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {str(e)}")
        raise

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
    logger.info(f"Received request to delete document ID: {document_id}")
    try:
        document_service.delete_document(db, document_id)
        logger.info(f"Successfully deleted document ID: {document_id}")
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise