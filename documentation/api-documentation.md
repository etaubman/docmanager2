# Document Manager API Documentation

## Overview

The Document Manager provides two interfaces for managing documents:
1. A REST API (this document)
2. A Command Line Interface (CLI)

## CLI Integration

The CLI provides a complementary interface to the API, using the same underlying services and repositories. This ensures consistency between both interfaces. For CLI usage, see the README.md file.

## API Endpoints

### Documents API

## Base URL
All API endpoints are prefixed with `/api`

## Authentication
Currently implemented as an open API. Authentication can be added through FastAPI's security dependencies.

## Documents API

### Create Document
- **POST** `/documents/`
- **Description**: Create a new document entry without file upload
```json
{
    "title": "string",
    "document_type_id": "integer",
    "metadata": {
        "field_name": "value"
    }
}
```

### Upload Document
- **POST** `/documents/upload`
- **Description**: Upload a document with file and metadata
- **Content-Type**: multipart/form-data
- **Fields**:
  - file: binary
  - title: string
  - document_type_id: integer
  - metadata: JSON string

### List Documents
- **GET** `/documents/`
- **Parameters**:
  - page: integer (optional)
  - limit: integer (optional)
  - search: string (optional)
  - document_type: integer (optional)

### Get Document
- **GET** `/documents/{id}`
- **Description**: Retrieve document metadata and versions

### Update Document
- **PUT** `/documents/{id}`
- **Description**: Update document metadata or upload new version

### Delete Document
- **DELETE** `/documents/{id}`
- **Description**: Delete document and all versions

## Metadata Fields API

### Create Metadata Field
- **POST** `/metadata/fields/`
```json
{
    "name": "string",
    "description": "string",
    "field_type": "string",
    "enum_values": ["string"],
    "is_multi_valued": "boolean"
}
```

### List Metadata Fields
- **GET** `/metadata/fields/`

### Update Metadata Field
- **PUT** `/metadata/fields/{id}`

### Delete Metadata Field
- **DELETE** `/metadata/fields/{id}`

## Document Types API

### Create Document Type
- **POST** `/doctypes/`
```json
{
    "name": "string",
    "description": "string",
    "metadata_fields": ["integer"]
}
```

### List Document Types
- **GET** `/doctypes/`

### Update Document Type
- **PUT** `/doctypes/{id}`

### Delete Document Type
- **DELETE** `/doctypes/{id}`

## Error Responses
All endpoints follow a consistent error response format:
```json
{
    "detail": "Error message",
    "code": "ERROR_CODE",
    "status": 400
}