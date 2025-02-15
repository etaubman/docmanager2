# Document Manager Application Structure

## Overview
The Document Manager is a FastAPI-based web application that follows a clean layered architecture pattern for handling document management operations. This document explains how requests flow through the application's various layers.

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────┐
│                    Client (Browser)                      │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Requests
                         ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Routes (document_routes.py)           │    │
│  │         Handles HTTP endpoints and routing       │    │
│  └───────────────────────┬─────────────────────────┘    │
│                          │                              │
│  ┌───────────────────────▼─────────────────────────┐    │
│  │         Services (document_service.py)           │    │
│  │    Business Logic & Operation Coordination       │    │
│  └───────────┬──────────────────────────┬──────────┘    │
│              │                          │               │
│  ┌───────────▼──────────┐    ┌─────────▼────────────┐   │
│  │      Repository      │    │    Storage Layer      │   │
│  │(document_repository) │    │    (local_storage)    │   │
│  │   Database Access    │    │    File Operations    │   │
│  └───────────┬──────────┘    └─────────┬────────────┘   │
│              │                          │               │
│  ┌───────────▼──────────┐    ┌─────────▼────────────┐   │
│  │      Database        │    │     File System       │   │
│  │    (SQLite DB)      │    │  (Uploads Directory)  │   │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Architecture Layers

### 1. Presentation Layer (Routes)
- Located in `app/routes/document_routes.py`
- Handles HTTP endpoints and request/response formatting
- Defines REST API endpoints with OpenAPI documentation
- Routes include:
  - POST `/api/documents/` - Create document
  - POST `/api/documents/upload` - Upload document with file
  - GET `/api/documents/` - List all documents
  - GET `/api/documents/{id}` - Get specific document
  - PUT `/api/documents/{id}` - Update document
  - DELETE `/api/documents/{id}` - Delete document
  - GET `/api/documents/download/{id}` - Download document file

### 2. Service Layer
- Located in `app/services/document_service.py`
- Implements business logic
- Coordinates between routes and repository
- Handles:
  - Document validation
  - File storage coordination
  - Error handling and HTTP exceptions
  - Business rule enforcement

### 3. Repository Layer
- Located in `app/repositories/document_repository.py`
- Manages database operations
- Handles:
  - CRUD operations for documents
  - Database session management
  - Query execution

### 4. Storage Layer
- Interface: `app/storage/storage_interface.py`
- Implementation: `app/storage/implementations/local_storage.py`
- Handles file operations:
  - File saving
  - File retrieval
  - File deletion
- Abstracts storage backend (currently local filesystem)

### 5. Data Layer
- Models: `app/models/document.py`
- Schemas: `app/schemas/document.py`
- Database: `app/database.py`
- Handles:
  - Database schema definitions
  - Data validation
  - ORM models
  - Pydantic schemas for API contracts

## Request Flow Example

Here's how a typical request flows through the application:

1. **Client Request** → HTTP request arrives at a route endpoint

2. **Route Handler**:
   - Validates request data
   - Converts request data to Pydantic models
   - Calls appropriate service method

3. **Service Layer**:
   - Applies business logic
   - Coordinates with storage for file operations
   - Calls repository methods for database operations
   - Handles errors and exceptions

4. **Repository Layer**:
   - Executes database operations
   - Returns database models

5. **Response**:
   - Data is converted back to Pydantic models
   - Sent back to client as JSON

## Frontend Integration

The application includes a web frontend (`static/` directory) that communicates with the backend API:
- `index.html` - Main application page
- `script.js` - Frontend logic and API calls
- `styles.css` - Application styling