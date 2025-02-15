"""
Path: app/models/document.py
Description: Document model definition using SQLAlchemy ORM
Purpose: Defines the database schema for documents
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class Document(Base):
    """
    Document model representing a document in the system
    
    Attributes:
        id (int): Primary key
        title (str): Document title
        content (str): Document content
        file_path (str): Path to the stored file
        file_name (str): Original filename
        file_size (int): Size of the file in bytes
        created_at (datetime): Document creation timestamp
        updated_at (datetime): Document last update timestamp
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String(512), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())