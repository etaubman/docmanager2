"""
Path: tests/test_category_routes.py
Description: Tests for category API endpoints
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.database import Base, get_db
from app.main import app
from app.database_seeder import create_categories

def test_create_category(test_db: Session, client: TestClient):
    """Test creating a new category"""
    response = client.post(
        "/api/categories/",
        json={
            "name": "Test Category",
            "description": "Test Description",
            "parent_ids": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "Test Description"

def test_get_categories(test_db: Session, client: TestClient):
    """Test getting all categories"""
    # Seed some categories
    create_categories(test_db)
    
    response = client.get("/api/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(isinstance(cat["name"], str) for cat in data)

def test_get_category_tree(test_db: Session, client: TestClient):
    """Test getting category tree"""
    # Seed categories
    categories = create_categories(test_db)
    root_id = categories[0].id
    
    response = client.get(f"/api/categories/tree?root_id={root_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    root = data[0]
    assert len(root["children"]) > 0

def test_update_category(test_db: Session, client: TestClient):
    """Test updating a category"""
    # Create a test category
    create_response = client.post(
        "/api/categories/",
        json={
            "name": "Update Test",
            "description": "Original Description",
            "parent_ids": []
        }
    )
    category_id = create_response.json()["id"]
    
    # Update it
    update_response = client.put(
        f"/api/categories/{category_id}",
        json={
            "name": "Updated Name",
            "description": "Updated Description",
            "parent_ids": []
        }
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Description"

def test_delete_category(test_db: Session, client: TestClient):
    """Test deleting a category"""
    # Create a test category
    create_response = client.post(
        "/api/categories/",
        json={
            "name": "To Delete",
            "description": "Will be deleted",
            "parent_ids": []
        }
    )
    category_id = create_response.json()["id"]
    
    # Delete it
    delete_response = client.delete(f"/api/categories/{category_id}")
    assert delete_response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/api/categories/{category_id}")
    assert get_response.status_code == 404

def test_category_hierarchy(test_db: Session, client: TestClient):
    """Test category hierarchical relationships"""
    # Create parent category
    parent_response = client.post(
        "/api/categories/",
        json={
            "name": "Parent Category",
            "description": "Parent Description",
            "parent_ids": []
        }
    )
    parent_id = parent_response.json()["id"]
    
    # Create child category
    child_response = client.post(
        "/api/categories/",
        json={
            "name": "Child Category",
            "description": "Child Description",
            "parent_ids": [parent_id]
        }
    )
    assert child_response.status_code == 200
    
    # Verify hierarchy in tree
    tree_response = client.get(f"/api/categories/tree?root_id={parent_id}")
    assert tree_response.status_code == 200
    data = tree_response.json()
    assert len(data) == 1
    parent = data[0]
    assert len(parent["children"]) == 1
    assert parent["children"][0]["name"] == "Child Category"