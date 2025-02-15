import pytest
from fastapi.testclient import TestClient
from app.models.metadata import MetadataField, DocumentType, MetadataType

def test_create_metadata_field(client):
    """Test metadata field creation endpoint"""
    field_data = {
        "name": "Test Field",
        "description": "Test description",
        "field_type": "text",
        "is_multi_valued": False
    }
    response = client.post("/api/metadata-fields/", json=field_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Field"
    assert response.json()["field_type"] == "text"

def test_get_metadata_fields(client):
    """Test get all metadata fields endpoint"""
    # First create a field
    field_data = {
        "name": "Test Field",
        "description": "Test description",
        "field_type": "text"
    }
    client.post("/api/metadata-fields/", json=field_data)
    
    # Then get all fields
    response = client.get("/api/metadata-fields/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_metadata_field(client):
    """Test get single metadata field endpoint"""
    # First create a field
    field_data = {
        "name": "Test Field",
        "description": "Test description",
        "field_type": "text"
    }
    create_response = client.post("/api/metadata-fields/", json=field_data)
    field_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/metadata-fields/{field_id}")
    assert response.status_code == 200
    assert response.json()["id"] == field_id
    assert response.json()["name"] == "Test Field"

def test_create_document_type(client):
    """Test document type creation endpoint"""
    # First create a metadata field
    field_data = {
        "name": "Test Field",
        "description": "Test description",
        "field_type": "text"
    }
    field_response = client.post("/api/metadata-fields/", json=field_data)
    field_id = field_response.json()["id"]
    
    # Then create a document type with this field
    type_data = {
        "name": "Test Type",
        "description": "Test description",
        "metadata_fields": [
            {
                "metadata_field_id": field_id,
                "is_required": True
            }
        ]
    }
    response = client.post("/api/document-types/", json=type_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Type"
    assert len(response.json()["metadata_fields"]) == 1
    assert response.json()["metadata_fields"][0]["id"] == field_id

def test_get_document_types(client):
    """Test get all document types endpoint"""
    # First create a document type
    field_data = {
        "name": "Test Field",
        "field_type": "text"
    }
    field_response = client.post("/api/metadata-fields/", json=field_data)
    field_id = field_response.json()["id"]
    
    type_data = {
        "name": "Test Type",
        "description": "Test description",
        "metadata_fields": [{"metadata_field_id": field_id, "is_required": True}]
    }
    client.post("/api/document-types/", json=type_data)
    
    # Then get all types
    response = client.get("/api/document-types/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_get_document_type(client):
    """Test get single document type endpoint"""
    # First create a document type
    field_data = {
        "name": "Test Field",
        "field_type": "text"
    }
    field_response = client.post("/api/metadata-fields/", json=field_data)
    field_id = field_response.json()["id"]
    
    type_data = {
        "name": "Test Type",
        "description": "Test description",
        "metadata_fields": [{"metadata_field_id": field_id, "is_required": True}]
    }
    create_response = client.post("/api/document-types/", json=type_data)
    type_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/api/document-types/{type_id}")
    assert response.status_code == 200
    assert response.json()["id"] == type_id
    assert response.json()["name"] == "Test Type"
    assert len(response.json()["metadata_fields"]) == 1

def test_update_document_type_fields(client):
    """Test updating document type fields endpoint"""
    # First create necessary metadata fields
    field1_data = {
        "name": "Field 1",
        "field_type": "text"
    }
    field2_data = {
        "name": "Field 2",
        "field_type": "integer"
    }
    field1_response = client.post("/api/metadata-fields/", json=field1_data)
    field2_response = client.post("/api/metadata-fields/", json=field2_data)
    field1_id = field1_response.json()["id"]
    field2_id = field2_response.json()["id"]
    
    # Create a document type with field1
    type_data = {
        "name": "Test Type",
        "description": "Test description",
        "metadata_fields": [{"metadata_field_id": field1_id, "is_required": True}]
    }
    create_response = client.post("/api/document-types/", json=type_data)
    type_id = create_response.json()["id"]
    
    # Update fields to include field2 and make field1 optional
    update_data = {
        "field_associations": [
            {"metadata_field_id": field1_id, "is_required": False},
            {"metadata_field_id": field2_id, "is_required": True}
        ]
    }
    response = client.put(f"/api/document-types/{type_id}/fields", json=update_data)
    assert response.status_code == 200
    assert len(response.json()["metadata_fields"]) == 2
    
    # Get the type to verify changes
    get_response = client.get(f"/api/document-types/{type_id}")
    fields = get_response.json()["metadata_fields"]
    assert len(fields) == 2
    field1 = next(f for f in fields if f["id"] == field1_id)
    field2 = next(f for f in fields if f["id"] == field2_id)
    assert field1["name"] == "Field 1"
    assert field2["name"] == "Field 2"