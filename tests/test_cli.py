"""Tests for the CLI interface"""
import pytest
from click.testing import CliRunner
from app.cli import cli
import os
import tempfile
from app.database import SessionLocal
from app.services.document_service import DocumentService
from app.services.category_service import CategoryService
from app.models.category import Category
from app.storage.implementations.local_storage import LocalFileStorage

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def db():
    db = SessionLocal()
    try:
        # Clear existing categories before each test
        db.query(Category).delete()
        db.commit()
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_file():
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as f:
        f.write('test content')
        filepath = f.name
    yield filepath
    os.unlink(filepath)

def test_list_documents(runner, db):
    result = runner.invoke(cli, ['documents', 'list'])
    assert result.exit_code == 0

def test_list_categories(runner, db):
    result = runner.invoke(cli, ['categories', 'list'])
    assert result.exit_code == 0

def test_create_category(runner, db):
    result = runner.invoke(cli, ['categories', 'create', 'TestCategory'])
    assert result.exit_code == 0
    assert 'created successfully' in result.output

    # Verify category was created
    service = CategoryService(db)
    categories = service.get_all_categories()
    assert any(c.name == 'TestCategory' for c in categories)

def test_upload_document(runner, db, sample_file):
    result = runner.invoke(cli, ['documents', 'upload', sample_file])
    assert result.exit_code == 0
    assert 'uploaded successfully' in result.output

def test_upload_document_with_category(runner, db, sample_file):
    # Create category first
    cat_result = runner.invoke(cli, ['categories', 'create', 'TestCategory'])
    assert cat_result.exit_code == 0

    # Upload document with category
    result = runner.invoke(cli, ['documents', 'upload', sample_file, '-c', 'TestCategory'])
    assert result.exit_code == 0
    assert 'uploaded successfully' in result.output

    # Verify document was uploaded with correct category
    storage = LocalFileStorage()
    service = DocumentService(db=db, storage=storage)
    docs = service.get_documents()
    assert any(d.metadata_values.get('category') == 'TestCategory' for d in docs)