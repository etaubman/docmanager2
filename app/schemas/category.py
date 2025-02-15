"""
Path: app/schemas/category.py
Description: Pydantic schemas for category data validation and serialization
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    parent_ids: Optional[List[int]] = None

class CategoryUpdate(CategoryBase):
    parent_ids: Optional[List[int]] = None

class Category(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CategoryRef(Category):
    """A simplified category reference to avoid recursion"""
    children: List[int] = []  # Just IDs of children
    parents: List[int] = []   # Just IDs of parents
    model_config = ConfigDict(from_attributes=True)

class CategoryTree(Category):
    """Full category tree with nested relationships"""
    children: List["CategoryTree"] = []
    model_config = ConfigDict(from_attributes=True)

# Required for recursive type reference
CategoryTree.model_rebuild()