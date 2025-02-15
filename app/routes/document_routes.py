"""
Path: app/routes/document_routes.py
Description: API routes for document management
Purpose: Defines all HTTP endpoints for document operations with OpenAPI documentation
"""

from fastapi import APIRouter, Depends, status, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
import json

from app.schemas.document import Document, DocumentCreate, DocumentUpdate, DocumentFile, DocumentResponse, DocumentVersionResponse
from app.services.document_service import DocumentService
from app.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={404: {"description": "Document not found"}}
)

@router.post("/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
    description="Creates a new document with the provided title and content"
)
async def create_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type_id: Optional[int] = Form(None),
    metadata_values: Optional[str] = Form(None),
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Create a new document with the following information:
    
    - **file**: Required file to upload
    - **title**: Required title of the document
    - **document_type_id**: Optional ID of the document type
    - **metadata_values**: Optional JSON string containing metadata key-value pairs
    
    Returns the created DocumentResponse object.
    """
    logger.info(f"Received request to create document: {title}")
    try:
        metadata_dict = json.loads(metadata_values) if metadata_values else {}
        result = await document_service.create_document(
            file=file,
            title=title,
            document_type_id=document_type_id,
            metadata_values=metadata_dict
        )
        logger.info(f"Successfully processed create document request for ID: {result.id}")
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    except ValueError as e:
        logger.error(f"Error processing create document request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{document_id}/metadata",
    response_model=DocumentResponse,
    summary="Update document metadata",
    description="Updates the metadata of an existing document"
)
async def update_document_metadata(
    document_id: int,
    document_type_id: Optional[int] = Form(None),
    metadata_values: str = Form(...),
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Update a document's metadata with the following information:
    
    - **document_id**: Required ID of the document to update
    - **document_type_id**: Optional ID of the document type
    - **metadata_values**: Required JSON string containing metadata key-value pairs
    
    Returns the updated DocumentResponse object.
    """
    logger.info(f"Received request to update metadata for document ID: {document_id}")
    try:
        metadata_dict = json.loads(metadata_values)
        result = document_service.update_document_metadata(
            document_id=document_id,
            document_type_id=document_type_id,
            metadata_values=metadata_dict
        )
        logger.info(f"Successfully updated metadata for document ID: {document_id}")
        return result
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    except ValueError as e:
        logger.error(f"Error updating metadata for document {document_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/upload",
    response_model=Document,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a document with file",
    description="Creates a new document with an attached file"
)
async def upload_document(
    file: UploadFile = File(...),
    document: str = Form(...),
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Upload a document with a file:
    
    - **file**: Required file to upload
    - **document**: JSON string containing title and content
    
    Returns the created Document object.
    """
    logger.info(f"Received document upload request with file: {file.filename}")
    try:
        doc_data = json.loads(document)
        result = await document_service.create_document_with_file(DocumentFile(**doc_data), file)
        logger.info(f"Successfully processed document upload for ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error processing document upload: {str(e)}")
        raise

# Moved search endpoint above routes using "/{document_id}" to avoid path conflicts.
@router.get("/search",
    response_model=List[Document],
    summary="Search documents",
    description="Search documents by filename, title, and metadata with optional pagination"
)
def search_documents(
    filename: Optional[str] = Query(None, description="Filter by file name"),
    title: Optional[str] = Query(None, description="Filter by title"),
    metadata: Optional[str] = Query(None, description="JSON string to filter metadata"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    document_service: DocumentService = Depends(DocumentService)
):
    metadata_filter = None
    if metadata:
        try:
            metadata_filter = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON format")
    return document_service.search_documents(filename, title, metadata_filter, skip, limit)

@router.get("/download/{document_id}",
    summary="Download document file",
    description="Downloads the file associated with a document"
)
async def download_document_file(
    document_id: int,
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Download a document's file:
    
    - **document_id**: Required ID of the document
    
    Returns a StreamingResponse to download the file.
    """
    logger.info(f"Received download request for document ID: {document_id}")
    try:
        doc = document_service.get_document(document_id)
        if not doc.file_path:
            logger.warning(f"No file associated with document ID: {document_id}")
            raise HTTPException(status_code=404, detail="No file associated with this document")
        
        logger.info(f"Streaming file for document ID: {document_id}")
        # Don't await the generator, pass it directly to StreamingResponse
        file_generator = document_service.get_file(doc.file_path)
        return StreamingResponse(
            file_generator,
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
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Retrieve all documents with pagination:
    
    - **skip**: Number of documents to skip (default: 0)
    - **limit**: Maximum number of documents to return (default: 100)
    
    Returns a list of Document objects.
    """
    logger.info(f"Received request to list documents (skip={skip}, limit={limit})")
    try:
        result = document_service.get_documents(skip=skip, limit=limit)
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
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Retrieve a specific document by its ID:
    
    - **document_id**: Required ID of the document to retrieve
    
    Returns the Document object if found, otherwise raises a 404 HTTPException.
    """
    logger.info(f"Received request to get document ID: {document_id}")
    try:
        result = document_service.get_document(document_id)
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
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Update a document with the following information:
    
    - **document_id**: Required ID of the document to update
    - **title**: New title of the document
    - **content**: New content of the document
    
    Returns the updated Document object.
    """
    logger.info(f"Received request to update document ID: {document_id}")
    try:
        result = document_service.update_document(document_id, document)
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
    document_service: DocumentService = Depends(DocumentService)
):
    """
    Delete a document by its ID:
    
    - **document_id**: Required ID of the document to delete
    
    Returns a 204 No Content status on successful deletion.
    """
    logger.info(f"Received request to delete document ID: {document_id}")
    try:
        document_service.delete_document(document_id)
        logger.info(f"Successfully deleted document ID: {document_id}")
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise

@router.get("/{document_id}/versions",
    response_model=List[DocumentVersionResponse],
    summary="Get document version history",
    description="Retrieves all versions (history) of a document"
)
def get_document_versions(
    document_id: int,
    document_service: DocumentService = Depends(DocumentService)
):
    versions = document_service.get_document_versions(document_id)
    return versions

@router.get("/{document_id}/versions/latest",
    response_model=DocumentVersionResponse,
    summary="Get latest document version",
    description="Retrieves just the latest archived version of a document"
)
def get_latest_document_version(
    document_id: int,
    document_service: DocumentService = Depends(DocumentService)
):
    latest_version = document_service.get_latest_document_version(document_id)
    return latest_version