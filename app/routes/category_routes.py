"""
Path: app/routes/category_routes.py
Description: API routes for category operations
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, Category, CategoryTree

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.post("", response_model=Category)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category"""
    service = CategoryService(db)
    try:
        return service.create_category(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[Category])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    service = CategoryService(db)
    return service.get_all_categories()

@router.get("/tree", response_model=List[CategoryTree])
def get_category_tree(
    root_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Get category tree starting from root_id or all root categories"""
    service = CategoryService(db)
    return service.get_category_tree(root_id)

@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Get a category by ID"""
    service = CategoryService(db)
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category"""
    service = CategoryService(db)
    updated = service.update_category(category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """Delete a category"""
    service = CategoryService(db)
    if not service.delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}