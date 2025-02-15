"""
Category model for document classification
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for self-referential relationship
category_hierarchy = Table(
    'category_hierarchy',
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column('child_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

# Association table for document types and categories
document_type_categories = Table(
    'document_type_categories',
    Base.metadata,
    Column('document_type_id', Integer, ForeignKey('document_types.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Category(Base):
    """Category model for hierarchical document classification"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)

    # Self-referential relationship for hierarchy
    children = relationship(
        "Category",
        secondary=category_hierarchy,
        primaryjoin=id==category_hierarchy.c.parent_id,
        secondaryjoin=id==category_hierarchy.c.child_id,
        backref="parents"
    )

    # Relationship with document types
    document_types = relationship(
        "DocumentType",
        secondary=document_type_categories,
        back_populates="categories"
    )

    def __repr__(self):
        return f"<Category {self.name}>"