"""
Test module for database seeder functionality
"""
import pytest
from sqlalchemy.orm import Session
from app.database_seeder import (
    create_metadata_fields,
    create_document_types,
    create_sample_documents,
    seed_database
)
from app.models.metadata import MetadataField, DocumentType
from app.models.document import Document
from app.models.document_version import DocumentVersion
from tests.conftest import override_get_db
from app.database import Base

@pytest.fixture(autouse=True)
def setup_db():
    """Create and drop tables for each test"""
    db = next(override_get_db())
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    yield db
    Base.metadata.drop_all(bind=db.get_bind())

def test_create_metadata_fields(setup_db):
    """Test metadata fields creation"""
    db = setup_db
    fields = create_metadata_fields(db)
    
    assert len(fields) == 5  # We create 5 default fields
    assert any(field.name == "department" for field in fields)
    assert any(field.name == "document_date" for field in fields)
    assert any(field.name == "confidential" for field in fields)
    assert any(field.name == "tags" for field in fields)
    assert any(field.name == "revision_number" for field in fields)

def test_create_document_types(setup_db):
    """Test document types creation with metadata field associations"""
    db = setup_db
    fields = create_metadata_fields(db)
    types = create_document_types(db, fields)
    
    assert len(types) == 3  # We create 3 document types
    
    # Test Contract type
    contract = next(t for t in types if t.name == "Contract")
    assert len(contract.metadata_fields) == 3
    assert any(field.name == "department" for field in contract.metadata_fields)
    assert any(field.name == "document_date" for field in contract.metadata_fields)
    assert any(field.name == "confidential" for field in contract.metadata_fields)
    
    # Test Report type
    report = next(t for t in types if t.name == "Report")
    assert len(report.metadata_fields) == 3
    assert any(field.name == "department" for field in report.metadata_fields)
    assert any(field.name == "document_date" for field in report.metadata_fields)
    assert any(field.name == "tags" for field in report.metadata_fields)

def test_create_sample_documents(setup_db):
    """Test sample documents creation with metadata and versions"""
    db = setup_db
    fields = create_metadata_fields(db)
    types = create_document_types(db, fields)
    
    num_docs = 10
    create_sample_documents(db, types, num_docs)
    
    # Check documents
    documents = db.query(Document).all()
    assert len(documents) == num_docs
    
    # Check document versions
    versions = db.query(DocumentVersion).all()
    assert len(versions) > num_docs  # Each document has 1-3 versions
    
    # Check a random document's metadata
    doc = documents[0]
    assert doc.metadata_values is not None
    assert doc.document_type_id is not None
    assert doc.title is not None
    assert doc.content is not None
    
    # Check document versions relationship
    assert len(doc.versions) > 0
    assert all(v.document_id == doc.id for v in doc.versions)

def test_seed_database(setup_db):
    """Test the main seeder function"""
    result = seed_database(num_documents=10, db=setup_db)
    
    assert result["metadata_fields"] == 5
    assert result["document_types"] == 3
    assert result["documents"] == 10