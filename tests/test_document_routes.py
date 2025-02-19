import pytest
from fastapi.testclient import TestClient
import json
import os
from app.models.document import Document

def test_create_document(client, test_uploads_dir):
    """Test document creation endpoint"""
    with open(os.path.join(test_uploads_dir, "test.txt"), "wb") as f:
        f.write(b"test content")
    
    with open(os.path.join(test_uploads_dir, "test.txt"), "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": "Test Document"}
        response = client.post("/api/documents/", data=data, files=files)
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Document"
    assert response.json()["file_name"] == "test.txt"

def test_get_documents(client):
    """Test get all documents endpoint"""
    response = client.get("/api/documents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_document(client, test_uploads_dir):
    """Test get single document endpoint"""
    # First create a document
    with open(os.path.join(test_uploads_dir, "test.txt"), "wb") as f:
        f.write(b"test content")
    
    with open(os.path.join(test_uploads_dir, "test.txt"), "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": "Test Document"}
        create_response = client.post("/api/documents/", data=data, files=files)
    
    document_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/api/documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["id"] == document_id
    assert response.json()["title"] == "Test Document"

def test_update_document(client, test_uploads_dir):
    """Test document update endpoint"""
    # First create a document
    with open(os.path.join(test_uploads_dir, "test.txt"), "wb") as f:
        f.write(b"test content")
    
    with open(os.path.join(test_uploads_dir, "test.txt"), "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": "Original Title"}
        create_response = client.post("/api/documents/", data=data, files=files)
    
    document_id = create_response.json()["id"]
    
    # Then update it
    update_data = {
        "title": "Updated Title",
        "content": "Updated content"
    }
    response = client.put(
        f"/api/documents/{document_id}",
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Updated content"

def test_delete_document(client, test_uploads_dir):
    """Test document deletion endpoint"""
    # First create a document
    with open(os.path.join(test_uploads_dir, "test.txt"), "wb") as f:
        f.write(b"test content")
    
    with open(os.path.join(test_uploads_dir, "test.txt"), "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": "Test Document"}
        create_response = client.post("/api/documents/", data=data, files=files)
    
    document_id = create_response.json()["id"]
    
    # Then delete it
    response = client.delete(f"/api/documents/{document_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/documents/{document_id}")
    assert get_response.status_code == 404

def test_download_document(client, test_uploads_dir):
    """Test document download endpoint"""
    content = b"test content"
    # First create a document
    with open(os.path.join(test_uploads_dir, "test.txt"), "wb") as f:
        f.write(content)
    
    with open(os.path.join(test_uploads_dir, "test.txt"), "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": "Test Document"}
        create_response = client.post("/api/documents/", data=data, files=files)
    
    document_id = create_response.json()["id"]
    
    # Then download it
    response = client.get(f"/api/documents/download/{document_id}")
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="test.txt"'
    assert response.content == content

def test_document_versioning(client, test_uploads_dir):
    """Test document versioning on update and retrieval of versions"""
    # Create a document
    with open(os.path.join(test_uploads_dir, "test.txt"), "wb") as f:
        f.write(b"original content")
    with open(os.path.join(test_uploads_dir, "test.txt"), "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": "Versioned Document"}
        # Updated endpoint from "/documents/" to "/api/documents/"
        create_resp = client.post("/api/documents/", data=data, files=files)
    assert create_resp.status_code == 201
    doc_id = create_resp.json()["id"]

    # Update the document twice to generate versions
    update_data1 = {"title": "Updated Title 1", "content": "Updated content 1"}
    # Updated endpoint from "/documents/{doc_id}" to "/api/documents/{doc_id}"
    resp1 = client.put(f"/api/documents/{doc_id}", json=update_data1)
    assert resp1.status_code == 200

    update_data2 = {"title": "Updated Title 2", "content": "Updated content 2"}
    resp2 = client.put(f"/api/documents/{doc_id}", json=update_data2)
    assert resp2.status_code == 200

    # Retrieve all versions
    versions_resp = client.get(f"/api/documents/{doc_id}/versions")
    assert versions_resp.status_code == 200
    versions = versions_resp.json()
    # Expecting 2 versions
    assert len(versions) == 2
    assert versions[0]["version_number"] == 1
    assert versions[1]["version_number"] == 2

    # Retrieve the latest version
    latest_resp = client.get(f"/api/documents/{doc_id}/versions/latest")
    assert latest_resp.status_code == 200
    latest = latest_resp.json()
    assert latest["version_number"] == 2

def create_document_helper(client, test_uploads_dir, title, file_content, metadata):
    file_path = os.path.join(test_uploads_dir, "test.txt")
    with open(file_path, "wb") as f:
        f.write(file_content)
    with open(file_path, "rb") as f:
        files = {"file": ("test.txt", f, "text/plain")}
        data = {"title": title, "metadata_values": json.dumps(metadata)}
        response = client.post("/api/documents/", data=data, files=files)
        return response

def test_search_documents(client, test_uploads_dir):
    """Test searching documents by title and metadata."""
    # Create two documents with different metadata and titles
    resp1 = create_document_helper(client, test_uploads_dir, "Report Q1", b"content1", {"category": "report", "author": "Alice"})
    assert resp1.status_code == 201
    resp2 = create_document_helper(client, test_uploads_dir, "Invoice 2022", b"content2", {"category": "invoice", "author": "Bob"})
    assert resp2.status_code == 201

    # Search by metadata category: report
    search_params = {
        "metadata": json.dumps({"category": "report"})
    }
    response = client.get("/api/documents/search", params=search_params)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Report Q1"

    # Search by title substring "Invoice"
    response = client.get("/api/documents/search", params={"title": "Invoice"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Invoice 2022"

    # Test paginated results by setting limit=1
    response = client.get("/api/documents/search", params={"limit": 1})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1

def test_create_document_without_file(client):
    """Test creating a document without providing a file"""
    data = {"title": "No File Document"}
    response = client.post("/api/documents/", data=data)
    # Expecting a validation error if file upload is required
    assert response.status_code in (400, 422)

def test_update_nonexistent_document(client):
    """Test updating a non-existent document"""
    update_data = {"title": "Non-existent", "content": "Nothing"}
    response = client.put("/api/documents/99999", json=update_data)
    # Expecting not found
    assert response.status_code == 404

def test_delete_nonexistent_document(client):
    """Test deleting a non-existent document"""
    response = client.delete("/api/documents/99999")
    # Expecting not found
    assert response.status_code == 404

def test_download_nonexistent_document(client):
    """Test downloading a non-existent document"""
    response = client.get("/api/documents/download/99999")
    # Expecting not found
    assert response.status_code == 404

def test_search_documents_no_match(client):
    """Test searching with parameters that yield no results"""
    response = client.get("/api/documents/search", params={"title": "NoSuchTitle", "limit": 1})
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) == 0