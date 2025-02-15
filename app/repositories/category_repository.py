"""
Path: app/repositories/category_repository.py
Description: Repository for category operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.category import Category, category_hierarchy

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, name: str, description: Optional[str] = None, parent_ids: Optional[List[int]] = None) -> Category:
        """Create a new category with optional parent categories"""
        category = Category(name=name, description=description)
        self.db.add(category)
        self.db.flush()  # Get ID without committing

        if parent_ids:
            for parent_id in parent_ids:
                parent = self.get_category(parent_id)
                if parent:
                    parent.children.append(category)

        self.db.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).all()

    def get_root_categories(self) -> List[Category]:
        """Get categories that have no parents"""
        subq = self.db.query(category_hierarchy.c.child_id).distinct()
        return self.db.query(Category).filter(Category.id.notin_(subq)).all()

    def get_category_tree(self, category_id: Optional[int] = None) -> List[Category]:
        """Get the category tree starting from the given category or all root categories"""
        if category_id:
            root = self.get_category(category_id)
            return [root] if root else []
        return self.get_root_categories()

    def update_category(self, category_id: int, name: Optional[str] = None, 
                       description: Optional[str] = None, parent_ids: Optional[List[int]] = None) -> Optional[Category]:
        """Update a category's details and parent relationships"""
        category = self.get_category(category_id)
        if not category:
            return None

        if name:
            category.name = name
        if description is not None:
            category.description = description

        if parent_ids is not None:
            # Clear existing parents
            category.parents.clear()
            # Add new parents
            for parent_id in parent_ids:
                parent = self.get_category(parent_id)
                if parent:
                    parent.children.append(category)

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        category = self.get_category(category_id)
        if category:
            # Clear relationships
            category.parents.clear()
            category.children.clear()
            self.db.delete(category)
            self.db.commit()
            return True
        return False