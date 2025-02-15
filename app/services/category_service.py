"""
Path: app/services/category_service.py
Description: Service layer for category operations
"""

from typing import List, Optional
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category

def convert_to_tree(category: Category, seen=None) -> dict:
    """Convert a category to a tree structure without recursion issues"""
    if seen is None:
        seen = set()
    
    if category.id in seen:
        return None
    
    seen.add(category.id)
    
    return {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "children": [
            child_dict for child in category.children
            if (child_dict := convert_to_tree(child, seen.copy())) is not None
        ]
    }

class CategoryService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.repository = CategoryRepository(db)

    def create_category(self, category_data: CategoryCreate) -> Category:
        """Create a new category"""
        return self.repository.create_category(
            name=category_data.name,
            description=category_data.description,
            parent_ids=category_data.parent_ids
        )

    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        return self.repository.get_category(category_id)

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return self.repository.get_all_categories()

    def get_category_tree(self, category_id: Optional[int] = None) -> List[dict]:
        """Get category tree starting from given category or all root categories"""
        categories = self.repository.get_category_tree(category_id)
        return [
            tree for cat in categories
            if (tree := convert_to_tree(cat)) is not None
        ]

    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        return self.repository.update_category(
            category_id=category_id,
            name=category_data.name,
            description=category_data.description,
            parent_ids=category_data.parent_ids
        )

    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        return self.repository.delete_category(category_id)