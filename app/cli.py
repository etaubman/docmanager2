"""
CLI interface for the Document Manager application.
Provides command-line access to core document management functionality.
"""

import click
from typing import Optional
import io
from fastapi import UploadFile
from app.services.document_service import DocumentService
from app.services.category_service import CategoryService
from app.database import SessionLocal
from app.schemas.category import CategoryCreate
from app.storage.implementations.local_storage import LocalFileStorage
import os
import asyncio

def get_db():
    # Return a DB session without closing immediately.
    return SessionLocal()

class ClickUploadFile(UploadFile):
    """Wrapper to make file objects compatible with FastAPI's UploadFile"""
    @classmethod
    def from_path(cls, path: str):
        filename = os.path.basename(path)
        file_obj = open(path, 'rb')
        return cls(file=file_obj, filename=filename)

@click.group()
def cli():
    """Document Manager CLI - Manage your documents from the command line"""
    pass

@cli.group()
def documents():
    """Manage documents"""
    pass

@documents.command()
@click.argument('filepath', type=click.Path(exists=True))
@click.option('--category', '-c', help='Category name for the document')
def upload(filepath: str, category: Optional[str]):
    """Upload a new document"""
    db = get_db()
    storage = LocalFileStorage()
    service = DocumentService(db=db, storage=storage)
    upload_file = ClickUploadFile.from_path(filepath)
    filename = os.path.basename(filepath)
    try:
        if category:
            from app.models.category import Category
            cat = db.query(Category).filter(Category.name == category).first()
            if not cat:
                click.echo(f"Category '{category}' not found")
                return
            metadata_values = {'category': category} if category else None
            doc = asyncio.run(service.create_document(
                file=upload_file,
                title=filename,
                metadata_values=metadata_values
            ))
        else:
            doc = asyncio.run(service.create_document(
                file=upload_file,
                title=filename
            ))
        click.echo(f"Document uploaded successfully. ID: {doc.id}")
    finally:
        upload_file.file.close()
        db.close()

@documents.command()
@click.argument('document_id', type=int)
def delete(document_id: int):
    """Delete a document by ID"""
    db = get_db()
    storage = LocalFileStorage()
    try:
        service = DocumentService(db=db, storage=storage)
        service.delete_document(document_id)
        click.echo(f"Document {document_id} deleted successfully")
    finally:
        db.close()

@documents.command()
def list():
    """List all documents"""
    db = get_db()
    storage = LocalFileStorage()
    try:
        service = DocumentService(db=db, storage=storage)
        docs = service.get_documents()
        for doc in docs:
            click.echo(f"ID: {doc.id} | Name: {doc.file_name or doc.title}")
    finally:
        db.close()

@cli.group()
def categories():
    """Manage categories"""
    pass

@categories.command()
@click.argument('name')
def create(name: str):
    """Create a new category"""
    db = get_db()
    try:
        service = CategoryService(db)
        category_data = CategoryCreate(name=name)
        category_obj = service.create_category(category_data)
        click.echo(f"Category '{category_obj.name}' created successfully")
    finally:
        db.close()

@categories.command()
def list():
    """List all categories"""
    db = get_db()
    try:
        service = CategoryService(db)
        categories = service.get_all_categories()
        for category in categories:
            click.echo(f"ID: {category.id} | Name: {category.name}")
    finally:
        db.close()

if __name__ == '__main__':
    cli()